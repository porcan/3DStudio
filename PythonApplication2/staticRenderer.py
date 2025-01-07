import pathlib
import PIL.Image
import random
import math
import time
from utilities import *

class Vect: #class for a 3D vector
    def __init__(self, x: float or int, y: float or int, z: float or int):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self): #method to print the vector values
        return f"({self.x}, {self.y}, {self.z})"
        
    def __add__(self, add): #method for adding the vector to either a scalar or another vector
        if type(add) == Vect:
            return Vect(self.x + add.x, self.y + add.y, self.z + add.z)
        elif type(add) == int or type(add) == float:
            return Vect(self.x + add, self.y + add, self.z + add)
        
        return self

    def __sub__(self, sub): #method for subtracting a vector or scalar from the vector
        if type(sub) == Vect:
            return Vect(self.x - sub.x, self.y - sub.y, self.z - sub.z)
        elif type(sub) == int or type(sub) == float:
            return Vect(self.x - sub, self.y - sub, self.z - sub)
        return self

    def __mul__(self, mul):
        if type(mul) == int or type(mul) == float:
            return Vect(self.x * mul, self.y * mul, self.z * mul)
        
        if type(mul) == Vect:
            return Vect(self.x * mul.x, self.y * mul.y, self.z * mul.z)

        return self
    
    def __truediv__(self, div):
        if type(div) == int or type(div) == float:
            return Vect(self.x / div, self.y / div, self.z * div)
        
        if type(div) == Vect:
            return Vect(self.x / div.x, self.y / div.y, self.z / div.z)

        return self

    def dot(self, dotVect): #method for calculating the dot product of the vector with another vector
        if type(dotVect) == Vect:
            return (self.x * dotVect.x) + (self.y * dotVect.y) + (self.z * dotVect.z)

    def mag(self): #returns the magnitude of the vector
        return math.sqrt((self.x ** 2) + (self.y ** 2) + (self.z ** 2))

    def angle(self, angleVect): #calculates the angle between the vector and another vector
        if type(angleVect) == Vect:
            radians = math.acos(self.dot(angleVect) / (self.mag() * angleVect.mag()))
            return radians * (180 / math.pi)

    def cross(self, crossVect): #calculates the cross product between the vector and another vector
        if type(crossVect) == Vect:
            return Vect((self.y * crossVect.z - self.z * crossVect.y),
                        (self.z * crossVect.x - self.x * crossVect.z),
                        (self.x * crossVect.y - self.y * crossVect.x))
        
    def normalise(self): #returns a unit vector in the same direction as the original vector
        if self.mag() == 0:
            return self
        return Vect((self.x / self.mag()),
                    (self.y / self.mag()),
                    (self.z / self.mag()))
    
    def roundTuple(self):
        return(round(self.x), round(self.y), round(self.z))
    
class Sphere:
    def __init__(self, centre: Vect, radius, colour: Vect, emissColour: Vect, emission: float):
        self.centre = centre
        self.radius = radius
        self.colour = colour
        self.emission = emission
        self.emissColour = emissColour

class Triangle:
    def __init__(self, p1: Vect, p2: Vect, p3: Vect, colour):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.colour = colour
        
class HitInfo:
    def __init__(self, hit: bool, dist: float, hitPoint: Vect, normal: Vect, colour: Vect, emissColour: Vect, emission: float):
        self.hit = hit
        self.dist = dist
        self.hitPoint = hitPoint
        self.normal = normal
        self.colour = colour
        self.emissColour = emissColour
        self.emission = emission
    
