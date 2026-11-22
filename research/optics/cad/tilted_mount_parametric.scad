// AE4901 8.16-degree replaceable tilted socket base, print 12 identical mounts.
// Mount local Z is CubeSat face normal, local X/Y define requested tilt azimuth.
// Reference optical axis: rotate XZ plane by azimuth around face normal.
// IMPORTANT: mounting assumes mask cap OD 10.7 mm; verify your print fit.
$fn=96;
tilt_deg=8.1615; // from +/-10deg rotation about spacecraft body diagonal
azimuth_deg=0;
base_side_mm=19;
base_thickness_mm=3;
socket_outer_radius_mm=8;
socket_inner_radius_mm=5.55; // 10.7 mm mask slips in with 0.4 mm diametral clearance
socket_length_mm=2.1; // holds cap collar; cap roof should protrude above socket for optical clearance
module tilted_socket(){
 difference(){
  cylinder(r=socket_outer_radius_mm,h=socket_length_mm);
  translate([0,0,-.1]) cylinder(r=socket_inner_radius_mm,h=socket_length_mm+.2);
 }
}
module mount(){
 difference(){
  union(){
   translate([-base_side_mm/2,-base_side_mm/2,0]) cube([base_side_mm,base_side_mm,base_thickness_mm]);
   translate([0,0,base_thickness_mm-.3]) rotate([0,0,azimuth_deg]) rotate([0,tilt_deg,0]) tilted_socket();
  }
  // central clearance for case leads and sensor body
  translate([0,0,-.2]) cylinder(r=3.1,h=base_thickness_mm+1);
  // optional two M2 base fixing holes, 15-mm spacing
  for(x=[-7.5,7.5]) translate([x,0,-.2]) cylinder(r=1.1,h=base_thickness_mm+.4);
 }
}
mount();
