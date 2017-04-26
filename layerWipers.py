#gcode postprocessor for slic3r
#wishlish
#do smart cooldown (for long waits between heads)
#smart heatup
#extrude length after toolchange varies based on time btwn 
#does smart blocking of layers: i.e. finds all lines between tool changes, 
#checks if multiple blocks printing on same z,
#will have to do such discoveries for above two comments regardless

#should rip T0 Home and to Y-pos for T1 

#on open, be sure to clear the bed
#on close, do flourish w/ head presentation

import sys
import re

gcode = open(sys.argv[1])
out = open(sys.argv[1] + "-pp.gcode", 'w') #going to write to this new bb +".gcode",

b4lyr = re.compile("; before layer change\n")
apreslyr = re.compile("; after layer change\n")

toolchng = re.compile("; tool change\n")

t0 = re.compile("T0\n")
t1 = re.compile("T1\n")

top = re.compile("; top of g code\n")
bottom = re.compile("; end of g code\n")

temps = re.compile("M190|M109|M140|M104")

rtrctz = "; b4 tool change: retracting z\nG91\nG1 Z5.0 F3000\nG90 ;fin\n"

toolchngflag = "; TOOL\n"

extruder0 = (
			"G91 ; START EX0 BLOCK\n"
			"G1 Z5 F1500\n"
			"G90\n"

			"T1\n" # THE FOLLOWING IS BLOCK FOR SWAP to ex0
			"G1 X238.7 F8000\n" # ;park and retract t1
			"T0\n" # ;swap to t0

			"G1 X5.0\n"
			"G1 Y10.0\n" # ;t0 pre-purge
			"G1 X-18.0\n"

			"G91\n"
			"G1 E0.25 F200\n" # purge
			"G1 X-18 F500\n" #wipe
			"G1 Y20 F4000\n"
			"G1 Y-15\n"
			"G1 Y40\n"
			"G1 X36 F8000\n"
			"G90 ; FIN EX0 BLOCK\n"

			) 

extruder1 = (
			"G91 ; START EX1 BLOCK\n"
			"G1 Z5 F1500\n"
			"G90\n"

			"T0\n" # THE FOLLOWING IS BLOCK FOR SWAP TO ex1
			"G1 X-39.0 F8000\n" #  ;park and retract t0
			"T1\n" #  ;swap to t1

			"G1 X219\n"
			"G1 Y278\n"

			"G91\n"
			"G1 E0.25 F200\n" #purge
			"G1 X18 F500\n" #wipe
			"G1 Y-20 F4000\n"
			"G1 Y15\n"
			"G1 Y-40\n"
			"G1 X-20 F8000\n"
			"G90 ; FIN EX1  BLOCK\n"

			)

topSequence = (
			"; START\n"
			"T0\n"
			)

endSequence = (
			"; FIN Sequence\n"
			"T1\n" 
			"G1 X238.7 F8000\n" # ;park and retract t1
			"T0\n"
			"G1 X-39.0 F8000\n" #  ;park and retract t0

			"G1 Z125 F1500\n"

			"T1\n"
			"G1 X160 Y100 F8000\n"
			"M104 S0\n"
			"T0\n"
			"G1 X50 F8000\n"
			"M104 S0\n"

			"M140 S0\n"
			)

for l in gcode:
	if re.search(b4lyr, l) is not None:
		out.write(l) #rtrctz
	elif re.search(apreslyr, l) is not None:
		out.write(l) #dropz
	elif re.search(toolchng, l) is not None:
		out.write(l)

	elif re.search(t0, l) is not None:
		out.write(extruder0)
	elif re.search(t1, l) is not None:
		out.write(extruder1)

	elif re.search(top, l) is not None:
		out.write(topSequence)
	elif re.search(bottom, l) is not None:
		out.write(endSequence)
	#elif re.search(temps, l) is not None: #for motion debug
	#	out.write("; wiped temp line\n")
	else:
		out.write(l)