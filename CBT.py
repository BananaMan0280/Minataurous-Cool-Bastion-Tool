import tkinter as tk
from tkinter import filedialog
import PIL.Image
import PIL.ImageDraw
import PIL.ImageTk
import numpy as np
import PIL as PIL
import math
import os

'''
possiblilities for future updates
    file export
    change color pallete
    bastion field outlines
    city bastion support
    AI
'''

'''
Represents each individual block. Each block can be 1 of 4 things:
    -1 = skybridge
    0 = empty
    1 = vault bastion
    2 = city bastion
'''
class Block:
    def __init__(self, type, y):
        self.type = type
        self.yVal = y
        self.numFields = 0

'''
Contains the app as a whole
Structures the UI
As of now, it is planned to handle simulation, but that may change if needed
'''
class App:
    def __init__(self, window, width, height):
        # UI elements
        self.window = window

        self.canvasFrame = None
        self.canvas = None

        self.infoFrame = None

        self.fileInfo = None

        self.generalInfo = None

        self.specificInfo = None

        self.skybridgeInfo = None

        self.titleFont = ("Ariel", 17, "bold")
        self.font = ("Ariel", 12, "normal")

        #File info UI elements
        self.fileNameText = None
        self.sizeText = None

        #Bastion Layout info UI Elements
        self.bastionLayoutTitle = None
        self.currentYFrame = None
        self.currentYLabel = None
        self.currentYVal = None
        self.yValText = None
        self.numBastionsText = None
        self.modeSwitch = None
        self.modeLabel = None
        self.skybridgeButton = None
        self.bastionButton = None

        #selected block info UI Elements
        self.selectedBlockTitle = None
        self.coordinateFrame = None
        self.xText = None
        self.yText = None
        self.zText = None

        #skybridge info UI elements
        self.skybridgeTitle = None
        self.bastionsBrokenText = None
        self.manHoursText = None
        self.blocksText = None

        # colors
        self.COLOR_BG = (10, 10, 10)
        self.COLOR_GRID = (40, 40, 40)
        self.COLOR_FIELD = (170, 170, 170)
        self.COLOR_BASTION = (255, 255, 255)
        self.COLOR_CBASTION = (0, 255, 255)#currently unused
        self.COLOR_SKYBRIDGE = (255, 0, 0)

        # internal stuff
        self.cellsW = width
        self.cellsH = height
        self.cells = np.array([[Block(0, -63) for j in range(self.cellsW)] for i in range(self.cellsH)])
        self.saveStateCells = np.array([[Block(0, -63) for j in range(self.cellsW)] for i in range(self.cellsH)])
        self.placementYVal = -63
        self.skybridgeMode = False
        self.numBastions = 0
        self.numBastionsBroken = 0
        self.manHours = 0
        self.blocks = 0
        self.selectedBlock = [0, 0]

        self.fileName = "Untitled Layout.cbt"
        self.saved = True
        self.filePath = None


        self.initUI()

    def initUI(self):

        #pack frame for canvas and info frame in a grid, put canvas in center of canvas frame
        self.canvasFrame = tk.Frame(self.window, highlightthickness=4)
        self.infoFrame = tk.Frame(self.window, highlightthickness=6)

        self.canvasFrame.grid(row=0, column=0, sticky="nsew")
        self.infoFrame.grid(row=0, column=1, sticky="nsew")
        self.infoFrame.grid_columnconfigure(0, weight=1)
        self.infoFrame.grid_rowconfigure(0, weight=1)
        self.infoFrame.grid_rowconfigure(1, weight=2)
        self.infoFrame.grid_rowconfigure(2, weight=1)
        self.infoFrame.grid_rowconfigure(3, weight=2)

        self.canvas = tk.Canvas(self.canvasFrame, bg="Black")
        self.canvas.pack(fill="both", anchor="center", expand="true")
        self.canvas.bind('<Button>', self.onCanvasClick)
        self.canvas.bind('<Button-3>', self.onCanvasRightClick)

        #set up info frames
        self.fileInfo = tk.Frame(self.infoFrame, borderwidth=3, relief=tk.GROOVE)
        self.generalInfo = tk.Frame(self.infoFrame, borderwidth=3, relief=tk.GROOVE)
        self.specificInfo = tk.Frame(self.infoFrame, borderwidth=3, relief=tk.GROOVE)
        self.skybridgeInfo = tk.Frame(self.infoFrame, borderwidth=3, relief=tk.GROOVE)
        self.fileInfo.grid(row=0, column=0, sticky="nsew")
        self.generalInfo.grid(row=1, column=0, sticky="nsew")
        self.specificInfo.grid(row=2, column=0, sticky="nsew")
        self.skybridgeInfo.grid(row=3, column=0, sticky="nsew")

        #Setup file info widget
        self.fileInfo.grid_columnconfigure(0, weight=1)
        self.fileInfo.grid_rowconfigure(0, weight=1)
        self.fileInfo.grid_rowconfigure(1, weight=1)

        #file name
        self.fileNameText = tk.Label(self.fileInfo, text=self.fileName, font=self.titleFont)
        self.fileNameText.grid(row=0, column=0)

        #length x width
        self.sizeText = tk.Label(self.fileInfo, text=str(self.cellsW)+"x"+str(self.cellsH), font=self.font)
        self.sizeText.grid(row=1, column=0)

        #Setup canvas info widget
        self.generalInfo.grid_columnconfigure(0, weight=1)
        self.generalInfo.grid_rowconfigure(0, weight=2)
        self.generalInfo.grid_rowconfigure(1, weight=1)
        self.generalInfo.grid_rowconfigure(2, weight=1)
        self.generalInfo.grid_rowconfigure(3, weight=1)

        #section title
        self.bastionLayoutTitle = tk.Label(self.generalInfo, text="Bastion Layout", anchor="n", font=self.titleFont)
        self.bastionLayoutTitle.grid(column=0, row=0)

        #enter ylevel thing
        self.currentYFrame = tk.Frame(self.generalInfo)
        self.currentYFrame.grid_rowconfigure(0, weight=1)
        self.currentYFrame.grid_columnconfigure(0, weight=1)
        self.currentYFrame.grid_columnconfigure(1, weight=1)
        self.currentYFrame.grid(column=0, row=1)

        self.currentYLabel = tk.Label(self.currentYFrame, text="Current Y Value: ", anchor="e", font=self.font)
        self.currentYLabel.grid(row=0, column=0, sticky="e")

        self.yValText = tk.StringVar()
        self.currentYVal = tk.Entry(self.currentYFrame, textvariable=self.yValText)
        self.currentYVal.bind("<Return>", self.setYVal)
        self.currentYVal.grid(row=0, column=1, sticky="ew")
        self.currentYVal.insert(0, self.placementYVal)

        #number of bastions
        self.numBastionsText = tk.Label(self.generalInfo, text="Number of Bastions: "+str(self.numBastions), anchor="ne", font=self.font)
        self.numBastionsText.grid(column=0, row=2)

        #mode switch
        self.modeSwitch = tk.Frame(self.generalInfo)
        self.modeSwitch.grid_rowconfigure(0, weight=1)
        self.modeSwitch.grid_columnconfigure(0, weight=1)
        self.modeSwitch.grid_columnconfigure(1, weight=1)
        self.modeSwitch.grid_columnconfigure(2, weight=1)
        self.modeSwitch.grid(column=0, row=3)

        self.modeLabel = tk.Label(self.modeSwitch, text="Mode: ", anchor="e", font=self.font)
        self.modeLabel.grid(row=0, column=0, sticky="e")

        self.bastionButton = tk.Button(self.modeSwitch, text="Bastion", command=self.switchMode, state="disabled")
        self.bastionButton.grid(row=0, column=1, sticky="nsew")

        self.skybridgeButton = tk.Button(self.modeSwitch, text="Skybridge", command=self.switchMode)
        self.skybridgeButton.grid(row=0, column=2, sticky="nsew")

        #Setup selected block widget
        self.specificInfo.columnconfigure(0, weight=1)
        self.specificInfo.rowconfigure(0, weight=2)
        self.specificInfo.rowconfigure(1, weight=1)

        #title
        self.selectedBlockTitle = tk.Label(self.specificInfo, text="Selected Block", anchor="n", font=self.titleFont)
        self.selectedBlockTitle.grid(row=0, column=0)

        #coordinates
        self.coordinateFrame = tk.Frame(self.specificInfo)
        self.coordinateFrame.rowconfigure(0, weight=1)
        self.coordinateFrame.columnconfigure(0, weight=1)
        self.coordinateFrame.columnconfigure(1, weight=1)
        self.coordinateFrame.columnconfigure(2, weight=1)
        self.coordinateFrame.grid(row=1, column=0)

        #X
        self.xText = tk.Label(self.coordinateFrame, text="X: "+str(self.selectedBlock[0]), font=self.font)
        self.xText.grid(row=0, column=0)

        #Y
        self.yText = tk.Label(self.coordinateFrame, text="Y: "+str(self.cells[self.selectedBlock[0], self.selectedBlock[1]].yVal), font=self.font)
        self.yText.grid(row=0, column=1)

        #Z
        self.zText = tk.Label(self.coordinateFrame, text="Z: "+str(self.selectedBlock[1]), font=self.font)
        self.zText.grid(row=0, column=2)

        #Setup skybridge info widget
        self.skybridgeInfo.columnconfigure(0, weight=1)
        self.skybridgeInfo.rowconfigure(0, weight=2)
        self.skybridgeInfo.rowconfigure(1, weight=1)
        self.skybridgeInfo.rowconfigure(2, weight=1)
        self.skybridgeInfo.rowconfigure(3, weight=1)

        #section title
        self.skybridgeTitle = tk.Label(self.skybridgeInfo, text="Skybridge", anchor="n", font=self.titleFont)
        self.skybridgeTitle.grid(row=0, column=0)

        #Bastions broken
        self.bastionsBrokenText = tk.Label(self.skybridgeInfo, text="Bastions Broken: " + str(self.numBastionsBroken), font=self.font)
        self.bastionsBrokenText.grid(row=1, column=0)

        #Manhours
        self.manHoursText = tk.Label(self.skybridgeInfo, text="Manhours: " + str(self.manHours), font=self.font)
        self.manHoursText.grid(row=2, column=0)

        #Blocks
        self.blocksText = tk.Label(self.skybridgeInfo, text="Blocks Placed: " + str(self.blocks), font=self.font)
        self.blocksText.grid(row=3, column=0)
    
    def onCanvasClick(self, event):
        cellW = self.canvas.winfo_width() / self.cellsW
        cellH = self.canvas.winfo_height() / self.cellsH
        pos = [math.floor(event.x / cellW), math.floor(event.y / cellH)]
        self.cells[pos[1], pos[0]].yVal = self.placementYVal
        if not self.skybridgeMode:
            if self.cells[pos[1], pos[0]].type != 1:
                self.cells[pos[1], pos[0]].type = 1
                self.updateFields(pos[1], pos[0])
                self.numBastions += 1
                self.numBastionsText.configure(text="Number of Bastions: "+str(self.numBastions))
            else:
                self.cells[pos[1], pos[0]].type = 0
                self.updateFields(pos[1], pos[0])
                self.numBastions -= 1
                self.numBastionsText.configure(text="Number of Bastions: "+str(self.numBastions))
        else:
            self.cells[pos[1], pos[0]].type = -1
            self.checkFields(pos[1], pos[0], self.placementYVal)
            self.blocks += 1
            self.blocksText.configure(text="Blocks Placed: "+str(self.blocks))
        
        self.selectedBlock = pos
        self.xText.configure(text="X: "+str(self.selectedBlock[0]))
        self.zText.configure(text="Z: "+str(self.selectedBlock[1]))
        self.yText.configure(text="Y: "+str(self.cells[self.selectedBlock[0], self.selectedBlock[1]].yVal))

        self.fileNameText.configure(text=self.fileName+"*")
        self.saved = False
        self.update(event)

    def onCanvasRightClick(self, event):
        cellW = self.canvas.winfo_width() / self.cellsW
        cellH = self.canvas.winfo_height() / self.cellsH
        self.selectedBlock = [math.floor(event.x / cellW), math.floor(event.y / cellH)]

        #reconfigure text
        self.xText.configure(text="X: "+str(self.selectedBlock[0]))
        self.zText.configure(text="Z: "+str(self.selectedBlock[1]))
        self.yText.configure(text="Y: "+str(self.cells[self.selectedBlock[0], self.selectedBlock[1]].yVal))

    def onScroll(self, event):
        #handle linux or windows
        if event.num == 5 or event.delta == -120:
            self.placementYVal -= 1
        if event.num == 4 or event.delta == 120:
            self.placementYVal += 1
        
        if self.placementYVal < -63:
            self.placementYVal = 319
        elif self.placementYVal > 319:
            self.placementYVal = -63
        
        self.currentYVal.delete(0, tk.END)
        self.currentYVal.insert(0, self.placementYVal)

    def setYVal(self, event):
        newY = int(self.yValText.get())

        if newY < -63:
            newY = -63
        elif newY > 319:
            newY = 319
        self.placementYVal = newY

        self.currentYVal.delete(0, tk.END)
        self.currentYVal.insert(0, self.placementYVal)
        self.window.focus_set()

    def switchMode(self, event=None):
        if self.skybridgeMode:
            for y in range(self.cellsW - 1):
                for x in range(self.cellsH - 1):
                    self.cells[x,y].type = self.saveStateCells[x,y].type
                    self.cells[x,y].yVal = self.saveStateCells[x,y].yVal
                    self.cells[x,y].numFields = self.saveStateCells[x,y].numFields
            self.skybridgeButton.config(state="normal")
            self.bastionButton.config(state="disabled")
        else:
            for y in range(self.cellsW - 1):
                for x in range(self.cellsH - 1):
                    self.saveStateCells[x,y].type = self.cells[x,y].type
                    self.saveStateCells[x,y].yVal = self.cells[x,y].yVal
                    self.saveStateCells[x,y].numFields = self.cells[x,y].numFields
            self.skybridgeButton.config(state="disabled")
            self.bastionButton.config(state="normal")
        
        self.skybridgeMode = not self.skybridgeMode

        self.blocks = 0
        self.blocksText.configure(text="Blocks Placed: "+str(self.blocks))
        self.numBastionsBroken = 0
        self.bastionsBrokenText.configure(text="Bastions Broken: "+str(self.numBastionsBroken))
        self.manHours = 0
        self.manHoursText.configure(text="Manhours: "+str(self.manHours))
        
        self.update(1)

    def update(self, event):
        #this is the method that draws all the blocks
        #originally, this was done with rectangles in the canvas which was slow as fuck
        #now it creates a single image and uses the canvas to display that
        #takes unused event parameter so it can be called on resize without hassle, just throw something random in there

        self.canvas.delete('all')# delete old image
        cellImage = PIL.Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), self.COLOR_GRID)
        draw = PIL.ImageDraw.Draw(cellImage)
        cellW = self.canvas.winfo_width()/self.cellsW
        cellH = self.canvas.winfo_height()/self.cellsH
        for row, col in np.ndindex(self.cells.shape):
            color = self.COLOR_BG 
            if self.cells[row, col].type == 0:
                if self.cells[row, col].numFields > 0:
                    color = self.COLOR_FIELD
            elif self.cells[row, col].type < 0:
                color = self.COLOR_SKYBRIDGE
            elif self.cells[row,col].type == 2:
                color = self.COLOR_CBASTION
            else:
                color = self.COLOR_BASTION
            draw.rectangle([(col*cellW) + 1, (row*cellH) + 1, (col*cellW) + cellW - 1, (row*cellH) + cellH - 1], fill=color)
        displayImage = PIL.ImageTk.PhotoImage(cellImage)
        self.canvas.create_image(0, 0, image=displayImage, anchor=tk.NW)
        self.canvas.image = displayImage
    
    def updateFields(self, row, col):
        if self.cells[row, col].type == 1:
            for x in range(-10, 11):
                for y in range(-10, 11):
                    if (0 <= row + x <= self.cellsH - 1) and (0 <= col + y <= self.cellsW - 1):
                        self.cells[row + x, col + y].numFields += 1
        else:
            for x in range(-10, 11):
                for y in range(-10, 11):
                    if (0 <= row + x <= self.cellsH - 1) and (0 <= col + y <= self.cellsW - 1):
                        self.cells[row + x, col + y].numFields -= 1
    
    def checkFields(self, row, col, yVal, recursive=False):
        if self.cells[row, col].numFields > 0:
            for x in range(-10, 11):
                for y in range(-10, 11):
                    if (0 <= row + x <= self.cellsH - 1) and (0 <= col + y <= self.cellsW - 1):
                        if self.cells[row + x, col + y].type == 1 and yVal >= self.cells[row + x, col + y].yVal:
                            self.cells[row + x, col + y].type = 0
                            self.updateFields(row + x, col + y)
                            self.numBastionsBroken += 1
                            self.bastionsBrokenText.configure(text="Bastions Broken: "+str(self.numBastionsBroken))
                            if not recursive:
                                self.checkFields(row + x, col + y, self.cells[row + x, col + y].yVal, recursive=True)
                                self.manHours += 1
                                self.manHoursText.configure(text="Manhours: "+str(self.manHours))
    
    def newFile(self, width, height, name="Untitled Layout.cbt"):
        self.cellsW = width
        self.cellsH = height
        self.cells = np.array([[Block(0, -63) for j in range(self.cellsW)] for i in range(self.cellsH)])
        self.saveStateCells = np.array([[Block(0, -63) for j in range(self.cellsW)] for i in range(self.cellsH)])
        self.placementYVal = -63
        self.skybridgeMode = False
        self.numBastions = 0
        self.numBastionsBroken = 0
        self.manHours = 0
        self.blocks = 0
        self.selectedBlock = [0, 0]

        self.fileName = name
        self.saved = True
        self.filePath = None

    def saveFile(self, event=0):
        if self.filePath == None:
            self.saveFileAs()
            return

        fileWriter = open(self.filePath, mode='w')
        
        fileWriter.write(str(self.cellsW)+"\n"+str(self.cellsH)+"\n")
        if self.skybridgeMode == False:
            for row in range (self.cellsH):
                for col in range (self.cellsW):
                    fileWriter.write(str(self.cells[row, col].type)+"/"+str(self.cells[row, col].yVal)+" ")
                if row < self.cellsH - 1:
                    fileWriter.write("\n")
        else:
            for row in range (self.cellsH):
                for col in range (self.cellsW):
                    fileWriter.write(str(self.saveStateCells[row, col].type)+"/"+str(self.saveStateCells[row, col].yVal)+" ")
                if row < self.cellsH - 1:
                    fileWriter.write("\n")

        fileWriter.close()

        self.fileNameText.configure(text=self.fileName)
        self.saved = True
    
    def saveFileAs(self):
        tester = tk.filedialog.asksaveasfilename(title="Save Bastion Layout", filetypes=[("Bastion Layout Files", "*.cbt"), ("All Files", "*.*")], initialfile=self.fileName, defaultextension="*.cbt")
        if tester == "" or tester == None:
            return

        self.filePath = tester

        fileWriter = open(self.filePath, mode='w')
        
        #write to file, first two lines contain array size, rest are "blocktype/yval" for each cell

        fileWriter.write(str(self.cellsW)+"\n"+str(self.cellsH)+"\n")
        if self.skybridgeMode == False:
            for row in range (self.cellsH):
                for col in range (self.cellsW):
                    fileWriter.write(str(self.cells[row, col].type)+"/"+str(self.cells[row, col].yVal)+" ")
                if row < self.cellsH - 1:
                    fileWriter.write("\n")
        else:
            for row in range (self.cellsH):
                for col in range (self.cellsW):
                    fileWriter.write(str(self.saveStateCells[row, col].type)+"/"+str(self.saveStateCells[row, col].yVal)+" ")
                if row < self.cellsH - 1:
                    fileWriter.write("\n")

        fileWriter.close()

        self.fileName = (os.path.basename(self.filePath))
        self.fileNameText.configure(text=self.fileName)

        self.fileNameText.configure(text=self.fileName)
        self.saved = True

    def importFile(self):
        cbtFile = tk.filedialog.askopenfilename(title="Import Bastion Layout", filetypes=[("Bastion Layout Files", "*.cbt")])
        fileReader = open(file=cbtFile, mode='r')

        #set up new cells of right size
        newW = int(fileReader.readline().strip("\n"))
        newH = int(fileReader.readline().strip("\n"))
        name = os.path.basename(cbtFile)
        self.newFile(newW, newH, name=name)

        #fill cells

        #create 2d array of file contents(contains the \n char because I'm stupid, just ignore it lol)
        textArray = []#I forgor how to do np arrays, but this thing is a local variable that doesn't last for long so I'll just stick with the jank as fuck syntax
        for line in fileReader.readlines():
            textArray.append(line.split(" "))

        for row in range(self.cellsH):
            for col in range(self.cellsW):
                cellInfo = textArray[row][col].split("/")
                self.cells[row, col].type = int(cellInfo[0])
                self.cells[row, col].yVal = int(cellInfo[1])

                if int(cellInfo[0]) == 1:
                    self.updateFields(row, col)
        
        self.update(1)

