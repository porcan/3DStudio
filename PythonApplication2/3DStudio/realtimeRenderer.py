# import necessary libraries
import math
import pygame
import pywavefront
from utilities import *

# class representing a 3D triangle
class Triangle:
    def __init__(self, p1: Vect, p2: Vect, p3: Vect, colour, rtArgs):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.colour = colour
        self.rtArgs = rtArgs # rendering attributes (["Triangle", shine, emission])

    def render(self, renderer): # renders the triangle to the screen
        if self.rtArgs[2] == 0: # if the triangle is not emissive
            # calculate distance from light source to determine shading
            distance = calculateDistance((self.p1 + self.p2 + self.p3) / 3, renderer.camPos / 10)
            distance = 1 + abs(distance / 100)
            shade = (self.colour[0] / distance, self.colour[1] / distance, self.colour[2] / distance)
            shade = (shade[0] * 255, shade[1] * 255, shade[2] * 255)
        else: # if the triangle is emissive, use its original colour instead
            shade = (self.colour[0] * 255, self.colour[1] * 255, self.colour[2] * 255)

        # project and render the triangle to the 2D screen
        pygame.draw.polygon(renderer.window, shade, (tuple(map(sum, zip(renderer.project(self.p1), renderer.globalTranslate))), 
                                                       tuple(map(sum, zip(renderer.project(self.p2), renderer.globalTranslate))), 
                                                       tuple(map(sum, zip(renderer.project(self.p3), renderer.globalTranslate)))))
    
    def getDistance(self, renderer): # calculates the distance of the triangle from the renderer camera
        # take an average of the x, y, and z components of the points, and use this point to calculate distance
        return calculateDistance((self.p1 + self.p2 + self.p3) / 3, renderer.camPos)

# class representing a 3D sphere
class Sphere:
    def __init__(self, centre: Vect, radius, colour, rtArgs):
        self.centre = centre
        self.radius = radius
        self.colour = colour
        self.rtArgs = rtArgs # rendering attributes (["Sphere", shine, emission])

    def render(self, renderer): # renders the sphere to the screen
        if self.rtArgs[2] == 0: # if sphere is not emissive
            # calculate distance from renderer camera to determine shading
            distance = calculateDistance(self.centre, renderer.camPos / 10)
            distance = 1 + abs(distance / 100)
            shade = (self.colour[0] / distance, self.colour[1] / distance, self.colour[2] / distance)
            shade = (shade[0] * 255, shade[1] * 255, shade[2] * 255)
        else:
            # if sphere is not emissive, use original colour
            shade = (self.colour[0] * 255, self.colour[1] * 255, self.colour[2] * 255)

        # project the sphere's centre to the 2D screen
        projectedCentre = tuple(map(sum, zip(renderer.project(self.centre), renderer.globalTranslate)))
        # project an outer point and use the distance to calculate a radius approximation
        projectedOuterPoint = tuple(map(sum, zip(renderer.project(self.centre + Vect(self.radius, 0, 0)), renderer.globalTranslate)))
        radius = math.sqrt((projectedOuterPoint[0] - projectedCentre[0])**2 + (projectedOuterPoint[1] - projectedCentre[1])**2)
        # project another point and take an average of the two for a more accurate radius approximation
        projectedOuterPoint = tuple(map(sum, zip(renderer.project(self.centre + Vect(0, self.radius, 0)), renderer.globalTranslate)))
        radius = (math.sqrt((projectedOuterPoint[0] - projectedCentre[0])**2 + (projectedOuterPoint[1] - projectedCentre[1])**2) + radius) / 2

        # draw the projected shape to the 2D screen
        pygame.draw.circle(renderer.window, shade, 
                               (int(projectedCentre[0]), int(projectedCentre[1])), 
                               radius)
    
    def getDistance(self, renderer): # calculates the distance from the centre of the circle to the renderer camera
        return calculateDistance(self.centre, renderer.camPos)

# function to collect and return all spheres from a list of different objects
def extractSpheres(list):
    extracted = []
    for item in list:
        if type(item) == Sphere:
            extracted.append(item)
    return extracted

# rotation functions using standard rotation matrices
def xRotate(coord, angle): # simulates matrix multiplication with x rotation matrix
    newX = coord.x
    newY = (coord.y * math.cos(angle)) - (coord.z * math.sin(angle))
    newZ = (coord.y * math.sin(angle)) + (coord.z * math.cos(angle))
    return Vect(newX, newY, newZ)

