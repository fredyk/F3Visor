import os, pygame, threading, math, re, json
import pygame.gfxdraw
from _3dlib import *
from lib.thread import Thread, TkThread, Runner
from testlib import *


class App(threading.Thread):
    # x = 0
    stopped = False
    objs = dict()
    cur_ob = 0
    delay = 1 / 30.0
    available_time = delay
    scale = 10
    visor = [0, -10, 5]
    # visor_rot = [0, 0, -math.pi / 4.0]
    visor_rot = [0, 0, 0.0625]
    visor_disp = [0, 0, 0]
    rots = [0.032, {0: 0, 1: 0, 2: 0}]
    movs = [64, {0: 0, 1: 0, 2: 0}]
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
        self.scale = self.width / 10.0
        self.visor = [s for s in self.scaled(self.visor)]
        center = (5, 1, 5)
        print "scale:", self.scale

        sys.stdout.flush()

    def scaled(self, v):
        if (type(v) == list) and (type(v[0]) == tuple):
            return [
                tuple([c * self.scale for c in ve])
                for ve in v
            ]
        else:
            return tuple([c * self.scale for c in v])

    def ObjFromFile(self, path, color="blue", rotate=True, name="", scale=1.0):
        ob0file = open(path, "rb")
        ob0 = Volume([], [], name=name or ("ob" + str(self.cur_ob)), color=color)
        self.objs[ob0.name] = ob0
        self.cur_ob += 1
        # scale = 1.0
        verts = []
        for l in ob0file:
            dt = l.strip().split(" ")
            if dt[0] == "v":
                verts.append([float(d) for d in dt[1:] if d])

            elif dt[0] == "f":
                vs = [
                    d.split("/")[0]
                    for d in dt[1:]
                ]
                ob0.addFace(tuple([int(float(s)) for s in vs]))
        min_z = 0
        max_z = 0
        min_y = 0
        max_y = 0

        for v in verts:
            if (v[2] < min_z):
                min_z = v[2]
            elif (v[2] > max_z):
                max_z = v[2]
            if (v[1] < min_y):
                min_y = v[1]
            elif (v[1] > max_y):
                max_y = v[1]

        scale = ((max_z - min_z) if \
                     ((max_z - min_z) > (max_y - min_y)) else \
                     (max_y - min_y)) / 5.0 * 1 / float(scale)
        print ob0.name, scale, min_y, max_y, min_z, max_z
        for v in verts:
            ob0.addVert(tuple(float(d) / scale + (5.0 if i < 2 else 0.0)
                              for i, d in enumerate(v)))
        ob0file.close()
        if (rotate):
            ob0.rotate([((5, 5, 0), (math.pi / 2.0, 0, 1.0)), ])

    def calculatePoints(self, loop=False):
        """
        This method uses app gui main canvas and app cords
        :param loop: 
        """
        app = self
        self.painted = set()
        init = now()
        for r in self.rots[1]:
            if (self.rots[1][r]):
                self.visor_rot[r] += self.rots[0] * self.rots[1][r]

        for m in self.movs[1]:
            if (self.movs[1][m]):
                if (m == 0):
                    self.visor_disp[m] += self.movs[0] * self.movs[1][m] * math.cos(self.visor_rot[2])
                elif (m == 1):
                    self.visor_disp[m] += self.movs[0] * self.movs[1][m] * math.cos(self.visor_rot[2])
                else:
                    self.visor_disp[m] += self.movs[0] * self.movs[1][m]

        for name, obj in app.objs.iteritems():
            init = now()
            try:
                ch = self.height
            except ValueError as e:
                print "error 0x01", sys.exc_info()  # , [dir(e) for e in sys.exc_info()]
            else:
                t0 = now()
                cords = obj.getCords(app.visor, app.visor_rot, app.visor_disp, app.scale)
                cnt = 0
                while len(self.points) < cnt:
                    self.points.append(None)
                for pol in obj.getPolygons(cnt):
                    if (not (app.stopped)):  # and (len(face)==4)):
                        face = pol.getFace()
                        ps = []
                        for i, n in enumerate(face):
                            if (not (app.stopped)):
                                px, py = cords[n - 1][0], \
                                         ch - cords[n - 1][1]
                                paint = (px, py,)
                                ps.append(paint)
                            else:
                                break
                        pol.setPaint(ps)
                        if ([True for i, p in enumerate(ps[1:]) if p[0] != ps[i][0]]) and \
                                ([True for i, p in enumerate(ps[1:]) if p[1] != ps[i][1]]):
                            if (cnt >= len(self.points)):
                                self.points.append(pol)
                            elif (self.points[cnt] is None):
                                print "was None"
                                self.points[cnt] = pol
                        cnt += 1
                    else:
                        break
                t1 = now()

        if (loop):
            while not self.stopped:
                self.calculatePoints()

    def paintPolygons(self, screen, loop=False):
        app = self
        init = now()
        size = len(self.points)
        self.painted = set()
        for pol in self.points:
            if pol is None: print "is None"; continue
            # if ( now() - init ) >= self.available_time/2.0: break
            paint = list(pol.getPaint())
            obj = pol.getObj()

            if (not (str(paint) in self.painted)):  # and(i >= obj.last_paint):
                try:
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
                    self.last_paint += 1 if (self.last_paint < (size - 1)) else -size
                except (ValueError, TclError) as e:

                    print "error 0x02", sys.exc_info()  # , [dir(e) for e in sys.exc_info()]
                    pass
                else:
                    self.painted.add(str(paint))
        if (loop):
            while not self.stopped:
                self.paintPolygons(screen)
        else:
            return (now() - init) or 1e-6

    def stop(self):
        self.tkthread.stop()
        self.stopped = True


