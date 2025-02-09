import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
from sys import exit
from realtimeRenderer import *
from staticRenderer import *
from utilities import *
import pygame_gui as gui

if __name__ == "__main__":

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("3D Studio - Main Menu")
    clock = pygame.time.Clock()
    
    winWidth, winHeight = 810, 540
    window = pygame.display.set_mode((winWidth, winHeight))
    guiManager = gui.UIManager((winWidth, winHeight))
    title = pygame.image.load(random.choice(["menu.png", "menu2.png", "menu3.png"]))

    runDemoButton = gui.elements.UIButton(relative_rect = pygame.Rect((155, 287), (100, 50)), text = "Run Demo", manager = guiManager)
    loadFileButton = gui.elements.UIButton(relative_rect = pygame.Rect((288, 287), (100, 50)), text = "Load File", manager = guiManager)
    openEditorButton = gui.elements.UIButton(relative_rect = pygame.Rect((422, 287), (100, 50)), text = "Open Editor", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((555, 287), (100, 50)), text = "Quit", manager = guiManager)

    state = "setup" #states: setup, editor, rendering
    while state == "setup":
        clock.tick()
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        window.blit(title, (0, 0))
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == runDemoButton:
                    runDemoButton.kill()
                    shapes = (0, 0)
                    baseCamX, baseCamY, baseCamZ = 0, 0, 1000
                    lightPos = "CAM"
                    polyGoal = 1000 #int(input("Polygon display limit (reccommended 1000): "))
                    state = "editor"
                    state = "rendering"
                elif event.ui_element == loadFileButton:
                    obj = input("File to load: ")
                    sf = float(input("SF: "))
                    shapes = (obj, sf)
                    camPos = input("Camera position: ")
                    camPos = tuple(int(x) for x in camPos.split(","))
                    baseCamX, baseCamY, baseCamZ = camPos
                    lightPos = input("Light source (CAM for camera): ")
                    if not lightPos == "CAM":
                        lightPos = tuple(int(y) for y in lightPos.split(","))
                    polyGoal = int(input("Polygon display limit (reccommended 1000): "))
                    state = "editor"
                elif event.ui_element == openEditorButton:
                    shapes = (0, 0)
                    camPos = input("Camera position: ")
                    camPos = tuple(int(x) for x in camPos.split(","))
                    baseCamX, baseCamY, baseCamZ = camPos
                    lightPos = input("Light source (CAM for camera): ")
                    if not lightPos == "CAM":
                        lightPos = tuple(int(y) for y in lightPos.split(","))
                    polyGoal = int(input("Polygon display limit (reccommended 1000): "))
                    state = "editor"
                elif event.ui_element == quitButton:
                    quit()
            guiManager.process_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    runDemoButton.hide()
    loadFileButton.hide()
    openEditorButton.hide()
    quitButton.hide()

    # opt = int(input("Renderer Main Menu\n1 - Run demo\n2 - Load file\n3 - Open editor"))
    # if opt == 2:
    #     obj = input("File to load: ")
    #     sf = float(input("SF: "))
    #     shapes = (obj, sf)
    # else:
    #     shapes = (0, 0)
    # if not opt == 1:
    #     camPos = input("Camera position: ")
    #     camPos = tuple(int(x) for x in camPos.split(","))
    #     baseCamX, baseCamY, baseCamZ = camPos
    #     lightPos = input("Light source (CAM for camera): ")
    # else:
    #     baseCamX, baseCamY, baseCamZ = 0, 0, 1000
    #     lightPos = "CAM"
    # if not lightPos == "CAM":
    #     lightPos = tuple(int(y) for y in lightPos.split(","))
    
    # polyGoal = int(input("Polygon display limit (reccommended 1000): "))

    count = 0
    focalLength = 300
    rt = RealtimeRenderer(window, focalLength, clock, baseCamX, baseCamY, baseCamZ, polyGoal, lightPos)

    startTime = time.perf_counter()

    objColour = normaliseRGB((255, 92, 0))
    loadedObj = rt.load(shapes[0],shapes[1], objColour)

    rt.placeEye(0,0,150,(200,200))

    rt.update()

    #state = "editor"
    pygame.display.set_caption("3D Studio - Editor")

    polygons = unnest(rt.setup(loadedObj))
    while state == "editor":
        clock.tick()
        count += 1
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        rt.update()
        rt.render(polygons)
    
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                rt.focalLength += event.y * 20
                if rt.focalLength < 4:
                    rt.focalLength = 4 #prevents focal length from inverting (negative)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    rt.eyeShowHide()
                if event.key == pygame.K_r:
                    state = "rendering"
                    # pygame.quit()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
    renderInput = None
    resolutions = [(1280,720),
                   (640,360)]
    
    width, height = resolutions[1]
    windowSize = (960,540)

    pygame.display.set_caption("3D Studio - Rendering...")
    window = pygame.display.set_mode(windowSize)

    polygons = [] #clears mesh to be passed in, remove later
    sr = StaticRenderer(width, height, (0,0,0), window, polygons)
    sr.render()