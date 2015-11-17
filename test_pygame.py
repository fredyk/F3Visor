import os, pygame, threading, math
import pygame.gfxdraw
from _3dlib import *
from lib.thread import Thread, TkThread, Runner
from testlib import *

class App(threading.Thread):
    # x = 0
    stopped = False
    objs = dict()
    cur_ob = 0
    delay = 1 / 60.0
    available_time = delay
    scale = 10
    visor =  [5, -10, 5]
    # visor_rot = [0, 0, -math.pi / 4.0]
    visor_rot = [0, 0, 0.0875]
    visor_disp = [0, 0, 0]
    rots = [0.032, {0:0, 1:0, 2:0}]
    movs = [64, {0:0,1:0,2:0}]
    painted = None
    width = 1920.0
    height = 1080.0
    points = []
    last_paint = 0
    cords = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.tkthread = TkThread(self)
        self.tkthread.noVerbose()
        self.tkthread.start()

        print 1
        # sys.stdout = open("stdout","wb")
        # sys.stderr = open("stderr","wb")
        self.scale = self.width / 10.0
        self.visor = [s for s in self.scaled(self.visor)]
        center = ( 5, 1, 5 )
        print "scale:", self.scale

        sys.stdout.flush()

    def scaled(self, v):
        if(type(v) == list)and(type(v[0])==tuple):
            return [
                tuple( [ c * self.scale for c in ve] )
                for ve in v
            ]
        else:
            return tuple( [c * self.scale for c in v] )

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
            ob0.rotate( [ ( (5, 5, 0), (math.pi / 2.0, 0, 1.0) ), ] )

    # def cube(self, width, position, rotation, color, name):
    #     cube = Volume([], [], name=name or ("cube"+str(self.cur_ob)), color=color)
    #     for x in xrange(2):
    #         for y in xrange(2):
                
    #     self.cur_ob += 1


    def calculatePoints(self, loop = False):
        app = self
        self.painted = set()
        init = now()
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

        for name, obj in app.objs.iteritems():
            # this method uses app gui main canvas and app cords
            init = now()
            # try: ch = canvas_height = app.gui.mc.winfo_height()
            # try: ch = size[1]
            try: ch = self.height
            except ValueError as e: print "error 0x01", sys.exc_info()#, [dir(e) for e in sys.exc_info()]
            else:
                # self.points = []
                # painted = []
                # painted = dict()
                # vertex = obj.getVertex()
                t0 = now()
                # if self.cords[name] is None:
                    # self.cords[name] = obj.getCords(app.visor, app.visor_rot, app.visor_disp, app.scale)
                cords = obj.getCords(app.visor, app.visor_rot, app.visor_disp, app.scale)
                # else:

                # print "mc:", app.gui.mc.winfo_height()
                # for face in obj.getFaces():
                # polygons = obj.getPolygons()
                # if ( now() - init ) >= self.available_time/2.0: break
                # cnt = self.last_paint
                cnt = 0
                while len(self.points) < cnt:
                    # self.points.append([(0, 0), (0, 0), (0, 0)])
                    self.points.append(None)
                # for pol in polygons[cnt:]:
                for pol in obj.getPolygons(cnt):
                    # if ( now() - init ) >= self.available_time/2.0: break
                    # face = [app.cords[n-1] for n in face]
                    if(not(app.stopped) ):#and (len(face)==4)):
                        # try: app.gui.mc.create_polygon([ cords[f-1] for f in face ], fill=obj.color, width=2, tags=obj.name) # paints in app gui main canvas
                        # except (ValueError, TclError) as e: print "error 0x02", sys.exc_info()#, [dir(e) for e in sys.exc_info()]
                        face = pol.getFace()
                        ps = []
                        for i, n in enumerate(face):
                            if(not(app.stopped)):
                                # if i == 0:
                                #     prev = -1
                                # else:
                                #     prev = i - 1
                                # # px, py = app.cords[face[prev]-1][0], app.gui.mc.winfo_height()-app.cords[face[prev]-1][1]
                                # px, py = cords[face[prev]-1][0], \
                                #          ch-cords[face[prev]-1][1]
                                # cx, cy = cords[n-1][0], \
                                #          ch-cords[n-1][1]
                                # paint = sorted([(px, py,), (cx, cy,)])
                                # if i == 0:
                                #     prev = -1
                                # else:
                                #     prev = i - 1
                                # px, py = app.cords[face[prev]-1][0], app.gui.mc.winfo_height()-app.cords[face[prev]-1][1]
                                # if(i < len(face) - 1):
                                px, py = cords[n-1][0], \
                                         ch-cords[n-1][1]
                                # cx, cy = cords[n-1][0], \
                                #          ch-cords[n-1][1]
                                # paint = sorted([(px, py,), (cx, cy,)])
                                paint = (px, py,)
                                # points.append(paint)
                                ps.append(paint)
                            else: break
                        # points.append(ps)
                        pol.setPaint(ps)
                        if([True for i, p in enumerate(ps[1:]) if p[0] != ps[i][0]]) and \
                          ([True for i, p in enumerate(ps[1:]) if p[1] != ps[i][1]]):
                            if(cnt >= len(self.points)):
                                self.points.append(pol)
                            elif(self.points[cnt] is None):
                                print "was None"
                                self.points[cnt] = pol
                        cnt += 1
                    else: break
                t1 = now()
                print len(cords) / float( (t1 - t0) or 1e-6 ), "cords/s"

                # for paint in points:
                # for pol in points[:16]:
        print "calc time:",now()-init
        if(loop):
            while not self.stopped:
                self.calculatePoints()

    def paintPolygons(self, screen, loop=False):
        app = self
        init = now()
        size = len(self.points)
        # for i, pol in enumerate(self.points):
        # for pol in self.points[self.last_paint:]:
        self.painted = set()
        for pol in self.points:
            if pol is None: print "is None"; continue
            # if ( now() - init ) >= self.available_time/2.0: break
            paint = list(pol.getPaint())
            obj = pol.getObj()

            if ( not (str(paint) in self.painted)):#and(i >= obj.last_paint):
                # canvas.create_line(px, py, cx, cy, fill="red")
                # try: app.gui.mc.create_line(*paint, fill=obj.color, width=2, tags=obj.name) # paints in app gui main canvas
                try:
                    # print paint
                    # app.gui.mc.create_polygon(*paint, outline=obj.color,fill="", width=2, tags=obj.name) # paints in app gui main canvas
                    # app.tkthread.after_gui( app.gui.mc.create_polygon, *paint, outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                    # app.tkthread.after_idle( app.gui.mc.create_polygon, *tuple(paint.list()), outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                    # app.gui.mc.delete(pol.getCode())
                    # app.tkthread.after_idle( app.gui.mc.delete, pol.getCode() )
                    # app.tkthread.after_idle( pol.setCode, app.gui.mc.create_polygon, *paint, outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                            # app.gui.mc.delete,
                    # app.tkthread.after_idle(
                    #     app.tkthread.nestedRun,
                        # [
                    # pol.setCode,
                            # ],
                        # BLUE,
                    pygame.gfxdraw.filled_polygon(
                        screen,
                        paint,
                        (0, 0, 255, 63),
                    )
                    pygame.gfxdraw.polygon(
                        screen,
                        paint,
                        (0, 0, 255),
                    )
                        # [(100, 100),(100, 200),(200, 100)],
                    # pygame.draw.polygon(screen, BLUE, paint, 1)
                    self.last_paint += 1 if ( self.last_paint < (size - 1) ) else -size
                except (ValueError, TclError) as e:

                    print "error 0x02", sys.exc_info()#, [dir(e) for e in sys.exc_info()]
                    pass
                else:
                    # painted.append(paint)
                    self.painted.add(str(paint))
        # self.painted = None
        print "paint time:",now()-init
        if(loop):
            while not self.stopped:
                self.paintPolygons(screen)
                # pass
        else:
            return (now() - init) or 1e-6

    def stop(self): self.stopped = True

