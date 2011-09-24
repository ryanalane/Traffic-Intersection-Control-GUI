# This GUI has been designed and developed by Ryan Lane. The algorithm for the Intersection.Automatic() method was developed by Ryan Lane, Sumit Nair, Johnathan Barone, and Guoxin Li.


from Tkinter import *
import time
import isec

color_bank = {"green":'#067302',"yellow":'#D2D914',"red":'#D92B04', "sensor": '#D98E04', 'switch':'#686E75','switch_hover':'#9BAAC1','streets':'#150517',"background":'dark grey'}

class Light():
    def __init__(self,Intersection,name,sensor_orientation,intersection_center_x,intersection_center_y):
        self.root = Intersection.root
        self.intersection_number = Intersection.intersection_number
        self.Canvas = Intersection.Canvas
        self.light_name = name
        self.sensor_orientation = sensor_orientation
        if sensor_orientation == "up":
            center_x = intersection_center_x
            sensor_center_x = intersection_center_x
            center_y = intersection_center_y - 40
            sensor_center_y = intersection_center_y - 70
        elif sensor_orientation == "down":
            center_x = intersection_center_x
            sensor_center_x = intersection_center_x
            center_y = intersection_center_y + 40
            sensor_center_y = intersection_center_y + 70
        elif sensor_orientation == "left":
            center_x = intersection_center_x - 40
            sensor_center_x = intersection_center_x - 70
            center_y = intersection_center_y   
            sensor_center_y = intersection_center_y
        elif sensor_orientation == "right":
            center_x = intersection_center_x + 40
            sensor_center_x = intersection_center_x + 70
            center_y = intersection_center_y
            sensor_center_y = intersection_center_y
        self.center = {"x":center_x,"y":center_y}
        self.sensor_center = {"x":sensor_center_x,"y":sensor_center_y}
        self.drawLight()
        self.drawSensor()
    
    def drawLight(self):
        x = self.center["x"]
        y = self.center["y"]
        self.gui = self.Canvas.create_oval(x-15,y-15,x+15,y+15, fill="", outline="black")

    def drawSensor(self):
        x = self.sensor_center["x"]
        y = self.sensor_center["y"]
        self.sensor = self.Canvas.create_oval(x-7,y-7,x+7,y+7, fill="", outline="")
        
    def turnLight(self,switch,color):
        color_letter = None
        if color == "green":
            color_letter = 'G'
        elif color == "yellow":
            color_letter = 'Y'
        elif color == "red":
            color_letter = 'R'
        if switch == "on":
            self.Canvas.itemconfig(self.gui,fill=color_bank[color])
            if self.light_name != "C" and self.light_name != "D":
                isec.light_on(self.intersection_number,self.light_name+color_letter)
        elif switch == "off":
            if self.light_name != "C" and self.light_name != "D":
                isec.light_off(self.intersection_number,self.light_name+color_letter)
        self.root.update()
                
    def turnSensor(self,switch):
        if switch == 'on':
            self.Canvas.itemconfig(self.sensor,fill=color_bank["sensor"])
        elif switch == 'off':
            self.Canvas.itemconfig(self.sensor,fill="")
        
    def checkSensor(self):
        result = None
        if isec.sense(self.intersection_number,self.light_name+'1') == True:
            self.turnSensor('on')
            result = True
        elif isec.sense(self.intersection_number,self.light_name+'1') == False:
            self.turnSensor('off')
            result = False
        return result

