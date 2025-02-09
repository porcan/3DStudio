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

    count = 0
    focalLength = 300
    skyTint = (1.5,1.3,1) #standard 1,1,1.7
    skyLight = 0.5
    globalTranslate = (490,0,0)
    rt = RealtimeRenderer(window, focalLength, clock, baseCamX, baseCamY, baseCamZ, polyGoal, lightPos, skyTint, skyLight, globalTranslate)

    startTime = time.perf_counter()

    objColour = normaliseRGB((255, 92, 0))
    loadedObj = rt.load(shapes[0],shapes[1], objColour)

    rt.placeEye(0,0,150,(200,200))

    rt.update()

    state = "editor"
    pygame.display.set_caption("3D Studio - Editor")

    renderButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 37), (100, 50)), text = "Render", manager = guiManager)
    editSkyButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 103), (100, 50)), text = "Edit Sky", manager = guiManager)
    addShapeButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 169), (100, 50)), text = "Add Shape", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 456), (100, 50)), text = "Quit", manager = guiManager)

    polygons = unnest(rt.setup(loadedObj))
    while state == "editor":
        clock.tick()
        count += 1
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        rt.update()
        rt.render(polygons)
        pygame.draw.rect(window, (17, 16, 33), pygame.Rect(0, 0, 170, winHeight))
        font = pygame.font.SysFont("calibri", 32)
        text1 = font.render("Camera position: " + str(round(rt.camX)) + ", " + str(round(rt.camY)) + ", " + str(round(rt.camZ)), True, (255, 255, 255))
        text1Pos = text1.get_rect()
        text1Pos.topleft = (180, 10)

        text3 = font.render("FPS: " + str(round(rt.clock.get_fps())), True, (255, 255, 255))
        text3Pos = text3.get_rect()
        text3Pos.topleft = (180, 100)
        window.blit(text1, text1Pos)

        window.blit(text3, text3Pos) #writing data to screen as text
    
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
            if event.type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == renderButton:
                    runDemoButton.kill()
                    state = "rendering"
                elif event.ui_element == quitButton:
                    quit()
            guiManager.process_events(event)
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