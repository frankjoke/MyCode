$fn=120;

di = 3.05;
do=2.5;
or= 26/2;
ir= 20/2;
tr=or+6/2;
th= 7;
thi=5;
wo=5.5;
i = 0.01;

difference() {
	cylinder(h=di,r=or);
	translate([wo/2,-or,-di]) cube(size=[or,or*2,di*3]);
	translate([-or-wo/2,-or,-di]) cube(size=[or,or*2,di*3]);
}

translate([0,0,di-i]) cylinder(h=di+i,r=ir);
translate([0,0,di+di-i]) cylinder(h=do+i,r=or);
translate([0,0,2*di+do-i]) difference() {
		cylinder(h=th+i,r=tr);
		translate([0,0,th-thi+i]) cylinder(h=thi+2*i,r=or);		
	}

translate([0,0,2*di+do+th/2]) cube(size=[wo/2,or*2+i,th],center=true);
