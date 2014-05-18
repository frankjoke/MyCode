sides=5;
diameter=80;
length=120;


module vase_edges(h2=length*1.5,r=length,d=diameter/4,m=length/7) {
	$fn=120;
	
	translate([0,0,length/2]) difference() {
		cylinder(h=length,r=3*d+length/sides,center=true);
		
		for ( i = [0 : 360/sides : 360*(sides-1)/sides] ) {
			rotate([0,0,i]) 
				translate([length+d,h2/2,-m]) 
					rotate([90,0,0])
						cylinder(r=r,h=h2);
		}
	}

}

module vase_twisted(twist=120,quirl=0) {
	
	linear_extrude(height=length, center=false, twist=twist,
		slices=length*5,scale=1.5)
				translate([quirl, 0, 0]) circle(r = diameter/2, $fn=sides);
}

//vase_edges(d=diameter/5);
//translate([diameter*1.5,0,0]) 
	vase_twisted(twist=240); 