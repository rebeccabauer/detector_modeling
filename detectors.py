from shapely import geometry
import shapely
from matplotlib import pyplot
from descartes import PolygonPatch
import constants


# Functions for generating single or multiple shapes
def rectangle(x, y, width, height):
    """
    Create a rectangle using one of the corners, and the width and height relative to that corner.
    Width and height can be positive or negative.
    """
    points = [(x,y), (x+width,y), (x+width, y+height), (x,y+height)]
    return shapely.geometry.Polygon(points)


def quad_rectangles(x_offset, y_offset, width, height):
    """
    Create four rectangles centered around the origin
    :param x_offset: distance from closest corner to origin on x-axis
    :param y_offset: distance from closest corner to origin on y-axis
    :param width: rectangle width
    :param height: rectangle height
    :return: list of rectangles
    """
    rectangles = []
    x_coeffs = (1, 1, -1, -1)
    y_coeffs = (1, -1, -1, 1)
    for i, x_coeff in enumerate(x_coeffs):
        y_coeff = y_coeffs[i]
        square = rectangle(x_coeff * x_offset,
                           y_coeff * y_offset,
                           x_coeff * width,
                           y_coeff * height)
        rectangles.append(square)
    return rectangles


class Detector(object):
    """
    Main detector class. Stores pixel info and methods for calculating beam overlap
    """
    def __init__(self, pixel_list):
        self.pixels = pixel_list

    def overlap(self, beam):
        """
        Intersects the provided beam with the detector sections and returns the resulting shapes
        """
        overlaps = [pixel.intersection(beam.shape) for pixel in self.pixels]
        return overlaps

    def overlap_areas(self, beam):
        """
        Return the areas of the sections of the detector that overlap with the provided beam
        """
        overlaps = self.overlap(beam)
        areas = [shape.area for shape in overlaps]
        return areas

    def calculate_displacement(self, beam):
        """
        Calculate the beam's displacement on the detector
        :return: displacement as a tuple, or None if no overlap
        """
        areas = self.overlap_areas(beam)
        if sum(areas) == 0:
            return None
        x = ((areas[0]+areas[1]) - (areas[2]+areas[3])) / sum(areas)
        y = ((areas[0] + areas[3]) - (areas[1] + areas[2])) / sum(areas)
        return x, y

    def plot_detector(self, subplot, beam=None, title="Detector"):
        """
        Plot the detector on the provided subplot
        :param beam: optional object to be overlaid on detector
        :param title: figure title
        """
        for pixel in self.pixels:
            subplot.add_patch(PolygonPatch(pixel, alpha=0.8, fc=constants.NAVY2))
        if beam is not None:
            beam_patch = PolygonPatch(beam, alpha=0.7, fc=constants.YELLOW, ec=constants.GRAY)
            subplot.add_patch(beam_patch)
        subplot.set_title(title)

    def display(self, beam=None, title="Detector"):
        """
        Display the detector in its own figure
        :param beam: optional object to be overlaid on detector
        :param title: figure title
        """
        fig = pyplot.figure(1, figsize=(5, 5), dpi=90)
        ax = fig.add_subplot(111)
        self.plot_detector(ax, beam, title)
        ax.autoscale()
        pyplot.show()


# Some Detector subclasses for the most common detector shapes
class SquareDetector(Detector):
    def __init__(self, pixel_width, pixel_gap):
        """
        :param pixel_width: width of a single pixel
        :param pixel_gap: gap between adjacent pixels
        """
        offset = pixel_gap/2.0
        pixels = quad_rectangles(offset, offset, pixel_width, pixel_width)
        super(SquareDetector, self).__init__(pixels)


class CircleDetector(Detector):
    def __init__(self, radius, pixel_gap):
        """
        :param radius: radius of the detector
        :param pixel_gap: gap between adjacent pixels
        """
        circle = geometry.Point(0.0, 0.0).buffer(radius)
        offset = pixel_gap/2.0
        squares = quad_rectangles(offset, offset, radius, radius)

        # create the pixels by intersecting the squares with the border circle of the detector
        pixels = []
        for square in squares:
            pixels.append(square.intersection(circle))
        super(CircleDetector, self).__init__(pixels)


