// AE4901 5-mm GL5537-1 educational test-cap -- GENERATIVE PARAMETRIC CAD
// Optical face is nominally z=0, top aperture at z=mask_depth_mm.
// Geometry is a simplified opaque circular opening; no claim of optical qualification.
// Print rotated 180 degrees (aperture roof on print bed); dark/opaque matte material.
// Verify actual LDR case diameter with calipers and adjust clearance before assembly.
// Use: openscad -o mask.stl -D 'mask_depth_mm=0.6' -D 'aperture_radius_mm=3.6' ldr_mask_parametric.scad
$fn=96;
part = "mask"; // mask | bare
mask_depth_mm=0.6; // z=0 is top of photosensitive disk
aperture_radius_mm=3.6;
aperture_offset_mm=0.0; // offset along x; experimental directional mask
recess_width_mm=4.15; // radius of open optical cavity behind aperture roof
lid_thickness_mm=1.0;
case_radius_mm=2.675; // adjust for actual 5-mm LDR diameter, clearance included
case_depth_mm=3.0;
outer_radius_mm=5.35;

module base_collar(){
 difference(){
  translate([0,0,-case_depth_mm]) cylinder(r=outer_radius_mm,h=case_depth_mm);
  translate([0,0,-case_depth_mm-0.1]) cylinder(r=case_radius_mm,h=case_depth_mm+0.2);
 }
}
module optical_roof(){
 difference(){
  union(){
   cylinder(r=outer_radius_mm,h=mask_depth_mm+lid_thickness_mm);
  }
  // cavity extends from detector plane until underside of top aperture roof
  translate([0,0,-0.1]) cylinder(r=recess_width_mm,h=mask_depth_mm+0.2);
  // opening placed above recessed cavity, optionally offset in x
  translate([aperture_offset_mm,0,mask_depth_mm-0.01])
     cylinder(r=aperture_radius_mm,h=lid_thickness_mm+0.1);
 }
}
if(part=="bare") base_collar();
else union(){base_collar();optical_roof();}
