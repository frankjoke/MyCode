module connector() {
	translate ([-4.8,-8.2,0]) import("bbFlexSeg_WN2.stl");
}

module top() {
	translate ([0,0,1]) union() {
	translate ([0,0,-15.1]) 
		difference() {
			connector();
		 	translate([0,0,6.99]) 
				cube([20,21,16],center=true);
		}
	cube([10,10,2],center=true);
	}
}

module bottom() {
	translate ([0,0,1]) union() {
	translate ([0,0,16]) rotate ([0,180,0]) difference() {
		connector();
		 translate([0,0,24]) cube([20,21,16],center=true);
	}
	cube([10,10,2],center=true);
	}
}

translate ([11,11,0]) connector();
translate ([-11,11,0]) connector();
translate ([11,-11,0]) bottom();
translate ([-11,-11,0]) top();
translate ([11,-33,0]) connector();
translate ([-11,-33,0]) connector();
