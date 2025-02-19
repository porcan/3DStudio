#from genericpath import samefile
import pygame
import math
import pywavefront
import keyboard
from utilities import *

class Triangle: #each individual triangle can be rendered and moved
    def __init__(self, outer, x1, y1, z1, x2, y2, z2, x3, y3, z3, colour, rtArgs):
        self.outer = outer
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1
        self.x2 = x2
        self.y2 = y2
        self.z2 = z2
        self.x3 = x3
        self.y3 = y3
        self.z3 = z3
        self.colour = colour
        self.rtArgs = rtArgs #should contain ["Triangle", shine, emission] in range 0-1
    
    # def move(self, mX, mY, mZ): #transforms the x, y and z values of the triangle object
    #     self.x1, self.x2, self.x3 = self.x1 + mX, self.x2 + mX, self.x3 + mX
    #     self.y1, self.y2, self.y3 = self.y1 + mY, self.y2 + mY, self.y3 + mY
    #     self.z1, self.z2, self.z3 = self.z1 + mZ, self.z2 + mZ, self.z3 + mZ

    def render(self): #renders the triangle object on screen
        distance = calculateDistance((self.x1 + self.x2 + self.x3) / 3, (self.y1 + self.y2 + self.y3) / 3, (self.z1 + self.z2 + self.z3) / 3, self.outer.lightX / 10, self.outer.lightY / 10, self.outer.lightZ / 10)
        distance = 1 + abs(distance / 100)
        shade = (self.colour[0] / distance, self.colour[1] / distance, self.colour[2] / distance)
        shade = (shade[0] * 255, shade[1] * 255, shade[2] * 255)
        pygame.draw.polygon(self.outer.window, shade, (tuple(map(sum, zip(self.outer.project(self.x1, self.y1, self.z1), self.outer.globalTranslate))), 
                                                       tuple(map(sum, zip(self.outer.project(self.x2, self.y2, self.z2), self.outer.globalTranslate))), 
                                                       tuple(map(sum, zip(self.outer.project(self.x3, self.y3, self.z3), self.outer.globalTranslate)))))
    
    def getDistance(self):
        return calculateDistance(((self.x1 + self.x2 + self.x3) / 3), ((self.y1 + self.y2 + self.y3) / 3), ((self.z1 + self.z2 + self.z3) / 3), self.outer.camX, self.outer.camY, self.outer.camZ)

class Sphere:
    def __init__(self, outer, x, y, z, radius, colour, rtArgs):
        self.outer = outer
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.colour = colour
        self.rtArgs = rtArgs #should contain ["Sphere", shine, emission] in range 0-1

    def render(self):
        if self.rtArgs[2] == 0:
            distance = calculateDistance(self.x, self.y, self.z, self.outer.lightX / 10, self.outer.lightY / 10, self.outer.lightZ / 10)
            distance = 1 + abs(distance / 100)
            shade = (self.colour[0] / distance, self.colour[1] / distance, self.colour[2] / distance)
            shade = (shade[0] * 255, shade[1] * 255, shade[2] * 255)
        else:
            shade = (self.colour[0] * 255, self.colour[1] * 255, self.colour[2] * 255)

        projectedCentre = tuple(map(sum, zip(self.outer.project(self.x, self.y, self.z), self.outer.globalTranslate)))
        projectedOuterPoint = tuple(map(sum, zip(self.outer.project(self.x + self.radius, self.y, self.z), self.outer.globalTranslate)))
        radius = math.sqrt((projectedOuterPoint[0] - projectedCentre[0])**2 + (projectedOuterPoint[1] - projectedCentre[1])**2)
        projectedOuterPoint = tuple(map(sum, zip(self.outer.project(self.x, self.y + self.radius, self.z), self.outer.globalTranslate)))
        radius = (math.sqrt((projectedOuterPoint[0] - projectedCentre[0])**2 + (projectedOuterPoint[1] - projectedCentre[1])**2) + radius) / 2

        pygame.draw.circle(self.outer.window, shade, 
                               (int(projectedCentre[0]), int(projectedCentre[1])), 
                               radius)
    
    def getDistance(self):
        return calculateDistance((self.x), (self.y), (self.z), self.outer.camX, self.outer.camY, self.outer.camZ)
    
