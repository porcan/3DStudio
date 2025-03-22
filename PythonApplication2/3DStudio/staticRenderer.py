from multiprocessing import Pool
import sys
import numpy as np
import time
import pygame
from utilities import *
    
class Sphere: # class representing a sphere object
    def __init__(self, centre, radius, colour, shine, emission):
        self.centre = centre
        self.radius = radius
        self.colour = colour
        self.shine = shine
        self.emission = emission

class Triangle: # class representing a triangle object
    def __init__(self, p1, p2, p3, colour, shine, emission):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.colour = colour
        self.shine = shine
        self.emission = emission
        
class HitInfo: # structure for storing information about a ray-object intersection
    def __init__(self, hit, dist, hitPoint, normal, colour, shine, emission):
        self.hit = hit # indicates if an intersection occured
        self.dist = dist # distance from ray origin to intersection point
        self.hitPoint = hitPoint # coordinate of the intersection
        self.normal = normal # surface normal at the intersection point
        # object information
        self.colour = colour
        self.shine = shine
        self.emission = emission
    
class Ray: # class representing a ray, with origin and direction
    def __init__(self, origin, direction):
        # define the origin point as a vector and the direction as a unit vector
        self.origin = origin
        self.direction = direction.normalise()

    def __repr__(self):
        return f"(Origin:{self.origin}, Direction:{self.direction})"

    def hitSphere(self, sphere): # checks if the ray intersects a given sphere
        rayToCentre = self.origin - sphere.centre
        # coefficients for the quadratic equation
        a = self.direction.dot(self.direction)
        b = 2 * self.direction.dot(rayToCentre)
        c = rayToCentre.dot(rayToCentre) - sphere.radius ** 2
        # solve quadratic equation to find intersection points
        intersects = solveQuadratic(a, b, c) # returns False for no intersections, or a tuple of roots otherwise
        
        # if there is no valid intersection or if intersection lies behind ray origin
        if intersects == False or (intersects[0] < 0 and intersects[1] < 0):
            return HitInfo(False, None, None, None, None, None, None)

        # choose the closest positive intersection
        # if both roots are positive, take the smaller
        # if only one is positive, take the positive
        dist = min(intersects) if intersects[0] > 0 and intersects[1] > 0 else max(intersects)
        
        # compute the intersection point using the ray equation
        hitPoint = self.origin + (self.direction * dist)
        # compute surface normal at the intersection point
        normal = (hitPoint - sphere.centre).normalise()
        # return intersection details
        return HitInfo(True, dist, hitPoint, normal, sphere.colour, sphere.shine, sphere.emission)
    
    def hitTriangle(self, triangle): # checks if ray intersects triangle using Möller-Trumbore algorithm
        epsilon = sys.float_info.epsilon # small value to handle floating point precision errors
        # compute the two edges of the triangle
        edge1 = triangle.p2 - triangle.p1
        edge2 = triangle.p3 - triangle.p1
        # calculate determinat to check if the ray and triangle are parallel
        rayCrossE2 = self.direction.cross(edge2)
        det = edge1.dot(rayCrossE2)
        # if ray and triangle are parallel or very close to parallel, return no hit
        if det > -epsilon and det < epsilon:
            return HitInfo(False, None, None, None, None, None, None)
        # compute inverse determinant
        invDet = 1 / det
        # calculate the vector from the first vertex to the ray origin
        # then compute the first barycentric coordinate u
        s = self.origin - triangle.p1
        u = invDet * s.dot(rayCrossE2)
        # if u is outside the valid range, intersection lies outside the triangle, so return no hit
        if ((u < 0 and abs(u) > epsilon) or (u > 1 and abs(u-1) > epsilon)):
            return HitInfo(False, None, None, None, None, None, None)
        # calculate the second barycentric coordinate v
        sCrossE1 = s.cross(edge1)
        v = invDet * self.direction.dot(sCrossE1)
        # if v is outsid the valid range or u + v is greater than 1, the intersection is outside the triangle
        if ((v < 0 and abs(v) > epsilon) or (u + v > 1 and abs(u + v - 1) > epsilon)):
            return HitInfo(False, None, None, None, None, None, None)
        # calculate distance between ray origin and intersection point
        dist = invDet * edge2.dot(sCrossE1)
        # if intersection is in front of the ray origin, hit has occurred
        if dist > epsilon:
            # compute intersection point and surface normal
            hitPoint = self.origin + (self.direction * dist)
            normal = edge1.cross(edge2).normalise()
            # return the intersection details
            return HitInfo(True, dist, hitPoint, normal, triangle.colour, triangle.shine, triangle.emission)
        else:
            # if intersection is behind the ray origin, return no hit
            return HitInfo(False, None, None, None, None, None, None)
    
