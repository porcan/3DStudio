from multiprocessing import Pool
import sys
import random
import numpy as np
import time
import pygame
from utilities import *

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
            return HitInfo(False, None, None, None, None, None, None)

        dist = min(intersects) if intersects[0] > 0 and intersects[1] > 0 else max(intersects)
        
        hitPoint = self.origin + (self.direction * dist)
        normal = (hitPoint - sphere.centre).normalise()
        
        return HitInfo(True, dist, hitPoint, normal, sphere.colour, sphere.shine, sphere.emission)
    
    def hitTriangle(self, triangle: Triangle):
        epsilon = sys.float_info.epsilon
        edge1 = triangle.p2 - triangle.p1
        edge2 = triangle.p3 - triangle.p1
        rayCrossE2 = self.direction.cross(edge2)
        det = edge1.dot(rayCrossE2)
        if det > -epsilon and det < epsilon:
            return HitInfo(False, None, None, None, None, None, None)
        invDet = 1 / det
        s = self.origin - triangle.p1
        u = invDet * s.dot(rayCrossE2)
        if ((u < 0 and abs(u) > epsilon) or (u > 1 and abs(u-1) > epsilon)):
            return HitInfo(False, None, None, None, None, None, None)
        sCrossE1 = s.cross(edge1)
        v = invDet * self.direction.dot(sCrossE1)
        if ((v < 0 and abs(v) > epsilon) or (u + v > 1 and abs(u + v - 1) > epsilon)):
            return HitInfo(False, None, None, None, None, None, None)
        dist = invDet * edge2.dot(sCrossE1)
        if dist > epsilon:
            hitPoint = self.origin + (self.direction * dist)
            normal = edge1.cross(edge2).normalise()
            return HitInfo(True, dist, hitPoint, normal, triangle.colour, triangle.shine, triangle.emission)
        else:
            return HitInfo(False, None, None, None, None, None, None)
    
