import os, math, lib, __builtin__
import sys
import threading
from Tkinter import *
from time import sleep, time as now
from _3dlib import *
from testlib import *
from lib.baselib import BaseControl
from lib.thread import TkThread

# class Control(threading.Thread):
class Control(BaseControl):

    gui = None
    NAME = "Control"
    stopped = False
    objs = {}
    # delay = 22.3 / (30.0**2)
    # delay = 0.034
    # delay = 0.067
    delay = 1 / 30.0
    scale = 10
    visor =  [5, -10, 5]
    visor_rot = [0, 0, 0]
    visor_disp = [0, 0, 0]
    visorchanged = True
    rots = [0.032, {0:0, 1:0, 2:0}]
    movs = [16, {0:0,1:0,2:0}]
    cur_ob = 0 #current object
    available_time = 0

    def __init__(self, Main):
        # threading.Thread.__init__(self)
        BaseControl.__init__(self, Main)
        # self.gui = Main
        self.tkthread = TkThread(self)
        self.tkthread.noVerbose()
        self.tkthread.start()

    def delete(self, code):
        if code >= 0:
            self.gui.mc.delete(code)
        else:
            print "OMIT"

    def update(self, none = None):
        # self.gui.after_idle(self.gui.update)
        # self.gui.mc.update()
        pass

    def ObjFromFile(self, path, color = "blue", rotate = True, name = "", scale=1.0):
        ob0file = open(path,"rb")
        ob0 = Volume([], [], name=name or ("ob"+str(self.cur_ob)), color=color)
        self.objs[ob0.name] = ob0
        self.cur_ob+=1
        # scale = 1.0
        verts = []
        for l in ob0file:
            dt = l.strip().split(" ")
            if dt[0] == "v":
                verts.append( [ float(d)  for d in dt[1:] if d ] )

            elif dt[0] == "f":
                vs = [
                    d.split("/")[0]
                    for d in dt[1:]
                ]
                ob0.addFace( tuple( [ int(float(s)) for s in vs ] ) )
        min_z = 0
        max_z = 0
        min_y = 0
        max_y = 0

        for v in verts:
            if(v[2] < min_z ):
                min_z = v[2]
            elif(v[2] > max_z ):
                max_z = v[2]
            if(v[1] < min_y ):
                min_y = v[1]
            elif(v[1] > max_y ):
                max_y = v[1]

        scale = ( (max_z - min_z) if \
                ( (max_z - min_z ) > (max_y - min_y) ) else \
                  (max_y - min_y) ) / 5.0 * 1 / float(scale)
        print ob0.name, scale, min_y, max_y, min_z, max_z
        for v in verts:
            ob0.addVert( tuple( float(d) / scale + ( 5.0 if i < 2 else 0.0 )
                         for i, d in enumerate(v) ) )
        ob0file.close()
        if(rotate):
            ob0.rotate( [ ( (5, 5, 0), (math.pi / 2.0, 0, 0) ) ] )

    def main(self):
        print 1
        # sys.stdout = open("stdout","wb")
        # sys.stderr = open("stderr","wb")
        self.scale = self.gui.w / 10.0
        self.visor = [s for s in self.scaled(self.visor)]
        center = ( 5, 1, 5 )
        print "scale:", self.scale

        sys.stdout.flush()
        
        cube = Volume(
            [
                (1, 1, 1),
                (1, 1, 2),
                (1, 2, 1),
                (1, 2, 2),
                (2, 1, 1),
                (2, 1, 2),
                (2, 2, 1),
                (2, 2, 2)
                ],
            [
                ( 1, 3, 4, 2 ),
                ( 5, 7, 8, 6 ),
                ( 1, 5, 6, 2 ),
                ( 3, 7, 8, 4 ),
                ( 2, 6, 8, 4 ),
                ( 1, 5, 7, 3 ),
            ] , name="cube0", color="blue")

        pyramid = Volume(
                [
                    ( 3  , 1  , 1 ),
                    ( 3.5, 1.5, 3 ),
                    ( 3.5, 2  , 1 ),
                    ( 4  , 1  , 1 )
                    ],
                [
                    ( 1, 2, 3 ),
                    ( 1, 2, 4 ),
                    ( 1, 3, 4 ),
                    ( 2, 3, 4 )
                    ],
                name="pyr0", color="red"
            )

        grid = Volume([], [], name="grid0", color="gray")
        for x in xrange(10):
            for y in xrange(10):
                grid.addVert( (x, y, 1) )

        for x in xrange(9):
            for y in xrange(9):
                grid.addFace(
                        (
                            2+x*10+y,
                            1+x*10+y,
                            1+(x+1)*10+y,
                            2+(x+1)*10+y
                            )
                    )
        
        # self.ObjFromFile("./MinoanColumnA_OBJ/MinoanColumnA_Low.obj", color="yellow", name="column")
        # self.ObjFromFile("./palm/palm1_LOD.obj", "green", rotate = True, name="palm")
        self.ObjFromFile("./Gta-spano-2010 obj/Gta-spano-2010 obj.obj", "blue", rotate = True, name="car",scale=2.0)
        # self.ObjFromFile("./L200-OBJ/L200-OBJ/L200-OBJ.obj", "blue", rotate = True, name="car",scale=1.0)
        self.objs["cube0"] = cube
        self.objs["pyr0"] = pyramid
        # self.objs["grid0"] = grid

        sys.stdout.flush()

        self.objs["cube0"].rotate(
                [
                    (
                        (5.0, 5.0, 0),
                        ( 
                            0,
                            0,
                            1.0
                            )
                        )
                    ]
            )
                            # -math.pi / 2.0 * 1.5

        self.rePaint()
        cnt = 0
        cnt2 = 0
        init = now()
        step = 1.0 / self.delay

        while (not(self.stopped)):

            t0 = now()
            if(not(self.stopped)):

                for r in self.rots[1]:
                    if(self.rots[1][r]):
                        self.visor_rot[r] += self.rots[0]*self.rots[1][r]

                for m in self.movs[1]:
                    if(self.movs[1][m]):
                        if(m == 0):
                            self.visor_disp[m] += self.movs[0]*self.movs[1][m]*math.cos(self.visor_rot[2])
                        elif(m == 1):
                            self.visor_disp[m] += self.movs[0]*self.movs[1][m]*math.cos(self.visor_rot[2])
                        else:
                            self.visor_disp[m] += self.movs[0]*self.movs[1][m]
                    
                # self.objs["car"].rotate(
                #     [

                #         (center, (
                #                     0,
                #                     0,
                #                     0
                #                     )

                #             ),
                #         (center, (
                #                     0,
                #                     0,
                #                     2.0*math.pi / 300.0
                #                     )
                #             )
                #         ]
                #     )

                # self.objs["car"].rotate(
                self.tkthread.after_idle(
                        self.objs["car"].rotate,
                        [
                            (
                                (5.0, 5.0, 0),
                                ( 
                                    0,
                                    0,
                                    2.0*math.pi / step / 10.0
                                    )
                                )
                            ]
                    )
                                    # 2.0*math.pi / 300.0
                self.available_time = self.delay - now() + t0
                if(self.available_time > 0):
                    self.rePaint()
                else:
                    print "OMIT BY TIME"

            try: self.gui.sl.config(text="fps: " + str(round(cnt2 / (max((now() - init), 1)), 1)))
            except TclError:
                print "error 0x04", sys.exc_info()
                pass
            cnt += 1
            cnt2 += 1
            if(not(cnt % 600)):
                cnt2 = 0
                init = now()

            delay = self.delay - now() + t0

            sys.stdout.flush()
            sleep(max(0.0, delay))

    def rePaint(self):

        _waserror = False
        for obname in self.objs:
            if(not(self.stopped)):
                obj = self.objs[obname]
                if(self.visorchanged or obj.changed):
                    try:
                        # self.gui.mc.delete(*self.gui.mc.find_withtag(obj.name))
                        pass
                    except (ValueError, TclError) as e:
                        _waserror = True
                        print "error 0x03", sys.exc_info()#, [dir(e) for e in sys.exc_info()], dir(sys.exc_info()[2].tb_frame), sys.exc_info()[2].tb_lasti, sys.exc_info()[2].tb_next
                    else:
                        paintObj(obj, self)
                        obj.noChanges()
        if(not(_waserror)):
            self.visorchanged = False

    def scaled(self, v):
        if(type(v) == list)and(type(v[0])==tuple):
            return [
                tuple( [ c * self.scale for c in ve] )
                for ve in v
            ]
        else:
            return tuple( [c * self.scale for c in v] )

    def unScaled(self, v):
        if(type(v) == list):
            return [
                tuple( [ c / float(self.scale) for c in ve] )
                for ve in v
            ]
        else:
            return tuple( [c / float(self.scale) for c in v] )

    def keyStart(self, e):

        
        if(e.keysym == "Left"): # left

            self.rots[1][2] = -1

        elif(e.keysym == "Up"): # up

            self.rots[1][0] = 1

        elif(e.keysym == "Right"): # right

            self.rots[1][2] = 1

        elif(e.keysym == "Down"): # down

            self.rots[1][0] = -1
        elif(e.char.lower() == "a"):

            self.movs[1][0] = 1
        elif(e.char.lower() == "w"):

            self.movs[1][1] = -1
        elif(e.char.lower() == "d"):

            self.movs[1][0] = -1
        elif(e.char.lower() == "s"):

            self.movs[1][1] = 1
        elif(e.char.lower() == "e"):

            self.movs[1][2] = -1
        elif(e.char.lower() == "c"):

            self.movs[1][2] = 1

        self.visorchanged = True

    def keyEnd(self, e):

        if(e.keysym == "Left"): # left

            self.rots[1][2] = 0

        elif(e.keysym == "Up"): # up

            self.rots[1][0] = 0

        elif(e.keysym == "Right"): # right

            self.rots[1][2] = 0

        elif(e.keysym == "Down"): # down

            self.rots[1][0] = 0
        elif(e.char.lower() == "a"):

            self.movs[1][0] = 0
        elif(e.char.lower() == "w"):

            self.movs[1][1] = 0
        elif(e.char.lower() == "d"):

            self.movs[1][0] = 0
        elif(e.char.lower() == "s"):

            self.movs[1][1] = 0
        elif(e.char.lower() == "e"):

            self.movs[1][2] = 0
        elif(e.char.lower() == "c"):

            self.movs[1][2] = 0

    def mouseCamera(self, e):

        midx = self.gui.w / 2.0
        midz = self.gui.h / 2.0
        rotz = math.pi/2.0 * ( (e.x - midx) / float(midx) )
        rotx = math.pi/2.0 * ( (e.y - midz) / float(midz) ) * (1 - abs(rotz / math.pi * 2.0))
        roty = (rotx + rotz) / 2.0

        self.visor_rot[0] = rotx
        self.visor_rot[1] = roty * 0.16
        self.visor_rot[2] = rotz
        self.visorchanged = True

    # def stop(self):
    #     self.stopped = True

    #     self.gui.destroy()
    #     print "stop"

