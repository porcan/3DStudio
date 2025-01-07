import time
import pywavefront
import math

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