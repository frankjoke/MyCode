#!python3
import sys
import math
import re

centerx = 100           # center of print x to start (need to be at least towerDistance/2*(nx+1))
centery = 100           # center of print y to start (need to be at least towerDistance/2*(ny+1))

towerSize = 20          # tower size in mm
towerDistance = 30      # tower distance in mm

filamentSize = 1.75     # Filament diameter
layerSize = 0.2         # Layer height
firstLayerSize = 0.15   # height of first layer 
nLayers = 200           # number of layers to print   
printWidth = 0.35       # nozzle or print width
fanOnL = 2              # Which layer will switch on Fans
tool = 1                # The tool to use (I used here the second head of my Felix3Dual)

nx = 3                  # number of flow towers with flowStep (going around center)
ny = 3                  # number of retract towers with retractStep (starting at 1)

retractSpeed = 30       # Detract Speed mm/s
extrudeSpeed = 5        # when extruding 
retractStep = 1.0       # detract start mm  - x
addlRetractStep = 0.03  # detract more than retract - y
moveSpeed = 150         # move Speed
printSpeed = 40         # print speed
changeSpeed = True      # switches off/on changeRetract
speedStep = 15          # Speed change steps
temp = 215              # start temperature
changeTemp = True       # Change temperature on layers?
layersTemp = 1          # change one degree every n mm
bedTemp = 55            # bet temp start
bedTempL2 = 40          # bed temp after L1

liftHead = 0            # lift head after retract and move back before
moreFeed = 100          # If >100 then feed will be increased to this value on first layer

changeRetract = not changeSpeed
changeFlow = True       # use Flow change
flowStep = 15           # percent of flow change 10 = 10% 
lPrime = 3              # last retract which should be used

cSpeed = printSpeed     # current print speed
cRetract = 2            # current retract len
cTemp = temp            # current temp
cFlow = 0.03            # current flowrate - will be calculated automatically
cZ = 0                  # current Z height
cLayer = 0              # current layer
cExtruder = 0           # current extruder position 


lX = 0
lY = 0
lZ = 0

filename = "TestGen.gcode"  # default filename
outfile = sys.stdout

verbose = True

def pv(arg):
    if verbose:
        print(arg)
        
def p(str,end='\n'):
    global outfile
    lines = str.split('|');
    for l in lines[:-1]:
        print(l,file=outfile)
    print(lines[-1],end=end,file=outfile)

def gline(x=None,y=None,z=None,e=None,f=None):
    global cExtruder,cFlow,lX,lY,lZ
    cx = lX
    cy = lY
    cz = lZ
    l = "G1"
    if x!=None:
        if cx != x:
            cx = x
            l += " X{0:01f}".format(x)
    if y!=None:
        if cy != y:
            cy = y
            l += " Y{0:01f}".format(y)
    if z!=None:
        if cz != z:
            cz = z
            l += " Z{0:01f}".format(z)
    if e!=None:
        cExtruder += cFlow * math.sqrt(math.pow(cx-lX,2)+math.pow(cy-lY,2))
        l += " E{0:01f}".format(cExtruder)
    if f!=None:
        l += " F{0:01.0f}".format(f*60)  # from mm/s to mm/min
    if cx!= lX:
        lX=cx
    if cy!= lY:
        lY=cy
    if cz!= lZ:
        lZ=cz
    p(l)

def gmove(x=None,y=None,z=None):
    gline(x=x,y=y,z=z,e=None,f=moveSpeed)

def gprint(x=None,y=None):
    gline(x=x,y=y,z=None,e=True,f=cSpeed)

def extrude(dist,speed=retractSpeed,reset=True):
    global lPrime,cExtruder
    rt = ""
 
    if dist==None:          # if dist is none prime retracted len
        dist=lPrime
        rt = " ; Prime Retract %f" % dist
        gmove(None,None,cZ)
    lPrime = 0
    if dist!=0:
        cExtruder += float(dist)
        if dist<0:
            lPrime = -dist  # if dist was negative we retracted, keep info about last retraction
            rt = " ; Retract %f" %dist
        p("G1 E{0:01f} F{1:1d}".format(cExtruder,int(speed*60.0))+rt)
        if reset:
            p("G92 E0")
            cExtruder = 0
        if lPrime!=0:
            gmove(None,None,cZ+liftHead)