class StaticRenderer:
    def __init__(self, width, height, camPos, screen, meshIn):
        self.width = width
        self.height = height
        self.camPos = Vect(camPos[0], camPos[1], camPos[2])
        self.objects = []#OctTree(2000,3)
        self.accumulationBuffer =  np.full((width, height), Vect(0, 0, 0), dtype=object)
        self.frames = 1
        self.surface = np.zeros((width, height, 3), dtype=np.uint8)
        self.screen = screen
        coordRatio = 0.25
        zOffset = -250
        for triangle in meshIn:
            self.objects.insertData(Vect((triangle.x1 + triangle.x2 + triangle.x3) / 3,
                                         (triangle.y1 + triangle.y2 + triangle.y3) / 3,
                                         (triangle.z1 + triangle.z2 + triangle.z3) / 3),
                                     Triangle(Vect(triangle.x1, triangle.y1, triangle.z1 + zOffset) * coordRatio, 
                                         Vect(triangle.x2, triangle.y2, triangle.z2 + zOffset) * coordRatio, 
                                         Vect(triangle.x3, triangle.y3, triangle.z3 + zOffset) * coordRatio, 
                                         Vect(triangle.colour[0], triangle.colour[1], triangle.colour[2]), 0, 0))
            
    @staticmethod
    def findRayHit(objects, ray):
        closestHit = HitInfo(None, float("inf"), None, None, Vect(0,0,0), Vect(0,0,0), 0)

        #filteredObjects = objects.getObjects(ray)
        for obj in objects:
            if type(obj) == Sphere:
                hitInfo = ray.hitSphere(obj)
            elif type(obj) == Triangle:
                hitInfo = ray.hitTriangle(obj)

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

        blur = 0.001 #small amount of blur for antialiasing
        coord += randomVector() * blur

        ray = Ray(Vect(0, 0, 0), coord.normalise())
        colour = Vect(1,1,1)
        light  = Vect(0,0,0)
        cos = 1

        for _ in range(maxBounces):
            hitInfo = StaticRenderer.findRayHit(objects, ray)
            if hitInfo.hit:

                colour *= hitInfo.colour
                light  += colour * hitInfo.emission
                
                ray.origin = hitInfo.hitPoint + hitInfo.normal * 0.01

                reflect = (ray.direction - (hitInfo.normal * 2 * (ray.direction.dot(hitInfo.normal)))).normalise()

                scatter = (randomVector() + hitInfo.normal).normalise()
                bounce = ((reflect.normalise() * hitInfo.shine) + (scatter.normalise() * (Vect(1,1,1) - hitInfo.shine)))/2

                ray.direction = bounce
                cos = max(hitInfo.normal.dot(ray.direction), 0) * 2

            else:
                skyAmbience = (1.5,1.3,1) #standard 1,1,1.7
                darkness = 0.5 #standard 0.5
                skyAmt = darkness / ((ray.direction.y + 1) ** 2)
                skyColor = Vect(skyAmt * skyAmbience[0], skyAmt * skyAmbience[1], skyAmt  * skyAmbience[2])
                light += colour * skyColor * cos
                break

        return light * 1.5
    
    def parallelShading(self):
        coords = [(self.objects, index % self.width, index // self.width, 3, self.width, self.height) for index in range(self.width * self.height)]
        
        with Pool() as pool:
            colours = pool.map(StaticRenderer.pixelShader, coords)
        
        for coord, colour in zip(coords, colours):
            x, y = coord[1], coord[2]
            self.accumulationBuffer[x, y] += colour
        
    def show(self):
        generator = ((index % self.width, index // self.width) for index in range(self.width * self.height))
        
        for x, y in generator:
            colour = (self.accumulationBuffer[x, y] * 255)  
            colour /= float(self.frames)
            colour = colour.roundTuple()
            colour = tuple(min(255, max(0, c)) for c in colour)
            
            self.surface[x, y] = colour

        pySurface = pygame.surfarray.make_surface(self.surface)

        scaledSurface = pygame.transform.scale(pySurface, self.screen.get_size())

        self.screen.blit(scaledSurface, (0, 0))

        pygame.display.flip()
                
    def render(self):
        self.objects = []
        self.objects.append(Sphere(Vect(-600, 300, -1500), 500, Vect(1,1,1), 0, 1)) #main "sun"
        self.objects.append(Sphere(Vect(0, -1000, -5), 995, Vect(100,100,100) / 255, 0.5, 0)) #main "ground" 171, 117, 219

        self.objects.append(Sphere(Vect(-1, -3, -13), 2, Vect(1,1,1), 0.9, 0))
        self.objects.append(Sphere(Vect(4, -2.5, -13), 2.5, Vect(255, 52, 80) / 255, 0, 0.5))
        self.objects.append(Sphere(Vect(10, -2, -13), 3, Vect(38, 136, 240) / 255, 0, 0))

        

        # self.objects.append(Triangle(Vect(4.4, -2.4, -13), #abc
        #                              Vect(0.5, 0, -5), 
        #                              Vect(-7.75, -4.6, -15), Vect(1,1,1), 0.5, 0))
        # self.objects.append(Triangle(Vect(-7.75, -4.6, -15), #abd
        #                              Vect(0.5, 0, -5), 
        #                              Vect(0.85, 4, -15), Vect(1,1,1), 0.5, 0))
        # self.objects.append(Triangle(Vect(0.85, 4, -15), #dbc
        #                              Vect(0.5, 0, -5), 
        #                              Vect(4.4, -2.4, -13), Vect(1,1,1), 0.5, 0))
        
        # tVect = Vect(20,5,0)
        # self.objects.append(Triangle(Vect(4.4, -2.4, -13) + tVect, #abc
        #                              Vect(0.5, 0, -5) + tVect, 
        #                              Vect(-7.75, -4.6, -15) + tVect, Vect(1,1,1), 0.5, 0))
        # self.objects.append(Triangle(Vect(-7.75, -4.6, -15) + tVect, #abd
        #                              Vect(0.5, 0, -5) + tVect, 
        #                              Vect(0.85, 4, -15) + tVect, Vect(1,1,1), 0.5, 0))
        # self.objects.append(Triangle(Vect(0.85, 4, -15) + tVect, #dbc
        #                              Vect(0.5, 0, -5) + tVect, 
        #                              Vect(4.4, -2.4, -13) + tVect, Vect(1,1,1), 0.5, 0))
        
        # self.objects.append(Triangle(Vect(4.4, -2.4, -13) - tVect, #abc
        #                              Vect(0.5, 0, -5) - tVect, 
        #                              Vect(-7.75, -4.6, -15) - tVect, Vect(1,1,1), 0, 0))
        # self.objects.append(Triangle(Vect(-7.75, -4.6, -15) - tVect, #abd
        #                              Vect(0.5, 0, -5) - tVect, 
        #                              Vect(0.85, 4, -15) - tVect, Vect(1,1,1), 0, 0))
        # self.objects.append(Triangle(Vect(0.85, 4, -15) - tVect, #dbc
        #                              Vect(0.5, 0, -5) - tVect, 
        #                              Vect(4.4, -2.4, -13) - tVect, Vect(1,1,1), 0, 0))
        
        # self.objects.append(Sphere(Vect(8, -2.5, -13), 2.5, Vect(235, 149, 52) / 255, 0, 1))
        # self.objects.append(Sphere(Vect(-10, -2.5, -13), 2.5, Vect(38, 136, 240) / 255, 0, 1))



        # self.objects.append(Sphere(Vect(-200, 0, -1500), 500, Vect(1,1,1), 0, 1))

        # self.objects.append(Triangle(Vect(-5, 0, -15), #abc
        #                              Vect(0, 0, -10), 
        #                              Vect(0, 10, -15), Vect(219, 117, 171) / 255, 0, 0))
        # self.objects.append(Triangle(Vect(0, 0, -10), #bcd
        #                              Vect(0, 10, -15), 
        #                              Vect(5, 0, -15), Vect(1,1,1), 0, 0))
        # self.objects.append(Triangle(Vect(-5, 0, -15), #abe
        #                              Vect(0, 0, -10), 
        #                              Vect(0, -10, -15), Vect(1,1,1), 0, 0))
        # self.objects.append(Triangle(Vect(0, 0, -10), #bed
        #                              Vect(0, -10, -15), 
        #                              Vect(5, 0, -15), Vect(1,1,1), 0, 1))

        # self.objects.append(Sphere(Vect(0, -1000, -5), 995, Vect(219, 117, 171) / 255, 0.75, 0))
        # self.objects.append(Sphere(Vect(-4, -4, -13), 1, Vect(0.2,0.05,0.05), 0, 0))



        # for item in objectList:
            # if type(item) == Sphere:
            #     self.objects.insertData(item.centre, item)
            # elif type(item) == Triangle:
            #     self.objects.insertData((item.p1 + item.p2 + item.p3) / 3, item)
        #quit()

        print("Rendering scene...")

        running = True

        totalTime = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            start = time.time()
            self.parallelShading()
            self.show()
            end = time.time()
            frameTime = end - start
            print("frame:", self.frames, "took", frameTime, "seconds")
            totalTime += frameTime
            print("Total render time:", totalTime)
            self.frames += 1
        
        pySurface = pygame.surfarray.make_surface(self.surface)
        pygame.image.save(pySurface, "image.png")

        pygame.quit()