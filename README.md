# magic_toolbox_auto
Python 3 written to automatically generate devices using the tcl toolbox provided.  .GDS files can be automatically generated according to user defined parameters. 

**NOTE: This is not the most elegant way of interacting with skywater using magic.**
It is, however, effective for generating large batches of gds files with devices.
  
 This script utilizes the toolkit named sky130A.tcl in the magic tech directory.
 That toolkit was written by Timothy Edwards and does most of the heavy lifting.

## Prerequisites
 Magic must be installed and enabled with the skywater130 technology.
 Efabless recommends running docker to use the skywater PDK, so it is you are inside the docker.
 If so, you already have all the prerequisites for this to work.

##  Running the Script

The script is setup by default to recursively generate nmos and pmos devices with all combinations of the following parameters 

- voltages : 1.8V, 5V 
- lengths : .15 microns .5 microns, 1 micron 
- widths : .42 microns 1 micron ,3 microns ,20 microns 
   
A time stamped directory is created with all gds files inside

## Naming Convention

An example of the naming convention used for the **GDS filenames*** is: 

- W42_L50_NMOS_1_8_.gds

This is a 1.8V NMOS of width 42 microns and length 50 microns. Any convention could be used here according to user preference.

An example of the naming convention **defined by skywater** for **device names** is:
- sky130_fd_pr__pfet_01v8

The naming convention is best outlined by skywater's own docs here: https://skywater-pdk.readthedocs.io/en/main/rules/device-details.html
![image](https://github.com/hen900/magic_toolbox_auto/assets/25012642/b22ad74e-c656-43dd-a8f5-a9e43a522ffa)