#in all honesty, I got so fed up with front end development that I made perplexity ai do most of this function for me
#same goes for all other popups lol
def newFileDialog(window, app):
    # Create a new top-level window
    popup = tk.Toplevel(window)
    popup.title("New File")
    popup.geometry("300x200")
    popup.resizable(False, False)

    # Create and pack the input fields
    tk.Label(popup, text="Canvas Width:", font=app.font).pack(pady=5)
    width_entry = tk.Entry(popup)
    width_entry.insert(0, str(app.cellsW))
    width_entry.pack()

    tk.Label(popup, text="Canvas Height:", font=app.font).pack(pady=5)
    height_entry = tk.Entry(popup)
    height_entry.insert(0, str(app.cellsH))
    height_entry.pack()

    tk.Label(popup, text="File Name:", font=app.font).pack(pady=5)
    filename_entry = tk.Entry(popup)
    filename_entry.insert(0, "Untitled Layout")
    filename_entry.pack()

    # Function to handle the OK button click
    def on_ok():
        width = width_entry.get()
        height = height_entry.get()
        filename = filename_entry.get()
        
        # Validate inputs
        if width.isdigit() and height.isdigit() and filename:
            popup.result = (int(width), int(height), filename)
            popup.destroy()
            app.newFile(int(width), int(height), filename+".cbt")
            app.fileNameText.configure(text=app.fileName)
            app.sizeText.configure(text=str(app.cellsW)+"x"+str(app.cellsH))
        else:
            tk.messagebox.showerror("Error", "Please enter valid width, height, and filename.")

    # Create and pack the OK button
    ok_button = tk.Button(popup, text="OK", command=on_ok)
    ok_button.pack(pady=10)

    # Wait for the popup to be closed
    popup.wait_window()