x, y = 0, 0

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

app = App()
app.ObjFromFile("./objs/Gta-spano-2010 obj/Gta-spano-2010 obj.obj", "blue", rotate=True, name="car", scale=2.0)
step = 1.0 / app.delay
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

PI = 3.141592653

app.width, app.height = 1920, 1080
size = (app.width, app.height)

texts = []
colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (2)
}
values = [0, 127, 255]
y = 40

keys = ["text", "x", "y", "color", "font", "size", "bold", "italic"]
patt = r"(\s*rgb\s*\(\s*)" + \
       r"([0-9]?[0-9]?[0-9])" + \
       r"(\s*\,\s*)" + \
       r"([0-9]?[0-9]?[0-9])" + \
       r"(\s*\,\s*)" + \
       r"([0-9]?[0-9]?[0-9])(\s*\)\s*)"
for fn in os.listdir("./"):
    if os.path.splitext(fn)[1].lower() in [".gui"] and os.path.isfile(fn):
        ftexts = open(fn, "rb").read().split("\n\n")
        for t in ftexts:
            text = dict()
            lines = t.splitlines()
            for l in lines:
                key = l.split(":")[0].strip().lower()
                value = "".join(l.split(":")[1:]).strip()
                print key, value
                if key in keys:
                    if key == "color":
                        r = re.search(patt, value)
                        if r and r.group(2) and r.group(4) and r.group(6):
                            # print r.groups()
                            try:
                                r, g, b = (int(r.group(x)) for x in [2, 4, 6])
                            except Exception as e:
                                print e
                            else:
                                print "rgb: ", r, g, b
                                text["color"] = (r, g, b)
                    elif key in ["x", "y", "size"]:
                        try:
                            text[key] = int(value)
                        except Exception as e:
                            print e
                    elif key in ["bold", "italic"]:
                        value = value.lower()
                        text[key] = True if value in ["true", "1", "yes"] else False
                    else:
                        text[key] = value
            if text:
                texts.append(text)
defaults = {
    "text": "",
    "x": 10,
    "y": 10,
    "color": (255, 255, 255),
    "font": "Calibri",
    "size": 18,
    "bold": False,
    "italic": False
}

for t in texts:
    for d in defaults:
        if not d in t:
            t[d] = defaults[d]

