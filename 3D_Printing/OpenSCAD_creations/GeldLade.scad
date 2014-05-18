$fn=120;

ow=100;
oh=30;
ww=2;
iw=ow-2*ww;
ih=oh-2*ww;
r=70;
d=15;
i=0.1;

module mycube(w,h,r,d) {
	difference() {
		cube([w,w,h],center=true);
		translate([0,0,h/2+r-d]) sphere(r=r);
	}

}

module lade(l,h,w) {
	cube([l+i,l+i,w],center=true);
	translate([0,w/2-l/2,h/2-i-w/2]) cube([l+i,w,h],center=true);
}

translate([0,0,ow/2]) rotate([270,0,90]) difference() {
	mycube(ow,oh,r,d);
	mycube(iw,ih,r,d);
	translate([0,3*i-ww,ww-oh/2+i]) lade(iw+ww/2,oh-ww/2+i,ww+2*i);
}

translate([ow,0,ww/2+i]) lade(iw+ww/2,oh-ww/2,ww+2*i);
