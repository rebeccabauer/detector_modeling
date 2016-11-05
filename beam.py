from shapely import affinity, geometry
import shapely
from matplotlib import pyplot
import constants


class Beam(object):
    """
    Stores the shape of the laser beam on the detector
    """
    def __init__(self, radius, x=0.0, y=0.0):
        """
        :param radius: beam radius
        :param x: beam center x-coordinate
        :param y: beam center y-coordinate
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.shape = shapely.geometry.Point(x, y).buffer(radius)  # create circle of given radius

    def translate(self, dx, dy):
        """
        Move the beam dx in the x direction and dy in the y direction
        """
        self.x += dx
        self.y += dy
        self.shape = shapely.affinity.translate(self.shape, dx, dy)

    def recenter(self, new_x, new_y):
        """
        Set the beam's center to a different location
        """
        self.shape = shapely.affinity.translate(self.shape, new_x-self.x, new_y-self.y)
        self.x = new_x
        self.y = new_y

    def trajectory(self, x_i, y_i, x_f, y_f):
        """
        Returns a trajectory shape - essentially just the path of the laser over the detector
        Parameters are starting and ending coordinates (so this only works for linear paths)
        """
        route = geometry.LineString([(x_i, y_i), (x_f, y_f)])
        return route.buffer(self.radius)


class BeamOverlap(object):
    """
    Stores a beam and a detector, sweeps the beam across the detector and displays the results
    """
    def __init__(self, detector, beam):
        self.detector = detector
        self.beam = beam

    def display(self):
        """
        Display the beam superimposed on the detector
        """
        self.detector.display(self.beam.shape)

    def linear_sweep(self, x_i, y_i, x_f, y_f, points=200):
        """
        Sweep the laser across the detector, return the resulting displacement calculations after plotting
        :param x_i, y_i, x_f, y_f: initial and final centerpoints of the laser
        :param points: number of points to calculate laser-detector intersection at
        :return: for both x and y, return a list of physical centers and corresponding calculated displacement values
        """
        self.beam.recenter(x_i, y_i)
        dx = (x_f - x_i)/float(points)      # increment values
        dy = (y_f - y_i)/float(points)
        x_real = []
        y_real = []
        x_values = []
        y_values = []
        for i in range(points):
            self.beam.translate(dx, dy)
            displacement = self.detector.calculate_displacement(self.beam)
            if displacement is not None:     # check if there was any overlap between laser and detector
                x_values.append(displacement[0])
                y_values.append(displacement[1])
                x_real.append(x_i + i*dx)
                y_real.append(y_i + i*dy)
        self.plot_sweep(x_real, x_values, y_real, y_values)     # call plot_sweep to plot results
        return x_real, x_values, y_real, y_values

    def plot_sweep(self, x_real, x_values, y_real, y_values):
        """
        Display 3 sub-plots with info on the sweep
        """
        pyplot.figure(1, figsize=(8, 15))

        # First subplot - x displacement
        ax = pyplot.subplot(311)
        displacement_plot(ax, x_real, x_values, 'x')

        # Second subplot - y displacement
        ax = pyplot.subplot(312)
        displacement_plot(ax, y_real, y_values, 'y', c1='g', c2=constants.ORANGE)

        # Third subplot - trajectory
        ax = pyplot.subplot(313)
        pyplot.plot(x_real, y_real, 'k:')
        path = self.beam.trajectory(x_real[0], y_real[0], x_real[-1], y_real[-1])
        self.detector.plot_detector(ax, path, title="Detector and Laser Path")
        ax.autoscale()
        pyplot.show()
        ax.grid()


def derivative(x, y):
    """
    Calculate derivatives based on the provided x and y value lists
    :return: derivative values and corresponding x-values
    """
    derivatives = []
    new_x = []
    for i in range(1, len(y)):
        deriv = (y[i] - y[i-1])/(x[i] - x[i-1])
        derivatives.append(deriv)
        new_x.append((x[i] + x[i-1])/2.0)
    return new_x, derivatives


def displacement_plot(subplot, real, disp, var_name, c1='r', c2='b'):
    """
    Helper function for creating displacement plots
    :param subplot:
    :param real: physical displacement
    :param disp: sensor-calculated displacement
    :param var_name: variable name (for use in title/legend)
    :param c1: color of displacement line
    :param c2: color of derivative line
    """
    disp_title = "Calculated {0} Displacement vs Laser {0}-Coordinate"
    disp_handle = "Calculated {} displacement"
    deriv_handle = "{} displacement derivative"

    x, deriv = derivative(real, disp)
    pyplot.plot(real, disp, c1, linewidth=3, label=disp_handle.format(var_name))
    pyplot.plot(x, deriv, c2, linewidth=3, label=deriv_handle.format(var_name))
    subplot.set_title(disp_title.format(var_name))
    subplot.grid()
    subplot.legend(loc='best', framealpha=0.5)