def extractSpheres(list):
    extracted = []
    for item in list:
        if type(item) == Sphere:
            extracted.append(item)
    return extracted

class RealtimeRenderer:
    def __init__(self, window, focalLength, clock, baseCamX, baseCamY, baseCamZ, polyGoal, lightPos, skyTint, skyLight, globalTranslate, demoMode):
        self.window = window
        self.xRotation = 0
        self.yRotation = 0
        self.zRotation = 0
        self.focalLength = focalLength
        self.winWidth,  self.winHeight, self.mouseX, self.mouseY = 0, 0, 0, 0
        self.clock = clock
        self.baseCamX, self.baseCamY, self.baseCamZ = baseCamX, baseCamY, baseCamZ
        self.subdivisionAmount = 0
        self.polyGoal = polyGoal
        self.lightPos = lightPos
        if not self.lightPos == "CAM":
            self.lightX, self.lightY, self.lightZ = self.lightPos
        self.lastPolyCount = 0
        self.dynamicSubdivision = True
        self.eye = [0,0,0,(0,0),False] #camera for rendering stored as position (x,y,z) and show/hide (True/False)
        self.skyTint = skyTint
        self.skyLight = skyLight
        self.globalTranslate = globalTranslate
        self.demoMode = demoMode
        self.rotationLock = False
        
    def update(self):
        self.winWidth, self.winHeight = self.window.get_size()
        self.mouseX, self.mouseY = pygame.mouse.get_pos()
        self.mouseX -= self.window.width / 2
        self.mouseY -= self.window.height / 2
        self.mouseX /= 10
        self.mouseY /= 10
        self.xRotation, self.yRotation, self.zRotation = self.globalRotate()
        
        self.camX, self.camY, self.camZ = self.yRotate(self.baseCamX, self.baseCamY, self.baseCamZ, self.yRotation)
        self.camX, self.camY, self.camZ = self.xRotate(self.camX, self.camY, self.camZ, self.xRotation)
        self.camX, self.camY, self.camZ = self.zRotate(self.camX, self.camY, self.camZ, self.zRotation)
        self.camX = 0 - self.camX
        self.camY = 0 - self.camY
        
        if self.lightPos == "CAM":
            self.lightX, self.lightY, self.lightZ = self.camX, self.camY, self.camZ
        elif 1 == 0: #optional controls for moving lights
            if keyboard.is_pressed("x+up arrow"):
                self.lightX += 40
            elif keyboard.is_pressed("x+down arrow"):
                self.lightX -= 40
            if keyboard.is_pressed("y+up arrow"):
                self.lightY += 40
            elif keyboard.is_pressed("y+down arrow"):
                self.lightY -= 40
            if keyboard.is_pressed("z+up arrow"):
                self.lightZ += 40
            elif keyboard.is_pressed("z+down arrow"):
                self.lightZ -= 40
    
    def placeEye(self,x,y,z,fov):
        self.eye = [x,y,z,fov,False]
   
    def eyeShowHide(self):
        if self.eye[4]:
            self.eye[4] = False
        else:
            self.eye[4] = True

    def project(self,x,y,z): #calculates 2d projection x and y of a point in 3d space, applying global rotation values
        dX, dY, dZ = self.xRotate(x, y, z, self.xRotation)
        dX, dY, dZ = self.yRotate(dX, dY, dZ, self.yRotation)
        dX, dY, dZ = self.zRotate(dX, dY, dZ, self.zRotation)
        dZ -= 200
        if dZ == 0:
            dZ = 0.0001
        return (0 - (self.focalLength * (dX / dZ)) + self.winWidth / 2, 0 - (self.focalLength * (dY / dZ)) + self.winHeight / 2) #flips x and y bc they were opposite for some reason

    def globalRotate(self):
        if self.rotationLock:
            return (0,0,0)
        self.xRotation = (0 - self.mouseY) / 50
        self.yRotation = self.mouseX / 50
        self.zRotation = 0
        return (self.xRotation, self.yRotation, self.zRotation)

    def subdivide(self, triangles, amount): #relies on unnest() utility
        triangles = unnest([triangles])
        #now remove all non triangles ie spheres
        extracted = extractSpheres(triangles)
        triangles = list(filter(lambda i:type(i) is Triangle, triangles))
        for i in range(amount):
            triangles = unnest([triangles])
            temp = []
            for t in triangles:
                part1 = Triangle(self, t.x1, t.y1, t.z1,
                                            (t.x1 + t.x2) / 2, (t.y1 + t.y2) / 2, (t.z1 + t.z2) / 2,
                                            (t.x1 + t.x3) / 2, (t.y1 + t.y3) / 2, (t.z1 + t.z3) / 2,
                                             t.colour, t.rtArgs)
                part2 = Triangle(self, (t.x1 + t.x2) / 2, (t.y1 + t.y2) / 2, (t.z1 + t.z2) / 2,
                                            t.x2, t.y2, t.z2,
                                            (t.x2 + t.x3) / 2, (t.y2 + t.y3) / 2, (t.z2 + t.z3) / 2,
                                            t.colour, t.rtArgs)
                part3 = Triangle(self, (t.x1 + t.x3) / 2, (t.y1 + t.y3) / 2, (t.z1 + t.z3) / 2,
                                            (t.x2 + t.x3) / 2, (t.y2 + t.y3) / 2, (t.z2 + t.z3) / 2,
                                            t.x3, t.y3, t.z3,
                                            t.colour, t.rtArgs)
                part4 = Triangle(self, (t.x1 + t.x2) / 2, (t.y1 + t.y2) / 2, (t.z1 + t.z2) / 2,
                                            (t.x2 + t.x3) / 2, (t.y2 + t.y3) / 2, (t.z2 + t.z3) / 2,
                                            (t.x1 + t.x3) / 2, (t.y1 + t.y3) / 2, (t.z1 + t.z3) / 2,
                                            t.colour, t.rtArgs)
                temp.extend([part1, part2, part3, part4])
            triangles = temp
        triangles.extend(extracted)
        return [triangles]
    
    def group(self, triangles, amount): #take subdivide() and reverse to combine 4 trianges into 1 (improve performance by making sure #polygons is under limit)
        triangles = unnest([triangles])
        #now remove all non triangles ie spheres
        triangles = list(filter(lambda i:type(i) is Triangle, triangles))
        for i in range(amount):
            triangles = unnest([triangles])
            temp = []
            for j in range(math.floor(len(triangles) / 4)):
                t1 = triangles[(4 * j) - 4]
                t2 = triangles[(4 * j) - 3]
                t3 = triangles[(4 * j) - 2]
                t4 = triangles[(4 * j) - 1]
                temp.append(Triangle(self, t1.x1, t1.y1, t1.z1,
                                                t2.x2, t2.y2, t2.z2,
                                                t3.x3, t3.y3, t3.z3,
                                                t4.colour, t4.rtArgs))
            triangles = temp
        return [triangles]

    def createQuad(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4, colour, rtArgs): #creates a quadrilateral from triangles
        distance = calculateDistance((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, (z1 + z2 + z3 + z4) / 4, self.camX / 10, self.camY / 10, self.camZ / 10)
        distance = 1 + abs(distance / 100)
        shade = (colour[0] / distance, colour[1] / distance, colour[2] / distance)
        return[Triangle(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, shade, rtArgs),
               Triangle(self, x1, y1, z1, x3, y3, z3, x4, y4, z4, shade, rtArgs)]
    
    def createEye(self, radius, x, y, z): #creates the static renderer camera preview
        temp = []
        temp.append(self.createCube(radius, x, y, z, normaliseRGB((255,0,0))))
        s = 20 #scale for fov marker
        temp.append(self.createLine(x + (radius / 2), y + (radius / 2), z - (radius / 2), 0 - s*(x-radius), 0 - s*(y-radius), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine(x + (radius / 2), y - (radius / 2), z - (radius / 2), 0 - s*(x-radius), 0 - s*(y+radius), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine(x - (radius / 2), y - (radius / 2), z - (radius / 2), 0 - s*(x+radius), 0 - s*(y+radius), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine(x - (radius / 2), y + (radius / 2), z - (radius / 2), 0 - s*(x+radius), 0 - s*(y-radius), 0, normaliseRGB((255,0,0))))
        
        temp.append(self.createLine(0 - (self.eye[3][0] / 2), 0 - (self.eye[3][1] / 2), 0, 0 - (self.eye[3][0] / 2), (self.eye[3][1] / 2), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine(0 - (self.eye[3][0] / 2), (self.eye[3][1] / 2), 0, (self.eye[3][0] / 2), (self.eye[3][1] / 2), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine((self.eye[3][0] / 2), (self.eye[3][1] / 2), 0, (self.eye[3][0] / 2), 0 - (self.eye[3][1] / 2), 0, normaliseRGB((255,0,0))))
        temp.append(self.createLine((self.eye[3][0] / 2), 0 - (self.eye[3][1] / 2), 0, 0 - (self.eye[3][0] / 2), 0 - (self.eye[3][1] / 2), 0, normaliseRGB((255,0,0))))
        return temp

    def createCube(self, sideLength, x, y, z, colour, rtArgs): #creates a cube from quadrilaterals
        p = sideLength / 2
        return[self.createQuad(x - p, y + p, z - p, x + p, y + p, z - p, x + p, y - p, z - p, x - p, y - p, z - p, colour, rtArgs),
               self.createQuad(x - p, y + p, z - p, x - p, y + p, z + p, x - p, y - p, z + p, x - p, y - p, z - p, colour, rtArgs),
               self.createQuad(x - p, y + p, z + p, x + p, y + p, z + p, x + p, y - p, z + p, x - p, y - p, z + p, colour, rtArgs),
               self.createQuad(x + p, y + p, z + p, x + p, y + p, z - p, x + p, y - p, z - p, x + p, y - p, z + p, colour, rtArgs),
               self.createQuad(x - p, y + p, z - p, x + p, y + p, z - p, x + p, y + p, z + p, x - p, y + p, z + p, colour, rtArgs),
               self.createQuad(x - p, y - p, z - p, x + p, y - p, z - p, x + p, y - p, z + p, x - p, y - p, z + p, colour, rtArgs)]
    
    def createLine(self, x1, y1, z1, x2, y2, z2, colour):
        return self.createQuad(x1, y1, z1 + 0.5, x1, y1, z1 - 0.5, x2, y2, z2 + 0.5, x2, y2, z2 - 0.5, colour, rtArgs)

    def xRotate(self, x, y, z, deg): #calculates rotation of a point around x axis
        newX = x
        newY = (y * math.cos(deg)) - (z * math.sin(deg))
        newZ = (y * math.sin(deg)) + (z * math.cos(deg))
        return newX, newY, newZ

    def yRotate(self, x, y, z, deg): #calculates rotation of a point around y axis
        newX = (z * math.sin(deg)) + (x * math.cos(deg))
        newY = y
        newZ = (z * math.cos(deg)) - (x * math.sin(deg))
        return newX, newY, newZ

    def zRotate(self, x, y, z, deg): #calculates rotation of a point around z axis
        newX = (x * math.cos(deg)) - (y * math.sin(deg))
        newY = (x * math.sin(deg)) + (y * math.cos(deg))
        newZ = z
        return newX, newY, newZ

    def trianglesFromMesh(self, x, y, z, mesh, faces, sf, colour, rtArgs):
        triangles = []
        for face in faces:
            temp = []
            for i in range(3):
                temp.append(mesh[face[i]])
            triangles.append(Triangle(self, 
                                      temp[0][0] * sf + x, temp[0][1] * sf + y, temp[0][2] * sf + z, 
                                      temp[1][0] * sf + x, temp[1][1] * sf + y, temp[1][2] * sf + z, 
                                      temp[2][0] * sf + x, temp[2][1] * sf + y, temp[2][2] * sf + z, 
                                      colour, rtArgs))
        return triangles #returns Triangle objects from an obj mesh

    def load(self, obj, sf, colour): #creates a mesh from the vertices of an obj file (relies on trianglesFromMesh())
        if obj == 0:
            return 0
        else:
            data = pywavefront.Wavefront(obj, collect_faces = True)
            meshB1 = self.trianglesFromMesh(0, 0, 0, data.vertices, [face for mesh in data.mesh_list for face in mesh.faces], sf, colour)
            return[meshB1]

    def setup(self, obj):
        colourA = normaliseRGB((38, 136, 240))
        colourA = tuple([((1 - x) / 2) + x for x in colourA])
        colourB = normaliseRGB(tuple([(255 * self.skyLight) * x for x in self.skyTint])) #remove this later i beg
        colourB = tuple([((1 - x) / 2) + x for x in colourB])

        shadedShapes = []
        unshadedShapes = []
        if obj == 0:
            #replace with normal scene ie ground sphere and light sphere
            cube1 = self.createQuad(0,0,0,0,0,0,0,0,0,0,0,0,colourB, ["Triangle",0,0])
            shadedShapes.append(cube1)
            if self.demoMode:
                # shadedShapes.append(self.createCube(100, 0, 0, 0, colourA, ["Triangle",0,0]))
                # shadedShapes.append(Sphere(self, 60, 0, 50, 10, colourA, ["Sphere",0,0]))

                shadedShapes.append(Sphere(self, -2400, -1200, -5000, 2000, normaliseRGB((255,255,255)), ["Sphere",0,1])) #sun
                # shadedShapes.append(Sphere(self, 0, 4000, 180, 3980, normaliseRGB((100,100,100)), ["Sphere",0.5,0])) #ground

                shadedShapes.append(Sphere(self, -4, 12, 148, 8, normaliseRGB((255,255,255)), ["Sphere",0.9,0.5]))
                shadedShapes.append(Sphere(self, 16, 10, 148, 10, normaliseRGB((255, 52, 80)), ["Sphere",0,0]))
                shadedShapes.append(Sphere(self, 40, 8, 148, 12, normaliseRGB((38, 136, 240)), ["Sphere",0,0]))

                shadedShapes.append(self.createCube(10, -20, 13, 148, normaliseRGB((0, 255, 255)), ["Triangle",0,0]))
                
                # shadedShapes.append(Sphere(self, 50, -50, 0, 10, colourA, ["Sphere",0.5,0]))
                # shadedShapes.append(Sphere(self, -50, 50, 0, 20, colourB, ["Sphere",0.5,0]))
        else:
            shadedShapes.append(obj) #return all objects on screen as an array ie return[cube1, cube2, quad1, quad2]
        if self.eye[4]:
            unshadedShapes.append(self.createEye(5, self.eye[0], self.eye[1], self.eye[2]))
        return [shadedShapes, unshadedShapes]

    def render(self, allShapes):
        skyColour = tuple([(255 * self.skyLight) * x for x in self.skyTint])
        self.window.fill(skyColour)
        
        if self.subdivisionAmount >= 0:
            allShapes = self.subdivide(allShapes, self.subdivisionAmount)
        else:
            allShapes = self.group(allShapes, 0 - self.subdivisionAmount)

        allShapes = unnest(allShapes)
        
        if self.dynamicSubdivision:
            if len(allShapes) <= (self.polyGoal / 4) and self.lastPolyCount <= self.polyGoal:
                self.subdivisionAmount += 1
        if len(allShapes) > self.polyGoal:
            self.subdivisionAmount -= 1
        self.lastPolyCount = len(allShapes)
    
        distances = []
        for i in range(len(allShapes)):
            distances.append([i, allShapes[i].getDistance()]) #adds all distances to an array with an identifier corresponding to the position of each triangle in allShapes
        distances = mergeSort(distances, True, 1) #sorts distances in descending order according to the distances (item 1 of each sub array)
        newAllShapes = []
        for j in range(len(distances)):
            newAllShapes.append(allShapes[distances[j][0]])
    
        for shape in newAllShapes:
            shape.render()
        