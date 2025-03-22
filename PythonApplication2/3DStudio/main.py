# import necessary modules
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "" # hide pygame support prompt
import pygame
from sys import exit
import pygame_gui as gui
import pickle
from PIL import Image
# import custom renderers
from realtimeRenderer import RealtimeRenderer
from staticRenderer import StaticRenderer
# import custom utility functions and structures
from utilities import *

if __name__ == "__main__":
    # initialise pygame and set up main menu window
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption("3D Studio - Menu")
    clock = pygame.time.Clock()
    
    winWidth, winHeight = 810, 540
    window = pygame.display.set_mode((winWidth, winHeight))
    guiManager = gui.UIManager((winWidth, winHeight))

    # load background images
    bg_mainmenu = pygame.image.load("bg_mainmenu.png")
    bg_loadfile = pygame.image.load("bg_loadfile.png")

    # create main menu buttons
    runDemoButton = gui.elements.UIButton(relative_rect = pygame.Rect((155, 287), (100, 50)),
                                          text = "Run Demo", manager = guiManager)
    loadFileButton = gui.elements.UIButton(relative_rect = pygame.Rect((288, 287), (100, 50)),
                                           text = "Load File", manager = guiManager)
    openEditorButton = gui.elements.UIButton(relative_rect = pygame.Rect((422, 287), (100, 50)),
                                             text = "Open Editor", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((555, 287), (100, 50)),
                                       text = "Quit", manager = guiManager)
    loadButton = gui.elements.UIButton(relative_rect = pygame.Rect((158, 363), (100, 50)),
                                       text = "Load", manager = guiManager, visible = 0)
    returnButton = gui.elements.UIButton(relative_rect = pygame.Rect((292, 363), (100, 50)),
                                         text = "Return", manager = guiManager, visible = 0)

    # create main menu input fields
    fileInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((158, 193), (150, 50)),
                                            manager = guiManager, placeholder_text = ".obj or .txt", visible = 0)
    sfInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((158, 278), (90, 50)),
                                          manager = guiManager, placeholder_text = "Scale: 0+", visible = 0)
    colourInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((244, 278), (115, 50)),
                                              manager = guiManager, placeholder_text = "Colour: FFFFFF", visible = 0)
    shineInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((355, 278), (90, 50)),
                                             manager = guiManager, placeholder_text = "Shine: 0-1", visible = 0)
    emissionInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((441, 278), (110, 50)),
                                                manager = guiManager, placeholder_text = "Emission: 0-1", visible = 0)
    
    # create dictionary to store input data for all fields
    uiInputData = {fileInput : "",
                   sfInput : "",
                   colourInput : "",
                   shineInput : "",
                   emissionInput : ""}
    
    # set initial state
    state = "setup"
    background = bg_mainmenu
    demoMode = False
    objColour = (0, 0, 0) # default object colour
    objRtArgs = ["Triangle", 0, 0] # default rendering arguments

    #main menu loop
    while state == "setup":
        clock.tick()
        time_delta = clock.tick(60)/1000.0 # delta time for frame updates
        window.fill("black")

        window.blit(background, (0, 0)) #draw background image
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        
        pygame.display.flip() # update display

        for event in pygame.event.get():
            if event.type == gui.UI_BUTTON_PRESSED: # handle button events
                if event.ui_element == runDemoButton:
                    # enter into editor with demo mode active
                    demoMode = True
                    shapes = (0, 0)
                    polygons = []
                    state = "editor"

                elif event.ui_element == loadFileButton:
                    # proceed to load file screen
                    background = bg_loadfile
                    uiHide((runDemoButton, loadFileButton, openEditorButton))
                    quitButton.set_position((426, 363))
                    uiShow((fileInput, sfInput, colourInput, shineInput, emissionInput, loadButton, returnButton))

                elif event.ui_element == openEditorButton:
                    # open editor with empty shape array
                    shapes = (0, 0)
                    state = "editor"
                    polygons = []

                elif event.ui_element == loadButton:
                    # validate inputs
                    if uiInputData[fileInput].endswith(".obj") and isInDirectory(uiInputData[fileInput]):
                        # load object
                        if isValidPositive(uiInputData[sfInput]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[shineInput]):
                            shapes = (uiInputData[fileInput], float(uiInputData[sfInput]))
                            objColour = normaliseRGB(hexToRGB(uiInputData[colourInput]))
                            # define object as being made up of triangles, with given renderer arguments
                            objRtArgs = ["Triangle", float(uiInputData[shineInput]), float(uiInputData[emissionInput])]
                            state = "editor"
                    elif uiInputData[fileInput].endswith(".txt") and isInDirectory(uiInputData[fileInput]):
                        # load scene data from binary file
                        try: 
                            save = open(uiInputData[fileInput], "rb")
                            polygons = pickle.load(save)
                            shapes = (0, 0)
                            state = "editor"
                        except:
                            pass

                elif event.ui_element == returnButton:
                    # return to main menu screen
                    background = bg_mainmenu
                    uiHide((fileInput, sfInput, colourInput, shineInput, emissionInput, loadButton, returnButton))
                    quitButton.set_position((555, 287))
                    uiShow((runDemoButton, loadFileButton, openEditorButton))

                elif event.ui_element == quitButton:
                    # close the program
                    quit()

            if event.type == gui.UI_TEXT_ENTRY_CHANGED:
                # update input dictionary with up to date text, stripped of whitespace
                uiInputData[event.ui_element] = event.text.replace(" ", "")

            if event.type == pygame.QUIT:
                # close the program
                pygame.quit()
                exit()

            # handle pygame_gui events
            guiManager.process_events(event)

    uiHide((runDemoButton, loadFileButton, openEditorButton, quitButton, loadButton,
            returnButton, fileInput, sfInput, colourInput, shineInput, emissionInput))

    pygame.display.set_caption("3D Studio - Editor")

    # create editor buttons
    renderButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 276), (100, 50)),
                                         text = "Render", manager = guiManager)
    addSphereButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 103), (100, 50)),
                                            text = "Add Sphere", manager = guiManager)
    addTriangleButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 169), (100, 50)),
                                              text = "Add Triangle", manager = guiManager)
    editSkyButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 37), (100, 50)),
                                          text = "Edit Sky", manager = guiManager)
    saveAsButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 390), (100, 50)),
                                         text = "Save As", manager = guiManager)
    quitButton = gui.elements.UIButton(relative_rect = pygame.Rect((37, 456), (100, 50)),
                                       text = "Quit", manager = guiManager)
    undoButton = gui.elements.UIButton(relative_rect = pygame.Rect((650, 456), (50, 50)),
                                       text = "Undo", manager = guiManager)
    redoButton = gui.elements.UIButton(relative_rect = pygame.Rect((725, 456), (50, 50)),
                                       text = "Redo", manager = guiManager)
    addButton = gui.elements.UIButton(relative_rect = pygame.Rect((598, 103), (50, 50)),
                                      text = "Add", manager = guiManager, visible = 0)
    updateButton = gui.elements.UIButton(relative_rect = pygame.Rect((330, 37), (70, 50)),
                                         text = "Update", manager = guiManager, visible = 0)
    saveButton = gui.elements.UIButton(relative_rect = pygame.Rect((249, 390), (50, 50)),
                                       text = "Save", manager = guiManager, visible = 0)

    # create editor entry fields
    centreInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((133, 103), (100, 50)),
                                              manager = guiManager, placeholder_text = "Centre: x,y,z", visible = 0)
    radiusInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((229, 103), (70, 50)),
                                              manager = guiManager, placeholder_text = "Radius:", visible = 0)
    colourInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((295,103), (115, 50)),
                                              manager = guiManager, placeholder_text = "Colour: FFFFFF", visible = 0)
    shineInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((406, 103), (90, 50)),
                                             manager = guiManager, placeholder_text = "Shine: 0-1", visible = 0)
    emissionInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((492, 103), (110, 50)),
                                                manager = guiManager, placeholder_text = "Emission: 0-1", visible = 0)
    point1Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((133, 169), (105, 50)),
                                              manager = guiManager, placeholder_text = "Point 1: x,y,z", visible = 0)
    point2Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((234, 169), (105, 50)),
                                              manager = guiManager, placeholder_text = "Point 2: x,y,z", visible = 0)
    point3Input = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((335, 169), (105, 50)),
                                              manager = guiManager, placeholder_text = "Point 3: x,y,z", visible = 0)
    lightInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((244, 37), (90, 50)),
                                             manager = guiManager, placeholder_text = "Light: 0-1", visible = 0)
    saveFileInput = gui.elements.UITextEntryBox(relative_rect = pygame.Rect((133, 390), (120, 50)),
                                                manager = guiManager, placeholder_text = "Filename: .txt", visible = 0)
    resolutionSelect = gui.elements.UIDropDownMenu(options_list = ["1280x720", "960x540", "640x360", "320x180"], starting_option = "640x360",
                                                   relative_rect = pygame.Rect((37, 235), (100, 25)), manager = guiManager, visible = 1)

    # dictionary to store input data for all fields
    uiInputData = {centreInput : "",
                   radiusInput : "",
                   colourInput : "",
                   shineInput : "",
                   emissionInput : "",
                   point1Input : "",
                   point2Input : "",
                   point3Input : "",
                   lightInput : "",
                   saveFileInput : "",
                   resolutionSelect : "640x360"}

    # set up real-time renderer parameters with default values
    baseCamPos = Vect(0, 0, 1000)
    polyGoal = 2000
    focalLength = 300
    skyTint = (1,1,1.7) #standard 1,1,1.7, 1.5,1.3,1 #hex is 9696FF
    skyLight = 0.8
    globalTranslate = (85,0,0)

    # initialise real-time renderer
    rt = RealtimeRenderer(window, focalLength, baseCamPos, polyGoal, skyTint, skyLight, globalTranslate, demoMode)

    # load object and store as a variable
    loadedObj = rt.load(shapes[0], shapes[1], objColour, objRtArgs)
    
    rt.update()

    # if object has been loaded, update polygons array
    if loadedObj != 0 or polygons == []:
        polygons = unnest(rt.setup(loadedObj))

    addingSphere = False
    addingTriangle = False
    editingSky = False
    savingAs = False

    # initialise stacks for undo/redo functionality
    undoStack = Stack()
    redoStack = Stack()

    # editor loop
    while state == "editor":
        clock.tick()
        time_delta = clock.tick(60)/1000.0
        window.fill("black")

        # update renderer attributes and render scene
        rt.update()
        rt.render(polygons)
        
        # draw menu
        pygame.draw.rect(window, (6, 6, 15), pygame.Rect(0, 0, 170, winHeight))
        guiManager.update(time_delta)
        guiManager.draw_ui(window)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.MOUSEWHEEL:
                rt.focalLength += event.y * 20 # adjust focal length (zoom) with mouse scroll
                if rt.focalLength < 4:
                    rt.focalLength = 4 # prevents negative focal length

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
                    # update ui elements accordingly
                    if addingSphere:
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                    else:
                        addingTriangle = False
                        editingSky = False
                        savingAs = False
                        uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput,
                                addButton, lightInput, updateButton, saveFileInput, saveButton))
                        colourInput.set_position((295, 103))
                        shineInput.set_position((406, 103))
                        emissionInput.set_position((492, 103))
                        addButton.set_position((598, 103))
                        uiShow((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                    addingSphere = not addingSphere

                elif event.ui_element == addTriangleButton:
                    # update ui elements accordingly
                    if addingTriangle:
                        uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                    else:
                        addingSphere = False
                        editingSky = False
                        savingAs = False
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton, lightInput,
                                updateButton, saveFileInput, saveButton))
                        colourInput.set_position((436, 169))
                        shineInput.set_position((547, 169))
                        emissionInput.set_position((633, 169))
                        addButton.set_position((739, 169))
                        uiShow((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                    addingTriangle = not addingTriangle

                elif event.ui_element == addButton:
                    if addingSphere:
                        # validate inputs
                        if isValidCoordinate(uiInputData[centreInput]) and isValidPositive(uiInputData[radiusInput]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[emissionInput]):
                            uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton))
                            p = uiInputData[centreInput].split(",") # get coordinates from input
                            # get sphere object from given data
                            sphere = rt.getSphere(Vect(float(p[0]), 0 - float(p[1]), float(p[2])), float(uiInputData[radiusInput]),
                                                  normaliseRGB(hexToRGB(uiInputData[colourInput])),
                                                  float(uiInputData[shineInput]), float(uiInputData[emissionInput]))
                            # add sphere object to shape array
                            polygons.append(sphere)
                            # push action to the undo stack
                            undoStack.push(sphere)
                            addingSphere = False

                    elif addingTriangle:
                        # validate inputs
                        if isValidCoordinate(uiInputData[point1Input]) and isValidCoordinate(uiInputData[point2Input]) and isValidCoordinate(uiInputData[point3Input]) and isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[shineInput]) and isValidSmallDec(uiInputData[emissionInput]):
                            uiHide((point1Input, point2Input, point3Input, colourInput, shineInput, emissionInput, addButton))
                            # get coordinates from inputs
                            p1 = uiInputData[point1Input].split(",")
                            p2 = uiInputData[point2Input].split(",")
                            p3 = uiInputData[point3Input].split(",")
                            # get triangle object from given data
                            triangle = rt.getTriangle(Vect(float(p1[0]), 0 - float(p1[1]), float(p1[2])),
                                                      Vect(float(p2[0]), 0 - float(p2[1]), float(p2[2])),
                                                      Vect(float(p3[0]), 0 - float(p3[1]), float(p3[2])),
                                                      normaliseRGB(hexToRGB(uiInputData[colourInput])),
                                                      float(uiInputData[shineInput]), float(uiInputData[emissionInput]))
                            # add triangle to shape array
                            polygons.append(triangle)
                            # push action to the undo stack
                            undoStack.push(triangle)
                            addingTriangle = False

                elif event.ui_element == editSkyButton:
                    # update ui elements accordingly
                    if editingSky:
                        uiHide((colourInput, lightInput, updateButton))
                    else:
                        addingSphere = False
                        addingTriangle = False
                        savingAs = False
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton,
                                point1Input, point2Input,point3Input, updateButton, saveFileInput, saveButton))
                        colourInput.set_position((133, 37))
                        uiShow((colourInput, lightInput, updateButton))
                    editingSky = not editingSky

                elif event.ui_element == updateButton:
                    # validate inputs
                    if isValidHexCode(uiInputData[colourInput]) and isValidSmallDec(uiInputData[lightInput]):
                        uiHide((colourInput, lightInput, updateButton))
                        # update renderer environment information with given data
                        rt.skyTint = normaliseRGB(tuple(1.7 * x for x in hexToRGB(uiInputData[colourInput])))
                        rt.skyLight = float(uiInputData[lightInput])
                        editingSky = False

                elif event.ui_element == saveAsButton:
                    # update ui elements accordingly
                    if savingAs:
                        uiHide((saveFileInput, saveButton))
                    else:
                        uiHide((centreInput, radiusInput, colourInput, shineInput, emissionInput, addButton,
                                point1Input, point2Input, point3Input, updateButton, lightInput, updateButton))
                        uiShow((saveFileInput, saveButton))
                    savingAs = not savingAs

                elif event.ui_element == saveButton:
                    # validate input
                    if uiInputData[saveFileInput].endswith(".txt"):
                        try:
                            # write scene data to the given binary file
                            save = open(uiInputData[saveFileInput], "wb")
                            pickle.dump(polygons, save)
                        except:
                            pass
                        uiHide((saveFileInput, saveButton))
                        savingAs = False

                elif event.ui_element == undoButton:
                    # pop last action from the undo stack, carry out action, push to redo stack
                    if undoStack.hasData():
                        action = undoStack.pop()
                        if action is not None:
                            polygons.remove(action)
                        redoStack.push(action)

                elif event.ui_element == redoButton:
                    # pop last action from the redo stack, carry out action, push to undo stack
                    if redoStack.hasData():
                        action = redoStack.pop()
                        if action is not None:
                            polygons.append(action)
                        undoStack.push(action)

                elif event.ui_element == quitButton:
                    # exit the program
                    quit()
            
            if event.type == gui.UI_TEXT_ENTRY_CHANGED or event.type == gui.UI_DROP_DOWN_MENU_CHANGED:
                # update dictionary of input data with input stripped of whitespace
                uiInputData[event.ui_element] = event.text.replace(" ", "")

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            # handle pygame_gui events
            guiManager.process_events(event)

    # set rendering resolution to user selection
    width, height = uiInputData[resolutionSelect].split("x")
    windowSize = (960,540)

    # set window for rendering
    pygame.display.set_caption("3D Studio - Rendering...")
    window = pygame.display.set_mode(windowSize)

    # initialise static renderer and render the final image
    sr = StaticRenderer(int(width), int(height), (0,0,0), window, polygons, rt.skyTint, rt.skyLight)
    sr.render()

    # open rendered image
    img = Image.open("image.png")
    img.show()