def pinfo():
    p("M117 {0:1d}/{1:1d}Z{2:01.2f}t{3:1d};".format(cLayer,nLayers,cZ,cTemp))
        
def towera(xt,yt):          # print one layer of one tower
    gmove(xt+towerSize/2,yt,cZ)
    extrude(None,reset=False)
    gprint(xt+towerSize,yt)
    gprint(xt+towerSize,yt+towerSize)
    extrude(-cRetract,reset=False)
    gmove(xt,yt+towerSize)
    extrude(None,reset=False)
    gprint(xt,yt)
    gprint(xt+towerSize/2,yt)
    extrude(-cRetract)

def tower(xt,yt):           # on first layer print 3 towers with 2 of them sligtly moved
    towera(xt,yt)
    if cLayer==1:
        towera(xt+printWidth,yt+printWidth)
        towera(xt-printWidth,yt-printWidth)

def mopt(arg,opt,default):  # check and parse a certain option
    ms = '^'+opt[:-1]
    me = opt[-1]
    if me=='d':
        ms +="([-\d]+)$"
    elif me=='f':
        ms +="([-\d\.]+)$"
    elif me=='b':
        ms +="(.+)$"
    elif me=='s':
        ms +="(.+)$"
    match = re.match(ms,arg.rstrip())
    if match:
        mg = match.group(1).strip()
        # pv(ms + ":=" + mg)
        if me=='d':
            return int(mg)
        if me=='f':
            return float(mg)
        if me=='b':
            return bool(mg) 
        if me=='s':
            return mg
    return default

