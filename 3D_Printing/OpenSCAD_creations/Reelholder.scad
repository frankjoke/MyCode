$fn=36;

sh = 11.7;
dspo= 21;
dspi= 6;
dsp=dspi-1;
boden=2;
hboden=5;
boden2=boden+hboden;
ns = 3;
nl = 8;
h = sh*ns+boden2;
th = h+boden;
wand=3;
tw = wand/2;
dist= dspo + 3;
l = nl * dist+wand*2;
w = 2 * dist+wand*2;
n = floor(l / dist /2)-1;

module rhbase() {
	difference() {
		translate([0,0,h/2]) 
			cube([l,w,h],center=true);
		translate([0,0,boden]) 
			difference() {
				translate([0,0,(h+boden2+1)/2]) 
					cube([l+1,w+1,h+boden2+1],center=true);
				translate([0,0,(hboden)/2]) 
					cube([l-wand,w-wand,hboden+0.01],center=true);
				for ( y = [-1 : 2 : 1] ) {
					for ( x = [-dist/2*abs(y)-dist*n : dist : dist*n+dist/2*abs(y)] ) {
						translate([x,y*dist/2,-1])
							cylinder(r=dsp/2,h=h+boden2);
					}
				}
			}
	}
}

module rhcover() {
	translate([0,0,th]) 
		rotate([180,0,0]) 
			difference() {
				translate([0,0,th/2]) 
					cube([l,w,th],center=true);
				translate([0,0,hboden/2-0.01]) 
					cube([l-tw,w-tw,hboden],center=true);
				translate([0,0,(th-boden)/2-0.02]) 
					cube([l-wand,w-wand,th-boden],center=true);
	}
}

rhbase();
translate([0,w+5,0]) 
	rhcover();