# x, y = -1920, 0
x, y = 0, 0

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

app = App()
app.ObjFromFile("./objs/Gta-spano-2010 obj/Gta-spano-2010 obj.obj", "blue", rotate = True, name="car",scale=2.0)
# app.ObjFromFile("./objs/ferrari_599_gtb_obj/ferrari_599gtb.obj", "blue", rotate = True, name="car",scale=2.0)
# app.ObjFromFile("./objs/black.obj", "blue", rotate = True, name="car",scale=2.0)
# app.ObjFromFile("./objs/Minecraft Town OBJ/Minecraft Town.obj", "blue", rotate = True, name="car",scale=2.0)
step = 1.0 / app.delay
pygame.init()

BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
BLUE     = (   0,   0, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)

PI = 3.141592653

# size = (1920, 1080)
# app.width, app.height = 1280, 1024
app.width, app.height = 1920, 1080
# app.width, app.height = 585, 1040
size = (app.width, app.height)
screen = pygame.display.set_mode(size)
# screen = pygame.display.set_mode(pygame.FULLSCREEN)
if os.name == "posix":
    pygame.display.toggle_fullscreen()  

pygame.display.set_caption("3D Visor")

done = False
clock = pygame.time.Clock()
cnt = 0
cnt2 = 0
init = now()

Runner( callback=app.calculatePoints, args=(True,)).start()
# Runner( callback=app.paintPolygons, args=(screen,True)).start()

