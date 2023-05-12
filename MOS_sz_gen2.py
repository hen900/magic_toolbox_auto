# ---------------------------------------------------------------------------------------------- 
# NOTE: This is not the most elegant way of interacting with skywater using magic...
# It is, however, effective for generating large batches of gds files with devices.
#  
# This script utilizes the toolkit named sky130A.tcl in the magic tech directory.
# That toolkit was written by Timothy Edwards and does most of the heavy lifting.

# magic must be installed and enabled with the skywater130 technology.
# Efabless reccommends running docker to use the skywater PDK, so it is you are inside the docker.
# If so, you already have all the prerequisits for this to work.
# ---------------------------------------------------------------------------------------------- 

#!/usr/bin/env python3

import os 
import datetime

def main():

    # Path to magic technology file (set or verified by user)
    pdk_path = "/foss/pdks/sky130A/libs.tech/magic" 
    rc_path=pdk_path + "/sky130A.magicrc"
    
    # Length parameters for both nmos and pmos (set by user in microns)
    lengs = [.15,.5,1]
    
    # Width paramereters for both nmos and pmos (set by in microns)
    wids = [.42,1,3,20]
    
    # Mins on length are set by skywater and this prevents any permutation from violating them
    l_mins=[.15,.5] 
    # Note: minimums for 5V and 1.8V devices are not the same
    
    # Everything below is to match naming convention according to skywater parameters  
    mos_ = ["sky130_fd_pr__pfet_","sky130_fd_pr__nfet_"]
    CELL_mos_names = ["pmos","nmos"]
    GDS_mos_names = ["PMOS","NMOS" ]
    CELL_v_names= ["_1_8V_","_5V_"] 
    GDS_v_names= ["_1_8_", "_5"]
    
    #A directory containing generated transistors in labeled DAY_HOUR_MINITE_gen_Q
    now = datetime.datetime.now()
    Q_dir =  str(now.day) + "_" + str(now.hour) + "_" +str(now.minute) + "_gen_Q"
    os.system("mkdir " + Q_dir)

    # The compatibility parameter is defined by skywater and has default values for pmos and nmos below
    # (Most likely not being redefined by user)
    compats= ["sky130_fd_pr__pfet_01v8 sky130_fd_pr__pfet_01v8_lvt sky130_fd_pr__pfet_01v8_hvt sky130_fd_pr__pfet_g5v0d10v5","sky130_fd_pr__nfet_01v8 sky130_fd_pr__nfet_01v8_lvt sky130_fd_bs_flash__special_sonosfet_star sky130_fd_pr__nfet_g5v0d10v5 sky130_fd_pr__nfet_05v0_nvt sky130_fd_pr__nfet_03v3_nvt"]

    # Skywater voltage naming convention
    voltages = ["01v8", "g5v0d10v5"] 

    # Running through all type,voltage and length parameters provived ( excluding lengths that are too small)
    
    for m in range(len(mos_)):
        for v in range(len(voltages)):
            for ll in range(len(lengs)):
                if (lengs[ll] >= l_mins[v]): 
                  for ww in range(len(wids)):
                      
                     # Creates tcl dictionary of parameters that is then imported into the sky130 toolkit
                      with open("/tmp/stored_params", "w") as f:
                          f.write("set par [dict create]\n")
                          f.write("dict set par w " + str(wids[ww]) + "\n")
                          f.write("dict set par l " + str(lengs[ll]) + "\n")
                          f.write("dict set par m 1\n")
                          f.write("dict set par nf 1\n")
                          f.write("dict set par diffcov 100\n")
                          f.write("dict set par polycov 100\n")
                          f.write("dict set par guard 1\n")
                          f.write("dict set par glc 1\n")
                          f.write("dict set par grc 1\n")
                          f.write("dict set par gtc 1\n")
                          f.write("dict set par gbc 1\n")
                          f.write("dict set par tbcov 100\n")
                          f.write("dict set par rlcov 100\n")
                          f.write("dict set par topc 1\n")
                          f.write("dict set par botc 1\n")
                          f.write("dict set par poverlap 0\n")
                          f.write("dict set par doverlap 1\n")
                          f.write("dict set par lmin "+ str(l_mins[v])+ "\n")
                          f.write("dict set par wmin 0.42\n")
                          f.write("dict set par compatible {"+compats[m]+"}\n")
                          f.write("dict set par full_metal 1\n")
                          f.write("dict set par viasrc 100\n")
                          f.write("dict set par viadrn 100\n")
                          f.write("dict set par viagate 100\n")
                          f.write("dict set par viagb 0\n")
                          f.write("dict set par viagr 0\n")
                          f.write("dict set par viagl 0\n")
                          f.write("dict set par viagt 0\n")
                      f.close()
    
                      # Meaurements are expected in nm
                      rescaled_w=str(int(wids[ww]*100))
                      rescaled_l=str(int(lengs[ll]*100))   
                       
                      renamed_cell = "w" + rescaled_w+ "_l" + rescaled_l+ CELL_v_names[v] + CELL_mos_names[m]
                      
                      gds_name = Q_dir + "/" + "W" + rescaled_w + "_L" + rescaled_l + "_"+ GDS_mos_names[m] + GDS_v_names[v]+ ".gds"
                      
                     # The renamed cell naming convention is arbitrary and user defined
                      device_name = mos_[m] + voltages[v] 
                      print(device_name)
                      # Temporary shell script of commands needed to run the tcl with skywater technology
                      with open("/tmp/magic_commands", "w") as c:
                          c.write("magic -T " + pdk_path + "/sky130A.tech" + " -rcfile " + rc_path + " -dnull -noconsole <<EOF\n")       
                          c.write("source " + pdk_path + "/sky130A.tcl \n")
                          c.write("source /tmp/stored_params \n")
                          c.write("cellname rename (UNNAMED) " + renamed_cell + "\n")
                          c.write("sky130::" + device_name+ "_draw \\$par\n" )
                          c.write("gds write " + gds_name + "\n")
                          c.write("exit\n")
                          c.write("EOF\n")
                      c.close()

                      # ...........................................................................................
       
                      # Uncomment the following line if you want to execute the shell script and generate gds files
                      # Otherwise the magic commands will only be generated, not run

                      os.system("bash /tmp/magic_commands")

                else:
                      print("#######################Size Violation######################## :" + device_name)
                     # ...........................................................................................       

if __name__ == "__main__":
    main()