class Intersection():
    def __init__(self,root,parent_canvas,square,intersection_number):
        self.root = root
        self.Canvas = parent_canvas
        self.square = square
        self.intersection_number = intersection_number
        self.Lights = {}       
    
    def buildIntersection(self):
        light_orientations = {"A":self.square["orientation"],"B":None,"C":None,"D":None}
        x = self.square["x"]
        y = self.square["y"]
        if light_orientations["A"] == 'up':
            light_orientations["B"] = 'right'
            light_orientations["C"] = 'down'
            light_orientations["D"] = 'left'
        elif light_orientations["A"] == 'down':
            light_orientations["B"] = 'left'
            light_orientations["C"] = 'up'
            light_orientations["D"] = 'right'
        elif light_orientations["A"] == 'left':
            light_orientations["B"] = 'up'
            light_orientations["C"] = 'right'
            light_orientations["D"] = 'down'
        elif light_orientations["A"] == 'right':
            light_orientations["B"] = 'down'
            light_orientations["C"] = 'left'
            light_orientations["D"] = 'up'
        for i in light_orientations:
            if i != "D" or self.square["number_of_lights"] == 4:
                self.Lights[i] = Light(self,i,light_orientations[i],x,y)
        self.switch_gui = self.Canvas.create_rectangle(x-17,y-17,x+17,y+17,fill=color_bank["switch"], outline = "black")
        self.Canvas.tag_bind(self.switch_gui, "<Button-1>", lambda dummy: self.bumpState())
        self.Canvas.tag_bind(self.switch_gui, "<Enter>", lambda dummy: self.Canvas.itemconfig(self.switch_gui,fill=color_bank["switch_hover"]))
        self.Canvas.tag_bind(self.switch_gui, "<Leave>", lambda dummy: self.Canvas.itemconfig(self.switch_gui,fill=color_bank["switch"]))
        
        self.currentState = 0
        self.moveGUIToState(self.currentState)
    
    def bumpState(self):
        if self.currentState != 3:
            self.currentState += 1
        else:
            self.currentState = 0
        self.moveGUIToState(self.currentState)    
    
    def moveGUIToState(self,newState):
        if newState == 0:
            self.Lights["B"].turnLight('off','yellow')
            self.Lights["B"].turnLight('on','red')
            if self.square["number_of_lights"] == 4:
                self.Lights["D"].turnLight('off','yellow')
                self.Lights["D"].turnLight('on','red')
            time.sleep(0.75)
            self.Lights["A"].turnLight('off','red')
            self.Lights["A"].turnLight('on','green')
            self.Lights["C"].turnLight('off','red')
            self.Lights["C"].turnLight('on','green')
        elif newState == 1:
            self.Lights["A"].turnLight('off','green')
            self.Lights["A"].turnLight('on','yellow')
            self.Lights["C"].turnLight('off','green')
            self.Lights["C"].turnLight('on','yellow')
        if newState == 2:
            self.Lights["A"].turnLight('off','yellow')
            self.Lights["A"].turnLight('on','red')
            self.Lights["C"].turnLight('off','yellow')
            self.Lights["C"].turnLight('on','red')
            time.sleep(0.75)
            self.Lights["B"].turnLight('off','red')
            self.Lights["B"].turnLight('on','green')
            if self.square["number_of_lights"] == 4:
                self.Lights["D"].turnLight('off','red')
                self.Lights["D"].turnLight('on','green')
        elif newState == 3:
            self.Lights["B"].turnLight('off','green')
            self.Lights["B"].turnLight('on','yellow')
            if self.square["number_of_lights"] == 4:
                self.Lights["D"].turnLight('off','green')
                self.Lights["D"].turnLight('on','yellow')
    
    def checkSensors(self):
        call_for_light_change = False
        wait_a_bit = False
        for i in self.Lights:
            result = self.Lights[i].checkSensor()
            if (i == "A" or i == "C") and result == True:
                wait_a_bit = True
            elif (i == "B" or i == "D") and result == True:
                call_for_light_change = True
        return [call_for_light_change,wait_a_bit]
   
    def smart_sleep(self,wait_time):
    # This method checks the auto/manual state so as to quicken the program's response time to user input.
        for i in range(wait_time*2):
            if self.currentMode == "auto":
                time.sleep(0.5)
            else:
                break
   
    def Manual(self):
        self.currentMode = "manual"    
    
    def Automatic(self):
        self.currentMode = "automatic"
        if self.currentState == 1 or self.currentState == 3:
                self.ChangeLights(1,1.5)
        if self.currentMode == "automatic":
            sensor_status = self.checkSensors()
            if self.currentState == 0 and sensor_status[0] == True:
        	      if sensor_status[1] == True:
        	          self.smart_sleep(3)
        	      self.ChangeLights(2,1.5)
            if self.currentState == 2:
                self.root.update() # This keeps the Automatic/Manual button from remaining in the depressed state during time.sleep().
                self.smart_sleep(3)
                
                self.ChangeLights(2,1.5)
                time.sleep(1)
        
    def ChangeLights(self,repeats,wait_time):
        self.checkSensors()
        # if AC is Green, then go through the light changes to end up with BD-Green
        if self.currentState == 0:
           self.bumpState()
        elif self.currentState == 1:
           self.bumpState()
           time.sleep(0.5)
        # if AC is Green, then go through the light changes to end up with BD-Green
        elif self.currentState == 2:
           self.bumpState()
        elif self.currentState == 3:
           self.bumpState()
           time.sleep(0.5)
        isec.print_lights()
        self.root.update()
        time.sleep(wait_time)
        if repeats != 1:
            self.ChangeLights(repeats-1,wait_time)

