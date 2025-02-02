import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
from sys import exit
from realtimeRenderer import *
from staticRenderer import *
from utilities import *

if __name__ == "__main__":


    # octTree = OctTree(2000,1)
    # for i in range(20):
    #     octTree.insertData(Vect(random.random(), random.random(), random.random()) * 1000, random.randint(1,100000))
    # octTree.insertData(Vect(0,0,5), "hhh")
    # ray = Ray(Vect(0,0,0), Vect(0,0,-1))
    # print(octTree.getObjects(ray))









    # a = 1/0
    state = "setup" #states: setup, editor, rendering

    pygame.init()
    clock = pygame.time.Clock()

    opt = int(input("Renderer Main Menu\n1 - Run demo\n2 - Load file\n3 - Open editor"))
    if opt == 2:
        obj = input("File to load: ")
        sf = float(input("SF: "))
        shapes = (obj, sf)
    else:
        shapes = (0, 0)
    if not opt == 1:
        camPos = input("Camera position: ")
        camPos = tuple(int(x) for x in camPos.split(","))
        baseCamX, baseCamY, baseCamZ = camPos
        lightPos = input("Light source (CAM for camera): ")
    else:
        baseCamX, baseCamY, baseCamZ = 0, 0, 1000
        lightPos = "CAM"
    if not lightPos == "CAM":
        lightPos = tuple(int(y) for y in lightPos.split(","))
    
    polyGoal = int(input("Polygon display limit (reccommended 1000): "))

    winWidth, winHeight = 810, 540
    window = pygame.display.set_mode((winWidth, winHeight), pygame.RESIZABLE)

    count = 0
    focalLength = 300
    rt = RealtimeRenderer(window, focalLength, clock, baseCamX, baseCamY, baseCamZ, polyGoal, lightPos)

    startTime = time.perf_counter()

    objColour = normaliseRGB((255, 92, 0))
    loadedObj = rt.load(shapes[0],shapes[1], objColour)

    rt.placeEye(0,0,150,(200,200))

    rt.update()

    state = "rendering"
    #state = "editor"

    polygons = unnest(rt.setup(loadedObj))
    while state == "editor":
        rt.update()
        rt.render(polygons)
    
        pygame.display.flip()
        rt.clock.tick()
        count += 1
    
        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                rt.focalLength += event.y * 20
                if rt.focalLength < 4:
                    rt.focalLength = 4 #prevents focal length from inverting (negative)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    rt.eyeShowHide()
                if event.key == pygame.K_r:
                    state = "rendering"
                    pygame.quit()
                
    renderInput = None
    resolutions = [(1280,720),
                   (640,360)]
    
    width, height = resolutions[1]
    windowSize = (960,540)

    pygame.init()
    sr = StaticRenderer(width,height,(0,0,0),pygame.display.set_mode(windowSize, pygame.RESIZABLE),polygons)
    sr.render()