if __name__ == '__main__':
    # run the code if not included
    args = sys.argv
    # args += ["-v","-b=50", "-ts=16", "-cs=1", "-o=Filename.gco"] # test
    # args += ["-v","-bt=45", "-lh=0.3", "-r=1.5", "-rsp=30", "-nl=100", "-b2=0", "-lt=0.5", "-ts=15", "-et=230", "-ps=30", "-ss=5", "-o=NinjaTest.gcode"] # my test for NinjaFlex
    # args += ["-v","-bt=55", "-lh=0", "-r=1.5", "-rsp=30", "-nl=100", "-b2=50", "-lt=0.5", "-ts=15", "-et=210", "-ps=40", "-ss=15"] # my test for Nunus 3D
    verbose = '-v' in args
    pv(args)
    for arg in args[1:]:
        a=arg.strip()        
        if a[0]=='-':
            a=a[1:]
            towerSize=mopt(a,"ts=d",towerSize)
            towerDistance=mopt(a,"td=d",towerDistance)
            bedTemp=mopt(a,"bt=d",bedTemp)
            bedTempL2=mopt(a,"b2=d",bedTempL2)
            nLayers=mopt(a,"nl=d",nLayers)
            fanOnL=mopt(a,"fl=d",fanOnL)
            filename=mopt(a,"o=s",filename)
            changeSpeed=mopt(a,"cs=b",changeSpeed)
            layerSize=mopt(a,"ls=f",layerSize)
            firstLayerSize=mopt(a,"fls=f",firstLayerSize)
            tool=mopt(a,"t=d",tool)
            nx=mopt(a,"nx=d",nx)
            ny=mopt(a,"ny=d",ny)
            cRetract=mopt(a,"r=f",cRetract)
            retractSpeed=mopt(a,"rsp=f",retractSpeed)
            extrudeSpeed=mopt(a,"es=f",extrudeSpeed)
            retractStep=mopt(a,"rst=f",retractStep)
            moveSpeed=mopt(a,"ms=d",moveSpeed)
            printSpeed=mopt(a,"ps=d",printSpeed)
            speedStep=mopt(a,"ss=d",speedStep)
            temp=mopt(a,"et=d",temp)
            changeTemp=mopt(a,"ct=b",changeTemp)
            layersTemp=mopt(a,"lt=f",layersTemp)
            changeFlow=mopt(a,"cf=b",changeFlow)
            flowStep=mopt(a,"fs=d",flowStep)
            centerx=mopt(a,"cx=d",centerx)
            centery=mopt(a,"cy=d",centery)
            liftHead=mopt(a,"lh=f",liftHead)
            

    skx = int((nx+0.5)* towerDistance/2)  # skirt x size around center 
    sky = int((ny+0.5)* towerDistance/2)  # skirt y size around center

    flowrate = layerSize*printWidth/(math.pow(filamentSize/2,2) * math.pi) # pro mm
    changeRetract = not changeSpeed
    
    cSpeed = printSpeed     # current print speed
    cTemp = temp            # current temp
    cFlow = flowrate        # current flowrate
    cZ = 0                  # current Z height
    cLayer = 0              # current layer
    cExtruder = 0           # current extruder position

    with open(filename, 'w') as outfile:
        p("G21 ; mm mode|G90 ; absolute mode|G28 ; home")           # setup printer modes
        p("T{0:1d} ; Select Tool|M82 ; Absolute E|G92 E0 ; reset extruder".format(tool))    # define tool & extruder mode
        p("M107 ; stop fan|M140 S{0:1d} ; Bed Temp|M109 S{1:1d} ; Extruder Temp".format(bedTemp,temp)) # define temperatures
        if moreFeed>100:                                            # if moreFeed>100
            p("M221 S{:1d} set feed to moreFeed".format(moreFeed))  # increase feed for first layer
        gline(50,0,20,None,moveSpeed)
        extrude(20,extrudeSpeed)
        extrude(-cRetract)
        gline(0,0,None,None,printSpeed/2)        
        for l in range(nLayers):
            cZ = l*layerSize+firstLayerSize
            t = int(temp-int(cZ/layersTemp))
            if changeTemp and t != cTemp:
                cTemp = t
                p("M104 S{0:1d} ; Change temperature".format(cTemp))
            if l<1:
                p("; Print Skirt")
                pinfo()
                gmove(centerx-skx,centery-sky,cZ)
                #extrude(None)
                gprint(centerx+skx,centery-sky)
                gprint(centerx+skx,centery+sky)
                gprint(centerx-skx,centery+sky)
                gprint(centerx-skx,centery-sky)
                extrude(-cRetract)
            cLayer = l+1
            p("; Begin Layer {:1d} of {:1d}, Z={:01.2f}".format(cLayer,nLayers,cZ))
            if cLayer==2 and moreFeed>100:
                p("M221 S100; Extruder feed normal")
            if cLayer == fanOnL:
                p("M106 S255 ; Turn Fan on|M140 S{0:1d} ; Set Bed temp".format(bedTempL2))

            pinfo()

            t = 0
            for x in range(nx):
                for y in range(ny):
                    t += 1
                    if changeSpeed:                 # change speed on Y-movement, only one of two works
                        cSpeed = printSpeed + ((y-(ny-1)/2.0)*speedStep)
                    if changeRetract:               # change retract on Y-movement, only one of two works
                        cRetract = retractStep * (y+1)
                    if changeFlow:                  # # change speed on X-movement
                        cFlow = flowrate * (1+(x-(nx-1)/2.0)*flowStep/100)
                    p("; Tower x={0:1d}, y={1:1d}, cRetract={2:01.2f}, cFlow={3:01.1f}%, cSpeed={4:01.1f}".format(x+1,y+1,cRetract,100.0*cFlow/flowrate,cSpeed))
                    tower(centerx - nx/2.0 * towerDistance + x * towerDistance,centery - ny/2.0 * towerDistance + y * towerDistance)
            
        extrude(-10,retractSpeed)                   # clean up nozzle 
        gmove(0,0,cZ+10)                # move home
        p("M107 ; Fan Off|M140 S0 ; Bed Temp Off|M104 S0 ; Tool heat off|M221 S100 ; reset feed |M220 S100 ; reset speed")


