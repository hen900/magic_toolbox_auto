#!/usr/bin/env python3

import os
import datetime

def main():

    # Path to magic technology file (set or verified by user)
    pdk_path = "/foss/pdks/sky130A/libs.tech/magic"
    rc_path = os.path.join(pdk_path, "sky130A.magicrc")

    # Length parameters for both nmos and pmos (set by user in microns)
    lengths = [0.15, 0.5, 1]

    # Width parameters for both nmos and pmos (set by in microns)
    widths = [0.42, 1, 3, 20]

    # Mins on length are set by skywater and this prevents any permutation from violating them
    length_mins = [0.15, 0.5]
    # Note: minimums for 5V and 1.8V devices are not the same

    # Everything below is to match naming convention according to skywater parameters
    sky_mos_names = ["sky130_fd_pr__pfet", "sky130_fd_pr__nfet"]
    mos_types = ["pmos", "nmos"]

    # These depend on how you want the output gds named
    gds_mos_names = ["PMOS", "NMOS"]
    gds_voltage_names = ["_1_8_", "_5"]

    # A directory containing generated transistors in labeled DAY_HOUR_MINUTE_gen_Q
    now = datetime.datetime.now()
    created_dir_name = now.strftime("%d_%H_%M_gen_Q")
    os.makedirs(created_dir_name, exist_ok=True)

    # The compatibility parameter is defined by skywater and has default values for pmos and nmos below
    # (Most likely not being redefined by user)
    compats = [
        "sky130_fd_pr__pfet_01v8 sky130_fd_pr__pfet_01v8_lvt sky130_fd_pr__pfet_01v8_hvt sky130_fd_pr__pfet_g5v0d10v5",
        "sky130_fd_pr__nfet_01v8 sky130_fd_pr__nfet_01v8_lvt sky130_fd_bs_flash__special_sonosfet_star sky130_fd_pr__nfet_g5v0d10v5 sky130_fd_pr__nfet_05v0_nvt sky130_fd_pr__nfet_03v3_nvt"
    ]

    # Skywater voltage naming convention
    sky_voltage_names = ["01v8", "g5v0d10v5"]

    # Running through all type, voltage, and length parameters provided (excluding lengths that are too small)
    for mos_type in mos_types:
        for voltage in sky_voltage_names:
            for length in lengths:
                if length >= length_mins[voltage]:
                    for width in widths:
                        # Creates tcl dictionary of parameters that is then imported into the sky130 toolkit
                        with open("/tmp/stored_params", "w") as f:
                            f.write(f"set par [dict create]\n")
                            f.write(f"dict set par w {width}\n")
                            f.write(f"dict set par l {length}\n")
                            f.write(f"dict set par m 1\n")
                            f.write(f"dict set par nf 1\n")
                            f.write(f"dict set par diffcov 100\n")
                            f.write(f"dict set par polycov 100\n")
                            f.write(f"dict set par guard 1\n")
                            f.write(f"dict set par glc 1\n")
                            f.write(f"dict set par grc 1\n")
                            f.write(f"dict set par gtc 1\n")
                            f.write(f"dict set par gbc 1\n")
                            f.write(f"dict set par tbcov 100\n")
                            f.write(f"dict set par rlcov 100\n")
                            f.write(f"dict set par topc 1\n")
                            f.write(f"dict set par botc 1\n")
                            f.write(f"dict set par poverlap 0\n")
                            f.write(f"dict set par doverlap 1\n")
                            f.write(f"dict set par lmin {length_mins[voltage]}\n")
                            f.write(f"dict set par wmin 0.42\n")
                            f.write(f"dict set par compatible {{{compats[mos_types.index(mos_type)]}}}\n")
                            f.write(f"dict set par full_metal 1\n")
                            f.write(f"dict set par viasrc 100\n")
                            f.write(f"dict set par viadrn 100\n")
                            f.write(f"dict set par viagate 100\n")
                            f.write(f"dict set par viagb 0\n")
                            f.write(f"dict set par viagr 0\n")
                            f.write(f"dict set par viagl 0\n")
                            f.write(f"dict set par viagt 0\n")
                        # Measure ments are converted to um
                        rescaled_w = int(width * 100)
                        rescaled_l = int(length * 100)
                        # The names of the the top and subcell
                        # In this case the topcell is named something like "w2000_l100_nmos"
                        # In this case the bottom cell is named something like "sky130_fd_pr__nfet_g5v0d10v5"
                        topcell_name = f"w{rescaled_w}_l{rescaled_l}_{mos_type}"
                        subcell_name = f"{sky_mos_names[mos_types.index(mos_type)]}{voltage}"
                        # Create the directory if it doesn't exist
                        os.makedirs(created_dir_name, exist_ok=True)
                        # gds_name refers to the naming convention you want, in this case it is something like "W42_L15_NMOS_1_8_.gds"
                        gds_name = os.path.join(created_dir_name, f"W{rescaled_w}_L{rescaled_l}_{gds_mos_names[mos_types.index(mos_type)]}{gds_voltage_names[sky_voltage_names.index(voltage)]}.gds")

                        # Temporary shell script of commands needed to run the tcl with skywater technology
                        with open("/tmp/magic_commands", "w") as c:
                            c.write(f"magic -T {os.path.join(pdk_path, 'sky130A.tech')} -rcfile {rc_path} -dnull -noconsole <<EOF\n")
                            c.write(f"source {os.path.join(pdk_path, 'sky130A.tcl')}\n")
                            c.write("source /tmp/stored_params\n")
                            c.write(f"cellname rename (UNNAMED) {topcell_name}\n")
                            c.write(f"load {topcell_name}\n")
                            c.write(f"cellname create {subcell_name}\n")
                            c.write(f"getcell {subcell_name}\n")
                            c.write(f"select {subcell_name}\n")
                            c.write(f"sky130::{subcell_name}_draw $par\n")
                            c.write(f"select top\n")
                            c.write(f"expand\n")
                            c.write(f"delete\n")
                            c.write(f"writeall force {gds_name}\n")
                            c.write("exit\n")
                            c.write("EOF\n")

                        # Run the shell script
                        os.system("bash /tmp/magic_commands")

    print("Completed transistor generation!")

if __name__ == "__main__":
    main()
