import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ""
import pygame
from sys import exit
from realtimeRenderer import *
from staticRenderer import *
from utilities import *
import pygame_gui as gui
import subprocess

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("3D Studio - Menu")
    clock = pygame.time.Clock()
    
    winWidth, winHeight = 810, 540
    window = pygame.display.set_mode((winWidth, winHeight))
    guiManager = gui.UIManager((winWidth, winHeight))
    bg_mainmenu = pygame.image.load("bg_mainmenu.png")
    bg_loadfile = pygame.image.load("bg_loadfile.png")

    runDemoButton = gui.elements.UIButton(relative_rect = pygame.Rect((155, 287), (100, 50)), text = "Run Demo", manager = guiManager)
    loadFileButton = gui.elements.UIButton(relative_rect = pygame.Rect((288, 287), (100, 50)), text = "Load File", manager = guiManager)
    openEditorButton = gui.elements.UIButton(relative_rect = pygame.Rect((422, 287), (100, 50)), text = "Open Editor", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((555, 287), (100, 50)), text = "Quit", manager = guiManager)
    loadButton = gui.elements.UIButton(relative_rect = pygame.Rect((158, 363), (100, 50)), text = "Load", manager = guiManager, visible = 0)
    returnButton = gui.elements.UIButton(relative_rect = pygame.Rect((292, 363), (100, 50)), text = "Return", manager = guiManager, visible = 0)

    fileInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((158, 193), (150, 50)), manager = guiManager, placeholder_text = "example.obj", visible = 0)
    sfInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((158, 278), (90, 50)), manager = guiManager, placeholder_text = "Scale: 0+", visible = 0)
    colourInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((244, 278), (115, 50)), manager = guiManager, placeholder_text = "Colour: FFFFFF", visible = 0)
    shineInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((355, 278), (90, 50)), manager = guiManager, placeholder_text = "Shine: 0-1", visible = 0)
    emissionInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((441, 278), (110, 50)), manager = guiManager, placeholder_text = "Emission: 0-1", visible = 0)
    
    uiInputData = {fileInput : "",
                   sfInput : "",
                   colourInput : "",
                   shineInput : "",
                   emissionInput : ""}
    
    state = "setup" #states: setup, editor, rendering
    background = bg_mainmenu
    demoMode = False
    objColour = normaliseRGB((255, 92, 0))
    objRtArgs = ["Triangle", 0, 0]
    while state == "setup":
        clock.tick()
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        window.blit(background, (0, 0))
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == runDemoButton:
                    # runDemoButton.kill()
                    demoMode = True
                    shapes = (0, 0)
                    state = "editor"
                elif event.ui_element == loadFileButton:
                    background = bg_loadfile
                    uiHide((runDemoButton, loadFileButton, openEditorButton))
                    quitButton.set_position((426, 363))
                    uiShow((fileInput, sfInput, colourInput, shineInput, emissionInput, loadButton, returnButton))
                elif event.ui_element == openEditorButton:
                    shapes = (0, 0)
                    state = "editor"
                elif event.ui_element == loadButton:
                    if isValidPositive(uiInputData[sfInput]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[shineInput]):
                        if uiInputData[fileInput].endswith(".obj") and isInDirectory(uiInputData[fileInput]):
                            shapes = (uiInputData[fileInput], float(uiInputData[sfInput]))
                            objColour = normaliseRGB(hexToRGB(uiInputData[colourInput]))
                            objRtArgs = ["Triangle", float(uiInputData[shineInput]), float(uiInputData[emissionInput])]
                            state = "editor"
                elif event.ui_element == returnButton:
                    background = bg_mainmenu
                    uiHide((fileInput, sfInput, colourInput, shineInput, emissionInput, loadButton, returnButton))
                    quitButton.set_position((555, 287))
                    uiShow((runDemoButton, loadFileButton, openEditorButton))
                elif event.ui_element == quitButton:
                    quit()
            if event.type == gui.UI_TEXT_ENTRY_CHANGED:
                uiInputData[event.ui_element] = event.text
            guiManager.process_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    baseCamX, baseCamY, baseCamZ = 0, 0, 1000
    polyGoal = 2000
    uiHide((runDemoButton, loadFileButton, openEditorButton, quitButton, loadButton, returnButton, fileInput, sfInput, colourInput, shineInput, emissionInput))

    count = 0
    focalLength = 300#300
    skyTint = (1,1,1.7) #standard 1,1,1.7, 1.5,1.3,1 #hex is 9696FF
    skyLight = 0.8
    globalTranslate = (85,0,0)
    rt = RealtimeRenderer(window, focalLength, baseCamX, baseCamY, baseCamZ, polyGoal, skyTint, skyLight, globalTranslate, demoMode)

    startTime = time.perf_counter()

    # objColour = normaliseRGB((255, 92, 0))
    # objRtArgs = ["Triangle", 0, 0]
    loadedObj = rt.load(shapes[0],shapes[1], objColour, objRtArgs)

    rt.update()

    pygame.display.set_caption("3D Studio - Editor")

    renderButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 37), (100, 50)), text = "Render", manager = guiManager)
    addSphereButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 103), (100, 50)), text = "Add Sphere", manager = guiManager)
    addTriangleButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 169), (100, 50)), text = "Add Triangle", manager = guiManager)
    editSkyButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 235), (100, 50)), text = "Edit Sky", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 456), (100, 50)), text = "Quit", manager = guiManager)

    centreInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((133, 103), (100, 50)), manager = guiManager, placeholder_text = "Centre: x,y,z", visible = 0)
    radiusInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((229, 103), (70, 50)), manager = guiManager, placeholder_text = "Radius:", visible = 0)
    colourInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((295,103), (115, 50)), manager = guiManager, placeholder_text = "Colour: FFFFFF", visible = 0)
    shineInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((406, 103), (90, 50)), manager = guiManager, placeholder_text = "Shine: 0-1", visible = 0)
    emissionInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((492, 103), (110, 50)), manager = guiManager, placeholder_text = "Emission: 0-1", visible = 0)
    addButton = gui.elements.UIButton(relative_rect = pygame.Rect((598, 103), (50, 50)), text = "Add", manager = guiManager, visible = 0)

    point1Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((133, 169), (105, 50)), manager = guiManager, placeholder_text = "Point 1: x,y,z", visible = 0)
    point2Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((234, 169), (105, 50)), manager = guiManager, placeholder_text = "Point 2: x,y,z", visible = 0)
    point3Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((335, 169), (105, 50)), manager = guiManager, placeholder_text = "Point 3: x,y,z", visible = 0)

    lightInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((244, 235), (90, 50)), manager = guiManager, placeholder_text = "Light: 0-1", visible = 0)
    updateButton = gui.elements.UIButton(relative_rect = pygame.Rect((330, 235), (70, 50)), text = "Update", manager = guiManager, visible = 0)

    uiInputData = {centreInput : "",
                   radiusInput : "",
                   colourInput : "",
                   shineInput : "",
                   emissionInput : "",
                   point1Input : "",
                   point2Input : "",
                   point3Input : "",
                   lightInput : ""}

    polygons = unnest(rt.setup(loadedObj))

    addingSphere = False
    addingTriangle = False
    editingSky = False

    while state == "editor":
        clock.tick()
        count += 1
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        rt.update()
        rt.render(polygons)
        pygame.draw.rect(window, (6, 6, 15), pygame.Rect(0, 0, 170, winHeight))
        
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                rt.focalLength += event.y * 20
                if rt.focalLength < 4:
                    rt.focalLength = 4 #prevents focal length from inverting (negative)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if rt.rotationLock:
                        rt.rotationLock = False
                    else:
                        rt.rotationLock = True
            if event.type == gui.UI_BUTTON_PRESSED:
                if event.ui_element == renderButton:
                    state = "rendering"
                elif event.ui_element == addSphereButton:
                    if addingSphere:
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                    else:
                        addingTriangle = False
                        editingSky = False
                        uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton, lightInput, updateButton))
                        colourInput.set_position((295, 103))
                        shineInput.set_position((406, 103))
                        emissionInput.set_position((492, 103))
                        addButton.set_position((598, 103))
                        uiShow((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                    addingSphere = not addingSphere
                elif event.ui_element == addTriangleButton:
                    if addingTriangle:
                        uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                    else:
                        addingSphere = False
                        editingSky = False
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton, lightInput, updateButton))
                        colourInput.set_position((436, 169))
                        shineInput.set_position((547, 169))
                        emissionInput.set_position((633, 169))
                        addButton.set_position((739, 169))
                        uiShow((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                    addingTriangle = not addingTriangle
                elif event.ui_element == addButton:
                    if addingSphere:
                        if isValidCoordinate(uiInputData[centreInput]) and isValidPositive(uiInputData[radiusInput]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[emissionInput]):
                            uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                            p = uiInputData[centreInput].split(",")
                            sphere = rt.getSphere(float(p[0]), 0 - float(p[1]), float(p[2]), float(uiInputData[radiusInput]),
                                                  normaliseRGB(hexToRGB(uiInputData[colourInput])),
                                                  float(uiInputData[shineInput]), float(uiInputData[emissionInput]))
                            polygons.append(sphere)
                            addingSphere = False
                    elif addingTriangle:
                        if isValidCoordinate(uiInputData[point1Input]) and isValidCoordinate(uiInputData[point2Input]) and isValidCoordinate(uiInputData[point3Input]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[emissionInput]):
                            uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                            p1 = uiInputData[point1Input].split(",")
                            p1[1] = 0 - float(p1[1])
                            p2 = uiInputData[point2Input].split(",")
                            p2[1] = 0 - float(p2[1])
                            p3 = uiInputData[point3Input].split(",")
                            p3[1] = 0 - float(p3[1])
                            triangle = rt.getTriangle(p1, p2, p3,
                                                      normaliseRGB(hexToRGB(uiInputData[colourInput])),
                                                      float(uiInputData[shineInput]), float(uiInputData[emissionInput]))
                            polygons.append(triangle)
                            addingTriangle = False
                elif event.ui_element == editSkyButton:
                    if editingSky:
                        uiHide((colourInput, lightInput, updateButton))
                    else:
                        addingSphere = False
                        addingTriangle = False
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton, point1Input, point2Input, point3Input, updateButton))
                        colourInput.set_position((133, 235))
                        uiShow((colourInput, lightInput, updateButton))
                    editingSky = not editingSky
                elif event.ui_element == updateButton:
                    if isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[lightInput]):
                        uiHide((colourInput, lightInput, updateButton))
                        rt.skyTint = normaliseRGB(tuple(1.7 * x for x in hexToRGB(uiInputData[colourInput])))
                        rt.skyLight = float(uiInputData[lightInput])
                        editingSky = False
                elif event.ui_element == quitButton:
                    quit()
            guiManager.process_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == gui.UI_TEXT_ENTRY_CHANGED:
                uiInputData[event.ui_element] = event.text
                
    renderInput = None
    resolutions = [(1280,720),
                   (640,360)]
    
    width, height = resolutions[1]
    windowSize = (960,540)

    pygame.display.set_caption("3D Studio - Rendering...")
    window = pygame.display.set_mode(windowSize)

    sr = StaticRenderer(width, height, (0,0,0), window, polygons, rt.skyTint, rt.skyLight)
    sr.render()
    subprocess.Popen(["explorer", "image.png"])