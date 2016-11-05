from detectors import *
from beam import *

# - EXAMPLES -
# model circular photodiode SD 197-23-21-041
# Dimensions (mm):
CIRCLE_GAP = 0.03
DIAMETER = 4.98
RADIUS = DIAMETER/2
circle_detector = CircleDetector(RADIUS, CIRCLE_GAP)

# model square photodiode SD 085-23-21-021
# Dimensions (mm):
SQUARE_GAP = 0.01
PIXEL_SIDE = 1.5
square_detector = SquareDetector(PIXEL_SIDE, SQUARE_GAP)

# test out a circular diode with large gaps
big_gaps = CircleDetector(RADIUS, 0.2*RADIUS)

# Create a beam (essentially just a circle)
BEAM_RADIUS = RADIUS/6
beam = Beam(BEAM_RADIUS)

# Create an instance of BeamOverlap, which handles interaction between the beam and sensor
overlap = BeamOverlap(big_gaps, beam)

# Sweep the beam over the detector and graph the results
overlap.linear_sweep(-1*RADIUS, -1*RADIUS, RADIUS, RADIUS)      # centered diagonal sweep
overlap.linear_sweep(-1*RADIUS/3, -1*RADIUS, RADIUS, RADIUS/2)  # off-center sweep

# Calculate displacement for a single laser position:
beam.recenter(0.5, 0.3)   # new beam position
x_disp, y_disp = square_detector.calculate_displacement(beam)       # calculate displacements
print "x displacement is {}, and y displacement is {}.".format(x_disp, y_disp)

# Display the beam on the photodiode:
overlap.display()