import time
import math
import random
import re
import os

class Vect: # class for a 3D vector
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"({self.x}, {self.y}, {self.z})"
        
    def __add__(self, add): # method for adding the vector to either a scalar or another vector
        if type(add) == Vect:
            return Vect(self.x + add.x, self.y + add.y, self.z + add.z)
        
        elif type(add) == int or type(add) == float:
            return Vect(self.x + add, self.y + add, self.z + add)
        
        return self

    def __sub__(self, sub): # method for subtracting a vector or scalar from the vector
        if type(sub) == Vect:
            return Vect(self.x - sub.x, self.y - sub.y, self.z - sub.z)
        
        elif type(sub) == int or type(sub) == float:
            return Vect(self.x - sub, self.y - sub, self.z - sub)
        
        return self

    def __mul__(self, mul): # method for multiplication by scalar
        if type(mul) == int or type(mul) == float:
            return Vect(self.x * mul, self.y * mul, self.z * mul)
        
        if type(mul) == Vect:
            return Vect(self.x * mul.x, self.y * mul.y, self.z * mul.z)

        return self
    
    def __truediv__(self, div): # method for division by scalar
        if type(div) == int or type(div) == float:
            return Vect(self.x / div, self.y / div, self.z / div)
        
        if type(div) == Vect:
            return Vect(self.x / div.x, self.y / div.y, self.z / div.z)

        return self

    def dot(self, dotVect): # method for calculating the dot product of the vector with another vector
        if type(dotVect) == Vect:
            return (self.x * dotVect.x) + (self.y * dotVect.y) + (self.z * dotVect.z)

    def mag(self): # returns the magnitude of the vector
        return math.sqrt((self.x ** 2) + (self.y ** 2) + (self.z ** 2))

    def angle(self, angleVect): # calculates the angle between the vector and another vector
        if type(angleVect) == Vect:
            # use dot product formula for angle
            radians = math.acos(self.dot(angleVect) / (self.mag() * angleVect.mag()))
            # convert to degrees from radians
            return radians * (180 / math.pi)

    def cross(self, crossVect): # calculates the cross product between the vector and another vector
        if type(crossVect) == Vect:
            return Vect((self.y * crossVect.z - self.z * crossVect.y),
                        (self.z * crossVect.x - self.x * crossVect.z),
                        (self.x * crossVect.y - self.y * crossVect.x))
        
    def normalise(self): # returns a unit vector in the same direction as the original vector
        if self.mag() == 0:
            # prevents division by zero errors
            return self
        
        # return vector with magnitude 1
        return Vect((self.x / self.mag()),
                    (self.y / self.mag()),
                    (self.z / self.mag()))
    
    def roundTuple(self): # return x,y,z as a tuple of integers
        return (round(self.x), round(self.y), round(self.z))
    
    def returnArray(self): # return x,y,z as an array
        return [self.x, self.y, self.z]

def uiHide(elements): # method to hide any number of ui elements at once
    for element in elements:
        element.hide()

def uiShow(elements): # method to show any number of ui elements at once
    for element in elements:
        element.show()

def isValidCoordinate(string): # use regex to check if given input is in coordinate format
    string = string.replace(" ", "")
    return re.fullmatch("(-?(([0-9]+)|([0-9]+.[0-9]+)),){2}-?(([0-9]+)|([0-9]+.[0-9]+))", string)

def isValidHexCode(string): # use regex to check if given input is in colour hex code format
    string = string.replace(" ", "")
    return re.fullmatch("([0-9]|[A-F]){6}", string)

def isValidSmallDec(string): # use regex to check if given input is in format of float range 0-1
    string = string.replace(" ", "")
    if re.fullmatch("([0-9]+)|([0-9]+.[0-9]+)", string):
        if 0 <= float(string) <= 1:
            return True
    return False

def isInDirectory(string): # check if a file is found in the program directory
    valid = False
    for file in os.listdir("."):
        if file == string:
            valid = True
    return valid

