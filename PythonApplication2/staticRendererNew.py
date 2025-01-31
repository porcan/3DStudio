from multiprocessing import Pool
import os
import sys
import random
import math
import numpy as np
import time
import pygame
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
            return Vect(self.x / div, self.y / div, self.z / div)
        
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


def randomVector() -> Vect:
    return Vect(random.random() * 2 - 1.0, random.random() * 2 - 1.0, random.random() * 2.0 - 1.0)        
    
class Sphere:
    def __init__(self, centre: Vect, radius, colour: Vect, shine: float, emission: float):
        self.centre = centre
        self.radius = radius
        self.colour = colour
        self.shine = shine
        self.emission = emission

class Triangle:
    def __init__(self, p1: Vect, p2: Vect, p3: Vect, colour: Vect, shine: float, emission: float):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.colour = colour
        self.shine = shine
        self.emission = emission
        
class HitInfo:
    def __init__(self, hit: bool, dist: float, hitPoint: Vect, normal: Vect, colour: Vect, shine: Vect, emission: float):
        self.hit = hit
        self.dist = dist
        self.hitPoint = hitPoint
        self.normal = normal
        self.colour = colour
        self.shine = shine
        self.emission = emission
    
class Ray:
    def __init__(self, origin: Vect, direction: Vect): #defines the origin point as a vector and the direction as a unit vector in the direction of the ray's travel
        self.origin = origin
        self.direction = direction.normalise()

    def __repr__(self):
        return f"(Origin:{self.origin}, Direction:{self.direction})"

    def hitSphere(self, sphere: Sphere): #checks if the ray intersects a given sphere
        OC = self.origin - sphere.centre
        a = self.direction.dot(self.direction)  # or self.direction.x**2 + self.direction.y**2 + self.direction.z**2
        b = 2 * self.direction.dot(OC)
        c = OC.dot(OC) - sphere.radius ** 2

        intersects = solveQuadratic(a, b, c) #returns False for no intersections, or a tuple of roots otherwise - root represents the distance along the ray that it intersects the sphere
        
        if intersects == False or (intersects[0] < 0 and intersects[1] < 0):
            return HitInfo(False, None, None, None, Vect(1,1,1), Vect(0,0,0), 0)

        dist = min(intersects) if intersects[0] > 0 and intersects[1] > 0 else max(intersects)
        
        hitPoint = self.origin + (self.direction * dist)
        normal = (hitPoint - sphere.centre).normalise()
        
        return HitInfo(True, dist, hitPoint, normal, sphere.colour, sphere.shine, sphere.emission)
    
    def hitTriangle(self, triangle: Triangle):
        return
    
class StaticRenderer:
    def __init__(self, width, height, camPos, screen):
        self.width = width
        self.height = height
        self.camPos = Vect(camPos[0], camPos[1], camPos[2])
        self.objects = []
        self.accumulationBuffer =  np.full((width, height), Vect(0, 0, 0), dtype=object)
        self.frames = 1
        self.surface = np.zeros((width, height, 3), dtype=np.uint8)
        self.screen = screen

    @staticmethod
    def findRayHit(objects, ray):
        closestHit = HitInfo(None, float("inf"), None, None, Vect(0,0,0), Vect(0,0,0), 0)
        for object in objects:
            if type(object) == Sphere:
                hitInfo = ray.hitSphere(object)
                if hitInfo.hit and (hitInfo.dist < closestHit.dist):
                    closestHit = hitInfo
        return closestHit

    @staticmethod
    def pixelShader(args):
        objects, x, y, maxBounces, width, height = args
        coord   = Vect(x, height - y, 1.0)
        coord  /= Vect(width, height, 1.0) 
        coord   = coord * 2 - 1
        coord.z = -1.0

        aspectRatio = width / height
        coord.x *= aspectRatio

        blur = 0.002 #small amount of blur for antialiasing
        coord += randomVector() * blur

        ray = Ray(Vect(0, 0, 0), coord.normalise())
        colour = Vect(1,1,1)
        light  = Vect(0,0,0)
        cos = 1

        for _ in range(maxBounces):
            hitInfo = StaticRenderer.findRayHit(objects, ray)
            if hitInfo.hit:
                light  += hitInfo.colour * hitInfo.emission 
                colour *= hitInfo.colour
                
                ray.origin = hitInfo.hitPoint + hitInfo.normal * 0.01

                reflect = (ray.direction - (hitInfo.normal * 2 * (ray.direction.dot(hitInfo.normal)))).normalise()

                scatter = (randomVector() + hitInfo.normal).normalise()
                bounce = ((reflect.normalise() * hitInfo.shine) + (scatter.normalise() * (Vect(1,1,1) - hitInfo.shine)))/2

                ray.direction = bounce
                cos = max(hitInfo.normal.dot(ray.direction), 0) * 2

            else:
                skyAmt = 0.5 / ((ray.direction.y + 1) ** 2)
                skyColor = Vect(skyAmt, skyAmt, skyAmt * 1.7)
                light += colour * skyColor * cos
                break

        return light * 1.5
    
    def parallelShading(self):
        coords = [(self.objects, index % self.width, index // self.width, 2, self.width, self.height) for index in range(self.width * self.height)]
        
        with Pool() as pool:
            colors = pool.map(StaticRenderer.pixelShader, coords)
        
        for coord, color in zip(coords, colors):
            x, y = coord[1], coord[2]
            self.accumulationBuffer[x, y] += color
        
        #coords = [(self.objects, index % self.width, index // self.width, 2, self.width, self.height) for index in range(self.width * self.height)]
        #
        #with Pool() as pool:
        #    colors = pool.map(StaticRenderer.pixelShader, coords)
        #
        #for coord, color in zip(coords, colors):
        #    x, y = coord[1], coord[2]
        #    self.accumulationBuffer[x, y] += color
        
    def show(self):
        generator = ((index % self.width, index // self.width) for index in range(self.width * self.height))
        
        for x, y in generator:
            color = (self.accumulationBuffer[x, y] * 255)  
            color /= float(self.frames)
            color = color.roundTuple()
            color = tuple(min(255, max(0, c)) for c in color)
            
            self.surface[x, y] = color

        pySurface = pygame.surfarray.make_surface(self.surface)

        scaledSurface = pygame.transform.scale(pySurface, self.screen.get_size())

        self.screen.blit(scaledSurface, (0, 0))

        pygame.display.flip()
                
    def render(self):
        self.objects.append(Sphere(Vect(-600, 300, -1500), 500, Vect(1,1,1), 0, 1))
        self.objects.append(Sphere(Vect(-5.5, -3.5, -13), 1.5, Vect(1,1,1), 0.5, 0))
        self.objects.append(Sphere(Vect(-1, -3, -13), 2, Vect(1,1,1), 0.9, 0))
        self.objects.append(Sphere(Vect(4, -2.5, -13), 2.5, Vect(112, 240, 38) / 255, 0, 0.5))
        self.objects.append(Sphere(Vect(10, -2, -13), 3, Vect(38, 136, 240) / 255, 0, 0))
        self.objects.append(Sphere(Vect(0, -1000, -5), 995, Vect(200, 200, 200) / 255, 0, 0)) #171, 117, 219

        print("Rendering scene...")

        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            start = time.time()
            self.parallelShading()
            self.show()
            end = time.time()
            print("frame: ", self.frames, " took ", end - start, " seconds")
            self.frames += 1
        
        pySurface = pygame.surfarray.make_surface(self.surface)
        pygame.image.save(pySurface, "image.png")

        pygame.quit()