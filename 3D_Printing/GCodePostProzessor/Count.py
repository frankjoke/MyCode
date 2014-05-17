#! python3

"""
Gcode to add 'layer/of layers %' message to KISSlicer.

Please add to Kisslicer Printer/Firmware/Post-Process the following:
/full/path/to/Count.py "<FILE>" [-v] ["-L[-]x g-code"]*

"""

import math
import os
import re
import sys
import time

verbose = True

def pv(arg):
    if verbose:
        print(arg)

def should_skip(p0, p1, p2):
    """Check if p1 is on a straight line between p0 and p2."""
    if p0 is None:
        return False
    if p1 is None:
        return False
    if p2 is None:
        return False
    indices = range(len(p1))
    # Calculate vectors for p1 and p2 relative to p0.
    v1 = [p1[i] - p0[i] for i in indices]
    v2 = [p2[i] - p0[i] for i in indices]
    # Calculate the lengths of the relative vectors.
    l1 = math.sqrt(sum(v1[i] * v1[i] for i in indices))
    l2 = math.sqrt(sum(v2[i] * v2[i] for i in indices))
    if l2 < 0.1:
        # Ignore midpoint because the whole segment is very short.
        return 'length=%.5f (too short)' % l2
    ratio = l1 / l2  # Ratio of midpoint vs endpoint.
    # How far is the midpoint away from straight line?
    d = [v1[i] - v2[i] * ratio for i in indices]
    error = math.sqrt(sum(d[i] * d[i] for i in indices))
    if error > 0.02:
        return False
    # Ignore midpoint because it is very close to the straight line.
    return 'ratio=%.5f error=%.5f (straight line)' % (ratio, error)

def rewrite(infile, outfile, args):
     
    l = 0
    al = []
    lc = []
    for a in args:
        match = re.match(r'^-L([\d-]+)(\s+)(.+)',a.rstrip())
        if match:
            al.append([int(match.group(1)),match.group(3)])
    pv(al)
    nl = 0
    ml = 0
    islc = False
    for line in infile:
        l = l +1
        if re.match(r'^; BEGIN_LAYER_OBJECT z=([\d\.]+)',line.rstrip()):
            nl += 1

        if islc:
            match = re.match(r'^G1 X',line.rstrip())
            if match:
                lc.append(line.rstrip()+"; Count.py move")
                pv("Tool change {:1d}:".format(len(lc)) +line.rstrip())
                islc = False
        else:
            match = re.match(r'^; \*\*\* Changing Extruders from',line.rstrip())
            if match:
                islc = True
                pv("Line {:1d} layer {:1d}".format(l,nl)+line.rstrip())
        
#    infile.seek(0)
    ml = nl
    nl = 0
    nc = len(lc)
    c = 0
    lz = 0
    lp = 0
    pv("Max Layer={:1d}, Tool changes={:1d}".format(ml,nc))
    p0 = None
    p1 = None
    previous = None

    for line in infile:
        match = re.match(r'^G1 X([-\d\.]+) Y([-\d\.]+) E([-\d\.]+)$',
                         line.rstrip())
        if match:
            p2 = [float(s) for s in match.groups()]
            message = should_skip(p0, p1, p2)
            if message:
                # Previous G1 is the midpoint of a straight line.
                stripped = previous.rstrip()
                newline = previous[len(stripped):]
                if verbose:
                    # Prefix with ; to ignore this line when printing.
                    previous = ';%s %s%s' % (stripped, message, newline)
                else:
                    previous = None
                p1 = p2
            else:
                p0 = p1
                p1 = p2
        else:
            p0 = None
            p1 = None
            match = re.match(r'^G1 .*Z([\d\.]+).*',line.rstrip())
            if match:
                lz = match.group(1)
                match = False;
            else:
                match = re.match(r'^; BEGIN_LAYER_OBJECT z=([\d\.]+)',line.rstrip())
            if match:
                nl += 1
                if match.group(1)=="0":
                    #print (nl,ml)
                    lp = "%0.1f" % ((float(nl)*100.0)/float(ml))
                else:
                    lz = match.group(1)
                mline = "M117 L%d/%d %s@%s; Line" %(nl,ml,lp,lz)
                pv(mline)
                outfile.write(mline+'\n')
                for l in al:
                    if (l[0]<0 and ml+l[0]==nl) or (l[0]>=0 and l[0]==nl):
                        outfile.write(l[1]+'\n')
                        pv("Layer {:1d} write: {:s}".format(nl,l[1]))
                match = False
            else:
                match = re.match(r'^; Percent of print ([\d\.]+)',line.rstrip())
            if match:
                if match.group(1)!="0":
                    lp=match.group(1)
                else:
                    lp = "%1.1f" %((100.0*float(nl))/float(ml))
                mline = "M117 L%d/%d %s@%s; Line" %(nl,ml,lp,lz)
                pv(mline)
                outfile.write(mline+'\n')
                match=False
            else:
                match = re.match(r'^; \*\*\* Changing Extruders from',line.rstrip())
            if match and nc>0:
                 outfile.write(lc[c]+'\n')
                 c=c+1                     
        if previous:
            outfile.write(previous)
        previous = line
    if previous:
        outfile.write(previous)
    mline = "M117 L%d/%d 100%%%%%% Done; Line" %(nl,ml)
    outfile.write(mline)
	
    if verbose:
        print(line)
        time.sleep(3)

    outfile.write("\n; Count.py END\n")


if __name__ == '__main__':
    args = sys.argv
#    args += ["-v","box-75inch.gcode","-L-1 ;Last Layer","-L0 ;First Layer"]
    if len(args) < 2:
        sys.exit('usage: Count.py <filename> [-v] [-Lx commands]*')
    verbose = '-v' in args
    pv(args)
    for arg in args[1:]:
        if arg[0]!="-":
            filename = arg
            pv("Print file: " + arg)
            with open(filename) as f:
                lines = f.readlines()            
            with open(filename, 'w') as outfile:
                rewrite(lines, outfile, sys.argv)