__builtin__.Control = Control
reload(lib.baselib)
GUI = lib.baselib.GUI
class Main(GUI):

    w = 0
    h = 0
    x = 0
    y = 0
    control = None
    main_frame = None
    mc = None # main canvas
    SIZE = 1
    use_mouse = False

    def __init__(self):
        # Tk.__init__(self)
        GUI.__init__(self)
        # self.b = back = Control(self)
        self.w = 1024  if self.SIZE == 0 else 1920
        # self.h =  768  if self.SIZE == 0 else 1080
        self.h =  768  if self.SIZE == 0 else 960

    # def start(self):
    #     self.protocol("WM_DELETE_WINDOW", self.control.stop)
    #     self.bind("<Key>", self.control.keyStart)
    #     self.bind("<KeyRelease>", self.control.keyEnd)
    #     self.after_idle(self.setStyle)
    #     self.mainloop()

    def setStyle(self):
        # self.title(self.control.NAME)
        # self.setSize()

        mf = self.main_frame = Frame(self, bg="black", width=self.w, height=self.h - 20)
        mf.place(relx=0, rely=0, x=0, y=0, anchor=NW)

        status_frame = self.sf = Frame(self, width=self.w, height=20)
        status_frame.place(relx=0, rely=1, x=0, y=0, anchor=SW)

        status_label = self.sl = Label(status_frame, text=self.control.NAME)
        status_label.place(relx=0, rely=1, x=3, y=-2, anchor=SW)

        main_canvas = self.mc = Canvas(mf, width=self.w, height=self.h - 20,bg="black")
        if(self.use_mouse):
            main_canvas.bind("<Motion>", self.control.mouseCamera)
        main_canvas.place(relx=0,rely=0,x=-1,y=-1, anchor=NW)

        # self.after_idle(self.control.start)

    # def setSize(self):
    #     self.geometry("%dx%d+%d+0" % (self.w, self.h, self.x))

if __name__ == "__main__":
    Main().start()

# cde