class StaticRenderer:
    def __init__(self, width, height, camPos, screen, meshIn, skyTint, skyLight):
        self.width = width
        self.height = height
        self.camPos = Vect(camPos[0], camPos[1], camPos[2]) # camera position as a vector
        self.objects = [] # stores scene objects
        # create buffer to store accumulated frames for averaging
        self.accumulationBuffer =  np.full((width, height), Vect(0, 0, 0), dtype=object)
        self.frames = 1
        # final image buffer
        self.surface = np.zeros((width, height, 3), dtype=np.uint8)
        self.screen = screen # pygame display surface
        self.skyTint = skyTint
        self.skyLight = skyLight
        # defines values for converting between coordinate systems
        coordRatio = 0.25
        zOffset = -50
        # convert mesh objects into scene objects
        for shape in meshIn:
            # if shape identifier is triangle, convert information to static renderer triangle object
            if shape.rtArgs[0] == "Triangle":
                self.objects.append(Triangle(Vect(shape.p1.x * coordRatio, (0 - shape.p1.y) * coordRatio, (shape.p1.z * coordRatio) + zOffset), 
                                             Vect(shape.p2.x * coordRatio, (0 - shape.p2.y) * coordRatio, (shape.p2.z * coordRatio) + zOffset), 
                                             Vect(shape.p3.x * coordRatio, (0 - shape.p3.y) * coordRatio, (shape.p3.z * coordRatio) + zOffset), 
                                             Vect(shape.colour[0], shape.colour[1], shape.colour[2]), shape.rtArgs[1], shape.rtArgs[2]))
            # if shape identifier is sphere, convert information to static renderer sphere object
            elif shape.rtArgs[0] == "Sphere":
                self.objects.append(Sphere(Vect(shape.centre.x * coordRatio, (0 - shape.centre.y) * coordRatio, (shape.centre.z * coordRatio) + zOffset), shape.radius * coordRatio, Vect(shape.colour[0], shape.colour[1], shape.colour[2]), shape.rtArgs[1], shape.rtArgs[2]))
                
    @staticmethod
    def findRayHit(objects, ray):
        # initialised closest hit of no intersection and infinite distance
        closestHit = HitInfo(None, float("inf"), None, None, Vect(0,0,0), Vect(0,0,0), 0)

        # interate through objects, checking for intersection with each
        for obj in objects:
            if type(obj) == Sphere:
                hitInfo = ray.hitSphere(obj)
            elif type(obj) == Triangle:
                hitInfo = ray.hitTriangle(obj)

            # update closest hit if any found hit is at a shorter distance along the ray
            if hitInfo.hit and (hitInfo.dist < closestHit.dist):
                closestHit = hitInfo

        return closestHit

    @staticmethod
    def pixelShader(args):
        objects, x, y, maxBounces, width, height, skyTint, skyLight = args
        # convert pixel coordinates to normalised coordinates for direction vector of rays
        coord = Vect(x, height - y, 1.0)
        coord /= Vect(width, height, 1.0)
        coord = coord * 2 - 1
        coord.z = -1.0
        # adjust for aspect ratio of screen
        aspectRatio = width / height
        coord.x *= aspectRatio
        # add a small amount of random blur for anti-aliasing
        blur = 0.002
        coord += randomVector() * blur

        # initiailse ray
        ray = Ray(Vect(0, 0, 0), coord.normalise())
        # initialise gathered colour and lighting
        colour = Vect(1,1,1)
        light  = Vect(0,0,0)
        cos = 1

        # repeat bouncing ray up to specified maximum
        for _ in range(maxBounces):
            # find closest intersection of ray with an object
            hitInfo = StaticRenderer.findRayHit(objects, ray)
            if hitInfo.hit:
                # gather object colour and any emitted light
                colour *= hitInfo.colour
                light  += colour * hitInfo.emission
                # offset origin slightly to prevent intersection with the same object again
                ray.origin = hitInfo.hitPoint + hitInfo.normal * 0.01
                # compute perfect reflection for specular reflection
                reflect = (ray.direction - (hitInfo.normal * 2 * (ray.direction.dot(hitInfo.normal)))).normalise()
                # compute random scattering for diffuse reflection
                scatter = (randomVector() + hitInfo.normal).normalise()
                # calculate wieghted average of specular and diffuse reflection based on object's shine property
                bounce = ((reflect.normalise() * hitInfo.shine) + (scatter.normalise() * (Vect(1,1,1) - hitInfo.shine)))/2

                # set mew ray direction
                ray.direction = bounce
                # apply cos weighting
                cos = max(hitInfo.normal.dot(ray.direction), 0) * 2

            else:
                # compute environment colour to gather based on ray direction
                skyAmt = skyLight / ((ray.direction.y + 1.2) ** 2)
                skyColour = Vect(skyAmt * skyTint[0], skyAmt * skyTint[1], skyAmt * skyTint[2])
                # apply accumulated colour and cos weighting to calculate final light
                light += colour * skyColour * cos
                break
        # return gathered colour from traversal of the scene
        return light * 1.5
    
    def parallelShading(self): # speeds up calculation process by implementing parallel computation
        # create a list of tasks to complete (one for each pixel)
        coords = [(self.objects, index % self.width, index // self.width, 5, self.width, self.height, self.skyTint, self.skyLight)
                  for index in range(self.width * self.height)]
        # execute in parallel, mapping pixelShader to all tasks
        with Pool() as pool:
            colours = pool.map(StaticRenderer.pixelShader, coords)
        
        # accumulate the colour values in accumulation buffer
        for coord, colour in zip(coords, colours):
            x, y = coord[1], coord[2]
            self.accumulationBuffer[x, y] += colour
        
    def show(self): # renders accumulated image to the screen
        # create generator to iterate through each pixels coordinates
        generator = ((index % self.width, index // self.width) for index in range(self.width * self.height))
        
        # loop through every pixel
        for x, y in generator:
            # yield colour and adjust for current number of calculated frames
            colour = (self.accumulationBuffer[x, y] * 255)
            colour /= float(self.frames)
            colour = colour.roundTuple()
            # clamp colour values to acceptable range
            colour = tuple(min(255, max(0, c)) for c in colour)
            
            # assign the computed colour to the corresponding pixel in the surface
            self.surface[x, y] = colour

        # create pygame surface and draw to screen
        pySurface = pygame.surfarray.make_surface(self.surface)
        scaledSurface = pygame.transform.scale(pySurface, self.screen.get_size())
        self.screen.blit(scaledSurface, (0, 0))
        pygame.display.flip()
                
    def render(self): # handles the rendering process of the scene in a loop
        # add a large sphere object to act as the ground
        self.objects.append(Sphere(Vect(0, -10000, -5), 9995, Vect(100,100,100) / 255, 0.5, 0))

        running = True
        totalTime = 0
        # main rendering loop, runs until the user closes the window
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            start = time.time()
            # call parallelShading to run the necessary pixel calculations in parallel
            self.parallelShading()
            # draw accumulated image to the screen
            self.show()
            end = time.time()
            # calculate frame time for debugging and performance testing
            frameTime = end - start
            self.frames += 1
        
        pySurface = pygame.surfarray.make_surface(self.surface)
        # save the output image to the directory to be opened later
        pygame.image.save(pySurface, "image.png")

        pygame.quit()