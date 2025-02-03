import time
import math
import numpy
import sys
import random

class Vect: #class for a 3D vector
    def __init__(self, x: float | int, y: float | int, z: float | int):
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
    
    def returnArray(self):
        return [self.x, self.y, self.z]

class OctNode:
    def __init__(self, position: Vect, radius: float, depth: int, data):
        self.position = position
        #children (xyz):
        #0: +++   1: ++-   2: -+-   3: -++
        #4: +-+   5: +--   6: ---   7: --+
        self.children = [None, None, None, None, None, None, None, None]
        self.radius = radius
        self.depth = depth
        self.data = data
        self.min = position - radius
        self.max = position + radius

    def addChild(self, childIndex, child):
        self.children[childIndex] = child

    def addData(self, data):
        self.data.append(data)

    def branch(self, rCount, maxDepth):
        f = self.radius / 2
        newDepth = self.depth + 1
        self.addChild(0, OctNode(self.position + Vect(f,f,f),    f, newDepth, []))
        self.addChild(1, OctNode(self.position + Vect(f,f,-f),   f, newDepth, []))
        self.addChild(2, OctNode(self.position + Vect(-f,f,-f),  f, newDepth, []))
        self.addChild(3, OctNode(self.position + Vect(-f,f,f),   f, newDepth, []))
        self.addChild(4, OctNode(self.position + Vect(f,-f,f),   f, newDepth, []))
        self.addChild(5, OctNode(self.position + Vect(f,-f,-f),  f, newDepth, []))
        self.addChild(6, OctNode(self.position + Vect(-f,-f,-f), f, newDepth, []))
        self.addChild(7, OctNode(self.position + Vect(-f,-f,f),  f, newDepth, []))
        if rCount < maxDepth:
            for child in self.children:
                child.branch(rCount + 1, maxDepth)
        else:
            return
    
    def rayIntersects(self, ray): #may need to check this
        epsilon = sys.float_info.epsilon
        tMin = ((self.min - ray.origin) / (ray.direction + epsilon)).returnArray()
        tMax = ((self.max - ray.origin) / (ray.direction + epsilon)).returnArray()
        
        t1 = numpy.minimum(tMin, tMax)
        t2 = numpy.maximum(tMin, tMax)
        
        tEntry = numpy.max(t1)
        tExit = numpy.min(t2)
        return (tEntry <= tExit and tExit >= 0)

class OctTree:
    def __init__(self, sceneRadius, maxDepth):
        self.root = OctNode(Vect(0,0,0), sceneRadius, 0, [])
        self.sceneRadius = sceneRadius
        self.maxDepth = maxDepth
        self.root.branch(0, maxDepth)

    def findLocation(self, location):
        node = self.root
        locationArray = location.returnArray()
        maxArray = node.max.returnArray()
        minArray = node.min.returnArray()
        #children (xyz):
        #0: +++   1: ++-   2: -+-   3: -++
        #4: +-+   5: +--   6: ---   7: --+
        for i in range(self.maxDepth + 1):
            if numpy.any(locationArray < minArray) or numpy.any(locationArray > maxArray):
                return False
            if location.x > node.position.x and location.y > node.position.y and location.z > node.position.z:
                node = node.children[0]
            elif location.x > node.position.x and location.y > node.position.y and location.z < node.position.z:
                node = node.children[1]
            elif location.x < node.position.x and location.y > node.position.y and location.z < node.position.z:
                node = node.children[2]
            elif location.x < node.position.x and location.y > node.position.y and location.z > node.position.z:
                node = node.children[3]
            elif location.x > node.position.x and location.y < node.position.y and location.z > node.position.z:
                node = node.children[4]
            elif location.x > node.position.x and location.y < node.position.y and location.z < node.position.z:
                node = node.children[5]
            elif location.x < node.position.x and location.y < node.position.y and location.z < node.position.z:
                node = node.children[6]
            elif location.x < node.position.x and location.y < node.position.y and location.z > node.position.z:
                node = node.children[7]
        return node
    
    def insertData(self, location, data):
        self.findLocation(location).addData(data)

    def rayCheck(self, node, ray, objects):
        if node.children[0] != None:
            for child in node.children:
                if child.rayIntersects(ray):
                    self.rayCheck(child, ray, objects)
        if len(node.data) > 0:
            objects.append(node.data)
        return objects
    
    def getObjects(self, ray):
        return unnest(self.rayCheck(self.root, ray, []))
        
def timer(startTime):
    return time.perf_counter() - startTime

def mergeSort(unsorted, rev, key): #merge sorts an array by a specified index (key) in a 2d array, taking unsorted as the array to be sorted, and rev as True or False for if reversed (relies on reverse())
    def sort(array):
        if len(array) > 1:
            midpoint = round((len(array) + 1) / 2) - 1
            firstHalf = array[:midpoint]
            secondHalf = array[midpoint:]
            sort(firstHalf)
            sort(secondHalf)
            a, b, c = 0, 0, 0
            while a < len(firstHalf) and b < len(secondHalf):
                if firstHalf[a][key] < secondHalf[b][key]:
                    array[c] = firstHalf[a]
                    a += 1
                else:
                    array[c] = secondHalf[b]
                    b += 1
                c += 1
            while a < len(firstHalf):
                array[c] = firstHalf[a]
                c += 1
                a += 1
            while b < len(secondHalf):
                array[c] = secondHalf[b]
                c += 1
                b += 1
            return array
    sortedArr = sort(unsorted)
    
    if rev == True:
        sortedArr = reverse(sortedArr)
    return sortedArr

def reverse(array): #returns the given array with terms in reverse order
    i = 0
    reversedArr = []
    for i in range(len(array)):
        reversedArr.append(array[(len(array) - i) - 1])
    return reversedArr

def unnest(nested): #function to un-nest a nested array of any dimension
    temp = []
    for i in nested:
        if type(i) == list:
            temp.extend(unnest(i))
        else:
            temp.append(i)
    return temp

def calculateDistance(x1, y1, z1, x2, y2, z2): #calculates distance between 2 points in 3d space
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

def normaliseRGB(rgb): #converts rgb from 0-255 ro 0-1 (normalised)
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

def solveQuadratic(a, b, c): #function for returning the roots of a quadratic equation.
    #calculate discriminant of the polynomial
    discriminant = (b**2) - (4*a*c)
    if discriminant < 0:
        return False #returns False if the equation has no real roots
    else:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return (root1, root2)