def yRotate(coord, angle): # simulates matrix multiplication with y rotation matrix
    newX = (coord.z * math.sin(angle)) + (coord.x * math.cos(angle))
    newY = coord.y
    newZ = (coord.z * math.cos(angle)) - (coord.x * math.sin(angle))
    return Vect(newX, newY, newZ)

def zRotate(coord, angle): # simulates matrix multiplication with z rotation matrix
    newX = (coord.x * math.cos(angle)) - (coord.y * math.sin(angle))
    newY = (coord.x * math.sin(angle)) + (coord.y * math.cos(angle))
    newZ = coord.z
    return Vect(newX, newY, newZ)

# main real-time renderer class
class RealtimeRenderer:
    def __init__(self, window, focalLength, baseCamPos: Vect, polyGoal, skyTint, skyLight, globalTranslate, demoMode):
        # initialises renderer with camera settings, environment, and other configurations
        self.window = window
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0
        self.focalLength = focalLength
        self.winWidth, self.winHeight = self.window.get_size()
        self.mouseX, self.mouseY = 0, 0
        self.baseCamPos = baseCamPos
        self.subdivisionAmount = 0
        self.polyGoal = polyGoal
        self.lastPolyCount = 0
        self.skyTint = skyTint
        self.skyLight = skyLight
        self.globalTranslate = globalTranslate
        self.demoMode = demoMode
        self.rotationLock = False
        
    def update(self):
        # get mouse position and update renderer rotation values based on mouse x and y 
        self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.mouseX -= self.window.width / 2
        self.mouseY -= self.window.height / 2
        self.mouseX /= 10
        self.mouseY /= 10
        self.xRotation, self.yRotation, self.zRotation = self.globalRotate()
        
        # update camera position with new rotation values
        self.camPos = yRotate(self.baseCamPos, self.yRotation)
        self.camPos = xRotate(self.camPos, self.xRotation)
        self.camPos = zRotate(self.camPos, self.zRotation)
        self.camPos.x = 0 - self.camPos.x
        self.camPos.y = 0 - self.camPos.y

    def getSphere(self, centre: Vect, radius, colour, shine, emission): # returns a realtime renderer sphere object with given parameters
        return Sphere(centre, radius, colour, ["Sphere", shine, emission])
    
    def getTriangle(self, p1: Vect, p2: Vect, p3: Vect, colour, shine, emission): # returns a realtime renderer triangle object with given parameters
        return Triangle(p1, p2, p3, colour, ["Triangle", shine, emission])

    def project(self, coord): # calculates 2D projection x and y of a point in 3D space, applying renderer rotation values
        coord = xRotate(coord, self.xRotation)
        coord = yRotate(coord, self.yRotation)
        coord = zRotate(coord, self.zRotation)
        coord.z -= 200
        # if dZ is 0, offset by a small amount to prevent division by zero errors
        if coord.z == 0:
            coord.z = 0.0001
        # return calculated projection
        return (0 - (self.focalLength * (coord.x / coord.z)) + self.winWidth / 2,
                0 - (self.focalLength * (coord.y / coord.z)) + self.winHeight / 2)

    def globalRotate(self): # update renderer rotation values
        # if rotation lock is enabled, return no rotation
        if self.rotationLock:
            return (0,0,0)
        # otherwise, rotate scene to follow standardised mouse position
        self.xRotation = (0 - self.mouseY) / 50
        self.yRotation = self.mouseX / 50
        self.zRotation = 0
        return (self.xRotation, self.yRotation, self.zRotation)

    def subdivide(self, triangles, amount): # function to split a triangle into smaller component triangles
        triangles = unnest([triangles]) # remove nesting in polygon array before processing
        # remove and store all spheres
        extracted = extractSpheres(triangles)
        triangles = list(filter(lambda i:type(i) is Triangle, triangles))
        # repeat subdivision by specified amount
        for _ in range(amount):
            triangles = unnest([triangles])
            temp = []
            for t in triangles:
                # create new triangles using midpoints of outer triangle calculated by averaging coordinate components
                part1 = Triangle(t.p1,
                                 (t.p1 + t.p2) / 2,
                                 (t.p1 + t.p3) / 2,
                                 t.colour, t.rtArgs)
                part2 = Triangle((t.p1 + t.p2) / 2,
                                 t.p2,
                                 (t.p2 + t.p3) / 2,
                                 t.colour, t.rtArgs)
                part3 = Triangle((t.p1 + t.p3) / 2,
                                 (t.p2 + t.p3) / 2,
                                 t.p3,
                                 t.colour, t.rtArgs)
                part4 = Triangle((t.p1 + t.p2) / 2,
                                 (t.p2 + t.p3) / 2,
                                 (t.p1 + t.p3) / 2,
                                 t.colour, t.rtArgs)
                temp.extend([part1, part2, part3, part4])
            # replace triangles with array of new smaller triangles
            triangles = temp
        # add previously removed spheres back to shape array
        triangles.extend(extracted)
        return [triangles]
    
    def group(self, triangles, amount): # function to combine a set of 4 triangles by taking their outer points
        triangles = unnest([triangles]) # remove nesting in polygon array before processing
        # remove and store all spheres
        extracted = extractSpheres(triangles)
        triangles = list(filter(lambda i:type(i) is Triangle, triangles))
        # repeat grouping by specified amount
        for _ in range(amount):
            triangles = unnest([triangles])
            temp = []
            # iterate through triangles in groups of 4
            for j in range(math.floor(len(triangles) / 4)):
                # select the 4 sequential triangles
                t1 = triangles[(4 * j) - 4]
                t2 = triangles[(4 * j) - 3]
                t3 = triangles[(4 * j) - 2]
                t4 = triangles[(4 * j) - 1]
                # create new triangle from outer points of the 4 triangles
                temp.append(Triangle(t1.p1,
                                     t2.p2,
                                     t3.p3,
                                     t4.colour, t4.rtArgs))
            triangles = temp
        # add spheres back to array
        triangles.extend(extracted)
        return [triangles]

    def createQuad(self, p1: Vect, p2: Vect, p3: Vect, p4: Vect, colour, rtArgs): # function to create a quadrilateral from 2 triangles
        # get distance of quadrilateral centre to pass shading value into component triangles
        distance = calculateDistance((p1 + p2 + p3 + p4) / 4, self.camPos / 10)
        distance = 1 + abs(distance / 100)
        shade = (colour[0] / distance, colour[1] / distance, colour[2] / distance)
        # return triangles forming the given quadrilateral
        return[Triangle(p1, p2, p3, shade, rtArgs),
               Triangle(p1, p3, p4, shade, rtArgs)]

    def createCube(self, sideLength, centre, colour, rtArgs): # creates a cube from quadrilaterals
        r = sideLength / 2 # "radius" of the cube
        # create each side of the cube by defining quadrilaterals from outer vertices
        return[self.createQuad(centre + Vect(0-r, r, 0-r),
                               centre + Vect(r, r, 0-r),
                               centre + Vect(r, 0-r, 0-r),
                               centre + Vect(0-r, 0-r, 0-r),
                               colour, rtArgs),
               self.createQuad(centre + Vect(0-r, r, 0-r),
                               centre + Vect(0-r, r, r),
                               centre + Vect(0-r, 0-r, r),
                               centre + Vect(0-r, 0-r, 0-r),
                               colour, rtArgs),
               self.createQuad(centre + Vect(0-r, r, r),
                               centre + Vect(r, r, r),
                               centre + Vect(r, 0-r, r),
                               centre + Vect(0-r, 0-r, r),
                               colour, rtArgs),
               self.createQuad(centre + Vect(r, r, r),
                               centre + Vect(r, r, 0-r),
                               centre + Vect(r, 0-r, 0-r),
                               centre + Vect(r, 0-r, r),
                               colour, rtArgs),
               self.createQuad(centre + Vect(0-r, r, 0-r),
                               centre + Vect(r, r, 0-r),
                               centre + Vect(r, r, r),
                               centre + Vect(0-r, r, r),
                               colour, rtArgs),
               self.createQuad(centre + Vect(0-r, 0-r, 0-r),
                               centre + Vect(r, 0-r, 0-r),
                               centre + Vect(r, 0-r, r),
                               centre + Vect(0-r, 0-r, r),
                               colour, rtArgs)]

    def trianglesFromMesh(self, mesh, faces, sf, colour, rtArgs): # take mesh from interpreted object file and translate to an array of triangle objects
        triangles = []
        for face in faces:
            temp = []
            for i in range(3):
                temp.append(mesh[face[i]])
            # create triangle from vertices of a face
            triangles.append(Triangle(Vect(temp[0][0] * sf, temp[0][1] * sf, temp[0][2] * sf), 
                                      Vect(temp[1][0] * sf, temp[1][1] * sf, temp[1][2] * sf), 
                                      Vect(temp[2][0] * sf, temp[2][1] * sf, temp[2][2] * sf), 
                                      colour, rtArgs))
        return triangles # return triangle object

    def load(self, obj, sf, colour, rtArgs): # get triangles from a specified object file
        if obj == 0:
            return 0
        else:
            # interpret object file with pywavefront
            data = pywavefront.Wavefront(obj, collect_faces = True)
            triangles = self.trianglesFromMesh(data.vertices, [face for mesh in data.mesh_list for face in mesh.faces], sf, colour, rtArgs)
            return[triangles]

    def setup(self, obj): # function to set up the shapes based on any input object mesh
        shapes = [] # initialise list to hold the shapes to be rendered
        if obj == 0: # if object is set to 0 (no object to be loaded), set up predefined shapes instead
            if self.demoMode: # if demo mode is enabled
                # create demo scene
                shapes.append(Sphere(Vect(-2400, -1200, -5000), 2000, normaliseRGB((255,255,255)), ["Sphere",0,1]))

                shapes.append(Sphere(Vect(-4, 12, 148), 8, normaliseRGB((255,255,255)), ["Sphere",0.9,0]))
                shapes.append(Sphere(Vect(16, 10, 148), 10, normaliseRGB((255, 52, 80)), ["Sphere",0,0.6]))
                shapes.append(Sphere(Vect(40, 8, 148), 12, normaliseRGB((38, 136, 240)), ["Sphere",0,0]))

                shapes.append(self.createCube(10, Vect(-20, 13, 148), normaliseRGB((0, 255, 255)), ["Triangle",0,0]))
            else: # if demo mode is not enabled
                # add a null shape to prevent issues with empty rendering list
                nullShape = self.createQuad(Vect(0,0,0), Vect(0,0,0), Vect(0,0,0), Vect(0,0,0), (0,0,0), ["Triangle",0,0])
                shapes.append(nullShape)

        else: # if an object mesh is passed in, append the given object to the shapes list
            shapes.append(obj)
        return [shapes]

    def render(self, allShapes): # subroutine to draw all shapes to the scene

        # update drawn sky colour based on light intensity and tint
        skyColour = tuple([(170 * self.skyLight) * x for x in self.skyTint])
        skyColour = tuple(min(255, max(0, c)) for c in skyColour) # clamps values in the range 0-255
        self.window.fill(skyColour) # draws sky
        
        # depending on subdivisionAmount, either subdivide or group shapes
        if self.subdivisionAmount >= 0:
            allShapes = self.subdivide(allShapes, self.subdivisionAmount) # perform subdivision the shapes
        else:
            allShapes = self.group(allShapes, 0 - self.subdivisionAmount) # perform grouping on the shapes

        allShapes = unnest(allShapes) # remove any nesting in the shape array
        
        if len(allShapes) <= (self.polyGoal / 4) and self.lastPolyCount <= self.polyGoal:
            # increase subdivision if the number of shapes is below 1/4 of the polygon limit
            self.subdivisionAmount += 1
        if len(allShapes) > self.polyGoal:
            # decrease subdivision if the number of shapes exceeds the polygon limit
            self.subdivisionAmount -= 1
        # update lastPolyCount to store number of shapes in the scene
        self.lastPolyCount = len(allShapes)
    
        # calculate the distances of each shape from the camera
        distances = []
        for i in range(len(allShapes)):
            # add all distances to an array with an identifier corresponding to the position of each triangle in allShapes
            distances.append([i, allShapes[i].getDistance(self)])
        # sort shapes in descending order according to the distances (item 1 of each sub array)
        distances = mergeSort(distances, True, 1) 

        sortedShapes = []
        for j in range(len(distances)):
            # append shapes to sorted shapes based on the order of their sorted distances
            sortedShapes.append(allShapes[distances[j][0]])
    
        # render each shape to the screen in their distance defined order
        for shape in sortedShapes:
            shape.render(self)