while not done:

    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done = True # Flag that we are done so we exit this loop

        # if(e.keysym == "Left"): # left

        #     self.rots[1][2] = -1

        # elif(e.keysym == "Up"): # up

        #     self.rots[1][0] = 1

        # elif(e.keysym == "Right"): # right

        #     self.rots[1][2] = 1

        # elif(e.keysym == "Down"): # down

        #     self.rots[1][0] = -1
        elif event.type == pygame.KEYDOWN:
            # Figure out if it was an arrow key. If so
            # adjust speed.
            if event.key == pygame.K_ESCAPE:
                done = True
            elif event.key == pygame.K_LEFT:
                app.rots[1][2] = -1
            elif event.key == pygame.K_RIGHT:
                app.rots[1][2] = 1
            elif event.key == pygame.K_UP:
                app.rots[1][0] = 1
            elif event.key == pygame.K_DOWN:
                app.rots[1][0] = -1
            elif(event.key == pygame.K_a):

                app.movs[1][0] = 1
            elif(event.key == pygame.K_w):

                app.movs[1][1] = -1
            elif(event.key == pygame.K_d):

                app.movs[1][0] = -1
            elif(event.key == pygame.K_s):

                app.movs[1][1] = 1
            elif(event.key == pygame.K_e):

                app.movs[1][2] = -1
            elif(event.key == pygame.K_c):

                app.movs[1][2] = 1

        # User let up on a key
        elif event.type == pygame.KEYUP:
            # If it is an arrow key, reset vector back to zero
            if event.key == pygame.K_LEFT:
                app.rots[1][2] = 0
            elif event.key == pygame.K_RIGHT:
                app.rots[1][2] = 0
            elif event.key == pygame.K_UP:
                app.rots[1][0] = 0
            elif event.key == pygame.K_DOWN:
                app.rots[1][0] = 0
            elif(event.key == pygame.K_a):

                app.movs[1][0] = 0
            elif(event.key == pygame.K_w):

                app.movs[1][1] = 0
            elif(event.key == pygame.K_d):

                app.movs[1][0] = 0
            elif(event.key == pygame.K_s):

                app.movs[1][1] = 0
            elif(event.key == pygame.K_e):

                app.movs[1][2] = 0
            elif(event.key == pygame.K_c):

                app.movs[1][2] = 0
    

    # pygame.draw.polygon(screen, BLUE,
    #     c3dto2d([
    #         (1000, 1000, 1000),
    #         (100, 1000, 2000),
    #         (2000, 3000, 1000)
    #         ]),
    #     1)
    # app.tkthread.after_idle(
    #         app.objs["car"].rotate,
    #         [
    #             (
    #                 (5.0, 5.0, 0),
    #                 ( 
    #                     0,
    #                     0,
    #                     2.0*math.pi / step
    #                     )
    #                 )
    #             ]
    #     )
    # app.tkthread.after_idle(

    #         app.calculatePoints
    #     )
    # # screen.fill(BLACK)
    # app.tkthread.after_idle(
    #     screen.fill,BLACK
    #     )
    # app.tkthread.after_idle(
    #     app.paintPolygons,
    #     screen
    #     )

    # app.tkthread.after_idle(
    #     pygame.display.flip
    #     )
    t0 = 0
    # t0 = app.objs["car"].rotate(
    app.tkthread.after_idle(
        app.objs["car"].rotate,
        [
            (
                (5.0, 5.0, 0),
                (
                    0, 0, 2.0*math.pi / step / 60.0
                    )
                )
            ]
        )
    # app.calculatePoints()
    screen.fill(BLACK)
    # screen.fill("#777777")
    screen.lock()
    t1 = app.paintPolygons(screen)
    screen.unlock()
    # pygame.display.flip()

    # self.gui.sl.config(text="fps: " + str(round(cnt2 / (max((now() - init), 1)), 1)))
    cnt += 1
    cnt2 += 1
    if(not(cnt % 600)):
        cnt2 = 0
        init = now()

    # Select the font to use, size, bold, italics
    font = pygame.font.SysFont('Calibri', 25, False, False)

    # Render the text. "True" means anti-aliased text. 
    # Black is the color. This creates an image of the 
    # letters, but does not put it on the screen
    # text = font.render("My text", True, BLACK)
    # text = font.render("fps: " + str(round(cnt2 / (max((now() - init), 1)), 1)), True, (255, 127, 63))
    text = font.render("fps: {:1.1f}".format(cnt2 / max(1e-3, float(now() - init) ) ), True, (255, 127, 63) )

    # Put the image of the text on the screen at 250x250
    # screen.blit(text, [10, 10])



    # clock.tick(60.0)
    # clock.tick(30.0)
    # clock.tick(15.0)
    # fps = min(1.0 / app.delay - 1.0 / (t0 + t1), 1.0 / app.delay)
    t = t0 + t1
    fps = 1.0 / t
    print "fps:", fps, {"t0":t0, "t1":t1}
    pygame.display.flip()
    # clock.tick(fps)

app.stop()
pygame.quit()