class Ray:
    def __init__(self, origin: Vect, direction: Vect): #defines the origin point as a vector and the direction as a unit vector in the direction of the ray's travel
        self.origin = origin
        self.direction = direction#.normalise()

    def __repr__(self):
        return f"(Origin:{self.origin}, Direction:{self.direction})"

    def hitSphere(self, sphere: Sphere): #checks if the ray intersects a given sphere
        #define a, b, and c as the coefficients in the polynomial
        #a = self.direction.x ** 2 + self.direction.y ** 2 + self.direction.z ** 2
        #b = (2 * self.origin.x * self.direction.x - 2 * sphere.centre.x * self.direction.x +
        #     2 * self.origin.y * self.direction.y - 2 * sphere.centre.y * self.direction.y +
        #     2 * self.origin.z * self.direction.z - 2 * sphere.centre.z * self.direction.z)
        #c = (self.origin.x ** 2 + sphere.centre.x ** 2 - self.origin.x * sphere.centre.x +
        #     self.origin.y ** 2 + sphere.centre.y ** 2 - self.origin.y * sphere.centre.y +
        #     self.origin.z ** 2 + sphere.centre.z ** 2 - self.origin.z * sphere.centre.z -
        #     sphere.radius ** 2)
        OC = self.origin - sphere.centre
        a = self.direction.dot(self.direction) 
        b = 2 * self.direction.dot(OC)
        c = OC.dot(OC) - sphere.radius ** 2

        intersects = solveQuadratic(a, b, c) #returns False for no intersections, or a tuple of roots otherwise - root represents the distance along the ray that it intersects the sphere
        
        if intersects == False or (intersects[0] < 0 and intersects[1] < 0):
            return HitInfo(False, None, None, None, Vect(1,1,1), Vect(0,0,0), 0)
        
        dist = min(intersects) if intersects[0] > 0 and intersects[1] > 0 else max(intersects)
        
        hitPoint = self.origin + (self.direction * dist)
        normal = (hitPoint - sphere.centre).normalise()
        
        return HitInfo(True, dist, hitPoint, normal, sphere.colour, sphere.emissColour, sphere.emission)

class StaticRenderer:
    def __init__(self, width, height, camPos):
        self.width = width
        self.height = height
        self.camPos = Vect(camPos[0], camPos[1], camPos[2])
        self.image = PIL.Image.new(mode = "RGB", size = (width, height))
        self.objects = []
            
    def findRayHit(self, ray):
        closestHit = HitInfo(None, float("inf"), None, None, Vect(0,0,0), Vect(0,0,0), 0)
        for object in self.objects:
            if type(object) == Sphere:
                hitInfo = ray.hitSphere(object)
                if hitInfo.hit and (hitInfo.dist < closestHit.dist):
                    closestHit = hitInfo
                    #shade = (int(object.colour[0] - (hitInfo.dist * 2)), int(object.colour[1] - (hitInfo.dist * 2)), int(object.colour[2] - (hitInfo.dist * 2)))
        return closestHit
        
    def pixelShader(self, x, y, maxBounces): #run for every pixel on the screen, return colour as a triple of 0-255 values
        coord   = Vect(x, self.height - y, 1.0)
        coord  /= Vect(self.width, self.height, 1.0) 
        coord   = coord * 2 - 1
        coord.z = -1.0

        aspectRatio = self.width / self.height
        coord.x *= aspectRatio

        ray = Ray(Vect(0, 0, 0), coord.normalise())
        colour = Vect(1,1,1)
        light = Vect(0,0,0)

        hit = 0

        for i in range(maxBounces):
            hitInfo = self.findRayHit(ray)
            if hitInfo.hit:
                emission = (hitInfo.emissColour / 255) * hitInfo.emission
                light  += emission
                colour *= (hitInfo.colour / 255)

                ray.origin = hitInfo.hitPoint + hitInfo.normal * 0.01

                bounce = ray.direction - (hitInfo.normal * 2 * (ray.direction.dot(hitInfo.normal)))
                ray.direction = bounce.normalise()
            else:
                skyColor = Vect(0.2, 0.2, 0.3)
                light += colour * skyColor
                break

        return (light * 255).roundTuple()

    def centraliseCoord(self, x, y): #adjusts pixels to have 0,0 as centre x y (2D coords)
        nX = x - (self.width / 2)
        nY = (self.height / 2) - y
        return nX, nY

    def blitPixels(self):
        pixels = self.image.load()
        for y in range(self.height):
            for x in range(self.width):
                pixels[x,y] = self.pixelShader(x,y, 6)
                
    def render(self):
        startTime = time.perf_counter()

        self.objects.append(Sphere(Vect(0, 0, -5),  2,  Vect(0,255,0),   Vect(0,255,0),     2))
        self.objects.append(Sphere(Vect(4, 0, -5), 2,  Vect(0,0,255),   Vect(0,255,0),     0))
        
        print("Rendering scene...")

        self.blitPixels()
        print("Render time:", timer(startTime))
        print("Image size:",self.width,self.height)
        self.image.show()