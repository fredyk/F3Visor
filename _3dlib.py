##IMPORTS
##NOBUILD
import math, sys
from Tkinter import TclError
from time import sleep, time as now
##BUILD
##EIMPORTS
##LIB
def trygon_signs(a, b=None):
    a, b = [x for x in a] if (b is None) else (a, b)
    return (
                1 if a>0 else -1, # sin sign
                1 if b>0 else -1  # cos sign
        )

def ang(a, b=None):
    a, b = [x for x in a] if (b is None) else (a, b)
    signs = trygon_signs(a, b)
    tan = abs(b/float(a)) if a != 0 else 9999
    return math.atan(tan) if (
            signs == (1, 1)
        ) else (
            math.pi-math.atan(tan) if (
                signs == (-1, 1)
                ) else (
                    math.pi+math.atan(tan) if (
                        signs == (-1, -1)
                        ) else (
                            math.pi*2-math.atan(tan)
                            )
                    )
            )

def dist(a, _b, c=None, d=None):
    if (not(c)) and (not(d)) and ((type(a)==tuple)or(type(a)==list)) \
                             and ((type(_b)==tuple)or(type(_b)==list)):
        a, b = (a) if (type(a)==tuple) else (a[0], a[1])
        c, d = (_b) if (type(_b)==tuple) else (_b[0], _b[1])
    else:
        b = _b
        if (not(d)) and (c) and ((type(c)==tuple)or(type(c)==list)):
            c, d = (c) if (type(c)==tuple) else (c[0], c[1])
    return math.sqrt((a-c)**2+(b-d)**2)

def c3dto2d(a, b=None, c=None, visor=(1920/2, -1920, 1080/2), _int=False): #[x, y, z]
    res = []
    for a in a:
        x, y, z = (a) if (not(b) and not(c)) else (a, b, c)
        vx, vy, vz = visor
    ##NOBUILD
    ##    print (vx-x)/float((vz-z))*(0-z), \
    ##          '\n           ', (vy-y)/float((vz-z))*(0-z)
    ##BUILD
        res.append( (
                ( int(x+(vx-x)/float((vy-y))*(0-y)), #x1
                  int(z+(vz-z)/float((vy-y))*(0-y)) )  #y1
            ) if (_int) else (
                x+(vx-x)/float((vy-y))*(0-y), #x1
                z+(vz-z)/float((vy-y))*(0-y)  #y1
                ) )
    # return (
    #         int(x+(vx-x)/float((vy-y))*(0-y)), #x1
    #         int(z+(vz-z)/float((vy-y))*(0-y))  #y1
    #     ) if (_int) else (
    #         x+(vx-x)/float((vy-y))*(0-y), #x1
    #         z+(vz-z)/float((vy-y))*(0-y)  #y1
    #         )
    return res

def _rot(cords, center, angle):
    x0, y0 = cords if type(cords)==tuple else [c for c in cords]
    cx, cy = center if type(center)==tuple else [c for c in center]
##NOBUILD
##    rx, ry = angle if type(angle)==tuple else [a for a in angle]
##BUILD
    res = complex(x0 - cx, y0 - cy) * complex(math.cos(angle), math.sin(angle))
    # res = complex(x0 - cx, y0 - cy) * angle
    return cx+ res.real, cy + res.imag
    rz = angle
    a = dist((x0, y0),(cx, cy))# * (-1 if ((((x0-cx)>=0)and((y0-cy)<0))or\
##                                          (((y0-cy)>=0)and((x0-cx)<0))) else 1)
##NOBUILD
##    beta = (math.atan((y0-cy)/float(x0-cx)) if (x0-cx)<>0 else math.pi/2.0)
##BUILD
    beta = ang((x0-cx, y0-cy))
##NOBUILD
##    if ((y0-cy)<0)and((x0-cx)<0):
##        beta+=math.pi
##    elif ((y0-cy)>0)and((x0-cx)<0):
##        beta+=math.pi
##BUILD
    alpha_beta = rz + beta
##NOBUILD
##    print a, alpha_beta,
##BUILD
    return (
        cx + a * \
            math.cos(alpha_beta),
        cy + a * \
            math.sin(alpha_beta)
        )

def rot(cords, angles):
    res = []
    for cord in cords:
        if(len(cord)==3):
            x0, y0, z0 = cord# if type(cords)==tuple else [c for c in cords]
            for angle in angles:
                center = angle[0]
                angle = angle[1]
                rx, ry, rz = angle# if type(angle)==tuple else [a for a in angle]
                cx, cy, cz = center# if type(center)==tuple else [c for c in center]
            ##NOBUILD
            ##    print x0, y0, z0
            ##BUILD

                y0, z0 = _rot((y0, z0), (cy, cz), rx) if rx else (y0, z0)
            ##NOBUILD
            ##    print x0, y0, z0
            ##BUILD
                x0, z0 = _rot((x0, z0), (cx, cz), ry) if ry else (x0, z0)
            ##NOBUILD
            ##    print x0, y0, z0
            ##BUILD
                x0, y0 = _rot((x0, y0), (cx, cy), rz) if rz else (x0, y0)
            ##NOBUILD
            ##    print x0, y0, z0
            ##BUILD
            res.append( (x0, y0, z0) )
        else:
            print "error bad cords", cord
    # return x0, y0, z0
    return res