with open("texts.json", "wb") as f:
    f.write(json.dumps(texts, indent=4, separators=(",", ":")))

screen = pygame.display.set_mode(size)
if os.name == "posix":
    pygame.display.toggle_fullscreen()

pygame.display.set_caption("3D Visor")

done = False
clock = pygame.time.Clock()
cnt = 0
cnt2 = 0
init = now()
target_fps = 1.0 / app.delay
fps = target_fps

Runner(callback=app.calculatePoints, args=(True,)).start()

while not done:

    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

        elif event.type == pygame.KEYDOWN:
            """
            Figure out if it was an arrow key. If so
            adjust speed.
            """
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

            elif event.key == pygame.K_a:
                app.movs[1][0] = 1

            elif event.key == pygame.K_w:
                app.movs[1][1] = -1

            elif event.key == pygame.K_d:
                app.movs[1][0] = -1

            elif event.key == pygame.K_s:
                app.movs[1][1] = 1

            elif event.key == pygame.K_e:
                app.movs[1][2] = -1

            elif event.key == pygame.K_c:
                app.movs[1][2] = 1

        elif event.type == pygame.KEYUP:
            """
            User let up on a key
            If it is an arrow key, reset vector back to zero
            """
            if event.key == pygame.K_LEFT:
                app.rots[1][2] = 0
            elif event.key == pygame.K_RIGHT:
                app.rots[1][2] = 0
            elif event.key == pygame.K_UP:
                app.rots[1][0] = 0
            elif event.key == pygame.K_DOWN:
                app.rots[1][0] = 0
            elif event.key == pygame.K_a:
                app.movs[1][0] = 0
            elif event.key == pygame.K_w:
                app.movs[1][1] = 0
            elif event.key == pygame.K_d:
                app.movs[1][0] = 0
            elif event.key == pygame.K_s:
                app.movs[1][1] = 0
            elif event.key == pygame.K_e:
                app.movs[1][2] = 0
            elif event.key == pygame.K_c:
                app.movs[1][2] = 0

    t0 = 0
    app.tkthread.after_idle(
        app.objs["car"].rotate,
        [
            (
                (5.0, 5.0, 0),
                (
                    0, 0, 2.0 * math.pi / step / max(target_fps, fps)
                )
            )
        ]
    )
    _paint = False
    if fps >= target_fps:
        _paint = True
    if _paint:
        print "PAINT"
        screen.fill(BLACK)
        screen.lock()
        t1 = app.paintPolygons(screen)
        screen.unlock()

    cnt += 1
    cnt2 += 1
    if not (cnt % 600):
        cnt2 = 0
        init = now()

    if _paint:
        """Select the font to use, size, bold, italics"""
        font = pygame.font.SysFont('Calibri', 25, False, False)

        """
        Render the text. "True" means anti-aliased text. 
        Black is the color. This creates an image of the 
        letters, but does not put it on the screen
        """
        text = font.render(
            "fps: {:1.1f} Camera rotation: {:s} Camera position: {:s} / {:s}".format(fps, str(app.visor_rot),
                                                                                     str(app.visor),
                                                                                     str(app.visor_disp)), True,
            (255, 127, 63))

        """Put the image of the text on the screen at 10x10"""
        for t in texts:
            text_surface = pygame.font.SysFont(t["font"], t["size"], t["bold"], t["italic"]) \
                .render(t["text"], True, t["color"])
            size = text_surface.get_size()
            x, y = t["x"], t["y"]
            screen.blit(text_surface, [
                x if x > 0 else app.width + x - size[0],
                y if y > 0 else app.height + y - size[1]]
                        )
        screen.blit(text, [10, 10])

    t = t0 + t1
    fps = cnt2 / max(1e-3, float(now() - init))
    pygame.display.flip()
    nfps = min(fps, fps ** 2 / float(target_fps * 1.01))
    print "fps", fps, "nfps", nfps
    if nfps >= target_fps:
        clock.tick(nfps)

app.stop()
pygame.quit()
