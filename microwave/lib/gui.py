# Based on "Digital Watch GUI" OCT 2008 by Reehan Shaikh reehan.shaikh@cs.mcgill.ca

import tkinter
from tkinter.constants import BOTH, NO
import os
MODULE_PATH = os.path.dirname(__file__)

from . import audio


CANVAS_W = 520
CANVAS_H = 348

TIME_X0 = 412
TIME_Y0 = 90
TIME_X1 = 472
TIME_Y1 = 106

BUTTON_HEIGHT = 18
BUTTON_X0 = 412
BUTTON_X1 = 472

START_X0 = BUTTON_X0
START_Y0 = 234
START_X1 = BUTTON_X1
START_Y1 = START_Y0 + BUTTON_HEIGHT

STOP_X0 = BUTTON_X0
STOP_Y0 = 211
STOP_X1 = BUTTON_X1
STOP_Y1 = STOP_Y0 + BUTTON_HEIGHT

INCTIME_X0 = BUTTON_X0
INCTIME_Y0 = 188
INCTIME_X1 = BUTTON_X1
INCTIME_Y1 = INCTIME_Y0 + BUTTON_HEIGHT

DOOR_X0 = 26
DOOR_Y0 = 68
DOOR_X1 = 379
DOOR_Y1 = 285

FONT_TIME = ("terminal", 14)

class GUI(tkinter.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.imgClosedOff = tkinter.PhotoImage(file=MODULE_PATH+"/small_closed_off.png")
        self.imgClosedOn = tkinter.PhotoImage(file=MODULE_PATH+"/small_closed_on.png")
        self.imgOpenedOff = tkinter.PhotoImage(file=MODULE_PATH+"/small_opened_off.png")
        self.imgOpenedOn = tkinter.PhotoImage(file=MODULE_PATH+"/small_opened_on.png")

        # state
        self.doorOpened = False
        self.running = False
        
        self.lastPressed = ""
                
        self.pack()
        self.canvas = tkinter.Canvas(master=self,
                             takefocus=1,
                             width=CANVAS_W, height=CANVAS_H,
                             background="black")
    
        self.canvas.pack(fill=BOTH, expand=1)
        self.canvas.focus_set()

        self.background = self.canvas.create_image(0, 0, image=self.imgClosedOff, anchor="nw")

        self.rects = [
            (START_X0, START_X1, START_Y0, START_Y1, "START"),
            (STOP_X0, STOP_X1, STOP_Y0, STOP_Y1, "STOP"),
            (INCTIME_X0, INCTIME_X1, INCTIME_Y0, INCTIME_Y1, "INCTIME"),
            (DOOR_X0, DOOR_X1, DOOR_Y0, DOOR_Y1, "DOOR"),
        ]

        self.timeTag = self.canvas.create_text(
            TIME_X1-16, TIME_Y0+7,
            font=FONT_TIME, justify="center", fill="#0f0", text="0")

        self.canvas.bind("<ButtonPress-1>", self.mouse1Click)
        self.canvas.bind("<ButtonRelease-1>", self.mouse1Release)
        
        parent.protocol("WM_DELETE_WINDOW", self.window_close)

    def mouse1Click(self, event):

        def handle(what):
            if what == "START":
                self.send_event("start_pressed")
                self.lastPressed = "start_pressed"
            elif what == "STOP":
                self.send_event("stop_pressed")
                self.lastPressed = "stop_pressed"
            elif what == "INCTIME":
                self.send_event("increase_time_pressed")
                self.lastPressed = "increase_time_pressed"
            elif what == "DOOR":
                self.doorOpened = not self.doorOpened
                if self.doorOpened:
                    self.send_event("door_opened")
                else:
                    self.send_event("door_closed")
                self.refresh_background()
                self.lastPressed = ""
            else:
                self.lastPressed = ""

        X = self.canvas.canvasx(event.x)
        Y = self.canvas.canvasy(event.y)

        for X0, X1, Y0, Y1, what in self.rects:
            if X >= X0 and X <= X1 and Y >= Y0 and Y <= Y1:
                handle(what)
                break
    
    def mouse1Release(self, event):
        if self.lastPressed == "start":
            # self.send_event("releasedStart")
            pass
        elif self.lastPressed == "stop":
            # self.send_event("releasedStop")
            pass
        elif self.lastPressed == "increase_time":
            # self.send_event("releasedIncTime")
            pass
        self.lastPressed = ""

    def refresh_background(self):
        if self.doorOpened:
            if self.running:
                self.canvas.itemconfig(self.background, image=self.imgOpenedOn)
            else:
                self.canvas.itemconfig(self.background, image=self.imgOpenedOff)
        else:
            if self.running:
                self.canvas.itemconfig(self.background, image=self.imgClosedOn)
            else:
                self.canvas.itemconfig(self.background, image=self.imgClosedOff)

        # play or stop sound
        if self.running:
            audio.play_running()
        else:
            audio.stop_running()

    def handle_event(self, event, param):
        if event == "turn_magnetron_on":
            self.running = True
            self.refresh_background()
        elif event == "turn_magnetron_off":
            self.running = False
            self.refresh_background()
        elif event == "set_displayed_time":
            self.setTime(param)
        elif event == "ring_bell":
            audio.play_bell()
                             
    def setTime(self, time: int):
        self.canvas.itemconfig(self.timeTag, text=str(time))

    def window_close(self):
        import sys
        sys.exit(0)
        self.send_event('GUIQuit')