class TrafficGUI(Frame):

    def __init__(self,master=None):
        Frame.__init__(self,master)
        self.master.title("Traffic System Control - Honors Contract Design")
        self.grid(padx=20,pady=20)
        self.resetIntersections()
        self.createLaunchScreen()
        
        isec.simulate_hardware = True
        isec.hw_init()
        #isec.hw_init(simulate_hardware = False)
        
    def createLaunchScreen(self):
        self.Quit = Button(self, text="Quit", command=self.destroy)
        self.Quit.grid(row=0,column=2,sticky=E)
        self.TopText = Label(self, text="Click the squares to activate the intersections.")
        self.TopText.grid(row=0,column=0,sticky=E)
        self.Clear = Label(self, text="(Clear them)",fg="dark gray")
        self.Clear.bind("<Enter>",lambda dummy:self.Clear.config(fg="dark red"))
        self.Clear.bind("<Leave>",lambda dummy:self.Clear.config(fg="dark gray"))
        self.Clear.bind("<Button-1>",lambda dummy:self.ClearSquares())
        self.Clear.grid(row=0,column=1,sticky=W)
        
        self.Activate = Button(self, text="Activate Traffic System", command=self.ActivateTrafficSystem)
        self.Activate.grid(row=2,columnspan=2)
        
        self.Canvas = Canvas(self, width=700,height=700,background=color_bank["background"])
        self.Canvas.grid(row=1,columnspan=2,padx=50)
        
        self.generateSquareStructures()
        self.loadSquareGUIs(reset=False)
    
    def generateSquareStructures(self):
        # This function populates Square Data
        centers_x = [350,90,350,610,350]
        centers_y = [90,350,350,350,610]
        orientations = ['right','up','up','down','left']
        number_of_lights = [3,3,4,3,3]
        self.squares = []
        for i in range(len(centers_x)):
            square_info = {"id":i,"x":centers_x[i],"y":centers_y[i],"orientation":orientations[i],"number_of_lights":number_of_lights[i],"gui":None,"label":None,"label_window":None}
            self.squares.append(square_info)
    
    def loadSquareGUIs(self,reset):
        for i, square in enumerate(self.squares):
            if reset == False:
	              x = square["x"]
	              y = square["y"]
	              square["gui"] = self.Canvas.create_rectangle(x-60,y-60,x+60,y+60,fill=color_bank["background"],dash=15, dashoffset=5, outline ="white", width=3)
            else:
	              self.Canvas.itemconfig(square["gui"], fill="dark gray", dash=15, dashoffset=5, outline="white")
	              self.Canvas.delete(square["label_window"])
            if i == 0:
                self.Canvas.tag_bind(square["gui"], "<Button-1>", lambda dummy: self.registerIntersection(self.squares[0]))
            elif i == 1:
                self.Canvas.tag_bind(square["gui"], "<Button-1>", lambda dummy: self.registerIntersection(self.squares[1]))
            elif i == 2:
                self.registerIntersection(self.squares[2])
            elif i == 3:
                self.Canvas.tag_bind(square["gui"], "<Button-1>", lambda dummy: self.registerIntersection(self.squares[3]))
            elif i == 4:
                self.Canvas.tag_bind(square["gui"], "<Button-1>", lambda dummy: self.registerIntersection(self.squares[4]))
        
    def ClearSquares(self):
        self.resetIntersections()
        self.loadSquareGUIs(reset=True)  
    
    def registerIntersection(self,square):
        if square["id"] != 2:
            intersection_number = self.intersection_queue.next()
            self.Canvas.tag_unbind(square["gui"], "<Button-1>")
        else:
            intersection_number = 1
        self.Intersections[intersection_number] = Intersection(self,self.Canvas,square,intersection_number)
        
        self.Canvas.itemconfig(square["gui"], fill="white", outline="black", dash=1)
        
        self.squares[square["id"]]["label"] = Label(self, text=str(intersection_number),font=('Helvetica',48),bg="white")
        self.squares[square["id"]]["label_window"] = self.Canvas.create_window(square["x"],square["y"],window=square["label"])
        
    def resetIntersections(self):
        intersection_range = range(2,6)
        self.intersection_queue = iter(intersection_range)
        self.Intersections = {}        

    def drawRoads(self):
        self.Canvas.create_rectangle(73,73,627,627,fill=color_bank["streets"],outline="black")
    
        self.Canvas.create_rectangle(107,107,333,333,fill=color_bank["background"],outline="black")
        self.Canvas.create_rectangle(367,107,593,333,fill=color_bank["background"],outline="black")
        self.Canvas.create_rectangle(107,367,333,593,fill=color_bank["background"],outline="black")
        self.Canvas.create_rectangle(367,367,593,593,fill=color_bank["background"],outline="black")
        
        
        self.Canvas.create_rectangle(90,90,610,610,fill="",outline=color_bank["yellow"],dash=10)
        self.Canvas.create_rectangle(350,90,610,350,fill="",outline=color_bank["yellow"],dash=10)
        self.Canvas.create_rectangle(90,350,350,610,fill="",outline=color_bank["yellow"],dash=10)
        
        self.update()
        
    def ActivateTrafficSystem(self):
        for square in self.squares:
            self.Canvas.delete(square['gui'])
            self.Canvas.delete(square['label_window'])
        self.Activate.grid_remove()
        self.TopText.grid_remove()
        self.Clear.grid_remove()
        self.BottomText = Label(self, text="Click the centers of the the intersections to change lights while in \"Manual.\"",fg="dark red",font=('Helvetica',18))
        self.BottomText.grid(row=2,columnspan=2)
        
        self.mode_var = IntVar()
        self.ManualButton = Radiobutton(self, text="Manual", variable=self.mode_var, value="manual", command=self.toggleMode)
        self.ManualButton.select()
        self.ManualButton.grid(row=0,column=0,sticky=E)
        self.AutomaticButton = Radiobutton(self, text="Automatic", variable=self.mode_var, value="automatic", command=self.toggleMode)
        self.AutomaticButton.grid(row=0,column=1,sticky=W)
        self.drawRoads()
        for i in self.Intersections:
            self.Intersections[i].buildIntersection()
        self.mode = "manual"
        self.update()
        self.Manual()

    def toggleMode(self):
        if self.mode == "manual":
            self.mode = "automatic"
            self.Automatic()
        elif self.mode == "automatic":
            self.mode = "manual"
            self.Manual()
        
    def Manual(self):
        for i in self.Intersections:
            self.Intersections[i].Manual()
        while self.mode == "manual":
            for i in self.Intersections:
                self.Intersections[i].checkSensors()
                self.update()
            for i in range(8):
                time.sleep(0.0625)
                self.update()
    
    def Automatic(self):
        while self.mode == "automatic":
            self.update()
            for i in self.Intersections:
                self.Intersections[i].checkSensors()
                self.Intersections[i].Automatic()
            for i in range(8):
                time.sleep(0.0625)
                self.update()

if __name__ == "__main__":
    TrafficApp = TrafficGUI()
    TrafficApp.mainloop()