def about(window, app):
    # Create a new top-level window
    about_window = tk.Toplevel(window)
    about_window.title("About")
    about_window.geometry("600x400")
    about_window.resizable(False, False)

    # Create a frame to hold the content
    main_frame = tk.Frame(about_window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Add a title
    title_label = tk.Label(main_frame, text="Minataurous' Cool Bastion Tool", font=app.titleFont)
    title_label.pack(pady=(0, 10))

    # Add version information
    version_label = tk.Label(main_frame, text="Version 1.0", font=app.font)
    version_label.pack()

    # Add a description
    description_text = """
    This is a tool for creating bastion layouts.
    It was designed by minataurous of Snowpeak for free public use.
    If you paid for this tool you were scammed!
    The only obligation that comes with the tool is that you must include the Snowpeak flag somewhere in some form in any piece of defense infra this tool(directly or indirectly) helps to design.

    I have more ideas for things to add, so if you would like to see the continued development of this tool, send me a kind message or a tip:
    minataurous - @bananaman0280 - u/NearbyTone1341
    HS-2174
    """
    description_label = tk.Label(main_frame, text=description_text, wraplength=500, justify="center", font=app.font)
    description_label.pack(pady=(10, 0))

    # Add copyright information
    copyright_label = tk.Label(main_frame, text="© 2024 Snowpeak Software")
    copyright_label.pack(side="bottom", pady=(20, 0))

    # Add an OK button to close the window
    ok_button = tk.Button(main_frame, text="OK", command=about_window.destroy)
    ok_button.pack(side="bottom", pady=(20, 0))

def help(window, app):
    # Create a new top-level window
    about_window = tk.Toplevel(window)
    about_window.title("About")
    about_window.geometry("600x450")
    about_window.resizable(False, False)

    # Create a frame to hold the content
    main_frame = tk.Frame(about_window)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Add a title
    title_label = tk.Label(main_frame, text="Controls", font=app.titleFont)
    title_label.pack(pady=(0, 10))

    # Add a description
    description_text = """
    Left click anywhere on the grid to place a vault bastion.
    Left click a vault bastion to remove it.
    Right click a cell to select it.
    Press space or use the sidebar to switch to skybridge mode.
    When you switch back to bastion mode from skybridge mode, your work will be set back to how it was before the skybridge.
    While in skybridge mode, the tool automatically keeps track of how many bastions are broken, and how many manhours that would take to accomplish on live.
    Use the scrollwheel or sidebar to set the Y value at which you place bastions and skybridge blocks.
    The window can be resized, but make it too small and things break until you make it bigger again, so beware.
    There is currently no way to zoom in.
    Use the file dropdown menu to save, load, and create new files.
    Saving can also be done with ctrl+s.
    """
    description_label = tk.Label(main_frame, text=description_text, wraplength=500, justify="center", font=app.font)
    description_label.pack()

    # Add an OK button to close the window
    ok_button = tk.Button(main_frame, text="OK", command=about_window.destroy)
    ok_button.pack(side="bottom", pady=(20))


def main():
    Window = tk.Tk()
    Window.title("Minataurous' Cool Bastion Tool")
    ico = PIL.Image.open("CBTIcon.png")
    photo = PIL.ImageTk.PhotoImage(ico)
    Window.wm_iconphoto(True, photo)

    Window.geometry("1600x800")
    Window.grid_columnconfigure(0, weight=3)
    Window.grid_columnconfigure(1, weight=1)
    Window.grid_rowconfigure(0, weight=1)
    app = App(Window, 100, 100)

    #setup menubar
    menuBar = tk.Menu(Window)
    fileMenu = tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="New", command=lambda w=Window, a=app: newFileDialog(w, a))
    fileMenu.add_command(label="Save", command=app.saveFile)
    fileMenu.add_command(label="Save As", command=app.saveFileAs)
    fileMenu.add_command(label="Load", command=app.importFile)
    fileMenu.add_separator()
    fileMenu.add_command(label="Quit", command=Window.quit)
    menuBar.add_cascade(label="File", menu=fileMenu)

    menuBar.add_command(label="About", command=lambda w=Window, a=app: about(w, a))
    menuBar.add_command(label="Help", command=lambda w=Window, a=app: help(w, a))

    Window.config(menu=menuBar)

    Window.bind('<Configure>', app.update)
    Window.bind('<space>', app.switchMode)
    #bind scrollwheel for windows and linux
    # with Windows OS
    Window.bind("<MouseWheel>", app.onScroll)
    # with Linux OS
    Window.bind("<Button-4>", app.onScroll)
    Window.bind("<Button-5>", app.onScroll)

    Window.bind("<Control-s>", app.saveFile)
    Window.mainloop()

if __name__ == '__main__':
    main()