def isValidPositive(string): # use regex to check if given input is in positive real number format
    string = string.replace(" ", "")
    return re.fullmatch("([0-9]+)|([0-9]+.[0-9]+)", string)

def hexToRGB(hex): # converts hexadecimal colour code to a tuple of 0-255 rgb values
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:], 16)
    return (r, g, b)

def timer(startTime): # calculate elapsed time
    return time.perf_counter() - startTime

# merge sorts a 2D array by a specified index (key) of each item
def mergeSort(unsorted, rev, key):
    # define a recursive function to sort 
    def sort(array):
        if len(array) > 1: # base case - only sort if array has more than 1 element
            # get midpoint of array and split by midpoint
            midpoint = len(array) // 2
            firstHalf = array[:midpoint]
            secondHalf = array[midpoint:]
            sort(firstHalf) # recursively sort left half
            sort(secondHalf) # recursively sort second half
            a, b, c = 0, 0, 0 # initialise indices for merging
            while a < len(firstHalf) and b < len(secondHalf):
                if firstHalf[a][key] < secondHalf[b][key]: # compare elements using given key
                    array[c] = firstHalf[a] # place smaller element into main array
                    a += 1
                else:
                    array[c] = secondHalf[b] # place smaller element into main array
                    b += 1
                c += 1 # iterate to next position
            # copy remaining elements
            while a < len(firstHalf):
                array[c] = firstHalf[a]
                c += 1
                a += 1
            while b < len(secondHalf):
                array[c] = secondHalf[b]
                c += 1
                b += 1
            return array # return the merged array
    sortedArr = sort(unsorted) # call sorting function on the input array
    
    if rev == True:
        # if reversed order is needed, reverse the array
        sortedArr = reverse(sortedArr)
    return sortedArr # return the final sorted array

def reverse(array): # returns the given array with terms in reverse order
    i = 0
    reversedArr = []
    for i in range(len(array)):
        reversedArr.append(array[(len(array) - i) - 1])
    return reversedArr

def unnest(nested): # function to remove nesting in an array of any dimension
    temp = [] # temporary list to store flattened elements
    for i in nested:
        if type(i) == list: # check if element is a nested structure
            temp.extend(unnest(i)) # recursive call to flatten the sublist
        else:
            temp.append(i) # append non-list items directly
    return temp # return flattened list

def calculateDistance(p1, p2): # calculates distance between 2 points in 3d space
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2 + (p2.z - p1.z)**2)

def normaliseRGB(rgb): # converts rgb from 0-255 to 0-1 (normalised)
    return (rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)

def solveQuadratic(a, b, c): # function for returning the roots of a quadratic equation
    # calculate discriminant of the polynomial
    discriminant = (b**2) - (4*a*c)
    if discriminant < 0:
        return False # returns False if the equation has no real roots
    else:
        # calculate roots and return
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return (root1, root2)
    
def randomVector(): # returns a vector with each component randomised
    return Vect(random.random() * 2 - 1.0, random.random() * 2 - 1.0, random.random() * 2.0 - 1.0)

class StackNode: # holds data held in the stack, as well as a pointer to the next node
    def __init__(self, lower, data):
        self.lower = lower
        self.data = data

class Stack: # stack data structure implemented as a linked list of StackNode objects
    def __init__(self):
        self.top = None

    def __repr__(self):
        if self.hasData():
            node = self.top
            out = []
            while node.lower is not None:
                out.append(node.data)
                node = node.lower
            out.append(node.data)
            return str(out)
        else:
            return "empty"

    def hasData(self): # check if the stack is empty
        return self.top is not None
    
    def push(self, item): # push an item to the stack
        node = StackNode(self.top, item)
        self.top = node

    def pop(self): # remove and return top item of the stack
        if self.hasData():
            data = self.top
            self.top = self.top.lower
            return data.data
        
    def peek(self): # return top item
        return self.top
    