##NOBUILD
##    print math.atan((y0-cy)/float(x0-cx)), (y0-cy)/float(x0-cx)
##    return (
##        dist((x0, y0),(cx, cy)) * \
##            math.cos(rz+math.atan((y0-cy)/float(x0-cx))),
##        y0,
##        z0
##        )

def mov(cords, movs):
    res = []
    for cord in cords:
        x0, y0, z0 = cord# if type(cords)==tuple else [c for c in cords]
        for angle in movs:
            # center = angle[0]
            # angle = angle[1]
            rx, ry, rz = angle# if type(angle)==tuple else [a for a in angle]
            # cx, cy, cz = center# if type(center)==tuple else [c for c in center]
            x0+=rx
            y0+=ry
            z0+=rz
        ##NOBUILD
        ##    print x0, y0, z0
        ##BUILD

            # y0, z0 = _rot((y0, z0), (cy, cz), rx) if rx else (y0, z0)
        ##NOBUILD
        ##    print x0, y0, z0
        ##BUILD
            # x0, z0 = _rot((x0, z0), (cx, cz), ry) if ry else (x0, z0)
        ##NOBUILD
        ##    print x0, y0, z0
        ##BUILD
            # x0, y0 = _rot((x0, y0), (cx, cy), rz) if rz else (x0, y0)
        ##NOBUILD
        ##    print x0, y0, z0
        ##BUILD
        res.append( (x0, y0, z0) )
    # return x0, y0, z0
    return res
##NOBUILD
##    print math.atan((y0-cy)/float(x0-cx)), (y0-cy)/float(x0-cx)
##    return (
##        dist((x0, y0),(cx, cy)) * \
##            math.cos(rz+math.atan((y0-cy)/float(x0-cx))),
##        y0,
##        z0
##        )

def paintObj(obj, app):

    # this method uses app gui main canvas and app cords
    init = now()
    try: ch = canvas_height = app.gui.mc.winfo_height()
    except ValueError as e: print "error 0x01", sys.exc_info()#, [dir(e) for e in sys.exc_info()]
    else:
        points = []
        # painted = []
        painted = set()
        # painted = dict()
        # vertex = obj.getVertex()
        t0 = now()
        cords = obj.getCords(app.visor, app.visor_rot, app.visor_disp, app.scale)
        # print "mc:", app.gui.mc.winfo_height()
        # for face in obj.getFaces():
        polygons = obj.getPolygons()
        size = len(polygons)
        for pol in polygons[obj.last_paint:]:
            if ( now() - init ) >= app.available_time: break
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
                points.append(pol)
            else: break
        t1 = now()
        print len(cords) / float( (t1 - t0) or 1e-6 ), "cords/s"

        # for paint in points:
        for pol in points:
            if ( now() - init ) >= app.available_time: break
            paint = pol.getPaint()
            if ( not (str(paint) in painted)):
                # canvas.create_line(px, py, cx, cy, fill="red")
                # try: app.gui.mc.create_line(*paint, fill=obj.color, width=2, tags=obj.name) # paints in app gui main canvas
                try:
                    # app.gui.mc.create_polygon(*paint, outline=obj.color,fill="", width=2, tags=obj.name) # paints in app gui main canvas
                    # app.tkthread.after_gui( app.gui.mc.create_polygon, *paint, outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                    # app.tkthread.after_idle( app.gui.mc.create_polygon, *tuple(paint.list()), outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                    # app.gui.mc.delete(pol.getCode())
                    # app.tkthread.after_idle( app.gui.mc.delete, pol.getCode() )
                    # app.tkthread.after_idle( pol.setCode, app.gui.mc.create_polygon, *paint, outline=obj.color,fill="", width=2, tags=obj.name ) # paints in app gui main canvas
                            # app.gui.mc.delete,
                    app.tkthread.after_idle(
                        app.tkthread.nestedRun,
                        [
                            app.update,
                            app.delete,
                            pol.setCode,
                            app.gui.mc.create_polygon,
                            ],
                        *paint,
                        outline=obj.color,
                        fill="",
                        width=1,
                        tags=obj.name
                    )
                    obj.last_paint += 1 if ( obj.last_paint < (size - 1) ) else -size
                except (ValueError, TclError) as e:

                    # print "error 0x02", sys.exc_info()#, [dir(e) for e in sys.exc_info()]
                    pass
                else:
                    # painted.append(paint)
                    painted.add(str(paint))

if __name__ == '__main__':
##    for y in xrange(0, 1080, 100):
##        for x in xrange(0, 1920, 100):
##            x, y, z = x, y, 1
##            print [x, y, z], c2dto3d([x, y, z], _int=True)
##    for x in xrange(-1, 2, 2):
##        for y in xrange(-1, 2, 2):
####            for z in xrange(-1, 2, 2):
##            x, y, z = x, y, 0
##            print [x, y, z], rot((x, y, z), (0, 0, 0), [0, 0, 1])
##        math.pi/4.0,
##        math.pi/4.0,
##        math.pi/4.0])
    # print 
    print c3dto2d( rot(
##        rot((1, 0, 0), (0, 0, 0), (math.pi/2.0, 0, 1)),
        [
            (100, 100, 100),
            (100, 100, 200),
            (100, 200, 100),
            (100, 200, 200),
            (200, 100, 100),
            (200, 100, 200),
            (200, 200, 100),
            (200, 200, 200)
            ],
        [
            [
                (0, 1024/2, 768/2),
                (1, 0, 1) ]
            ]
        ), _int = True )
##BUILD
##ELIB
