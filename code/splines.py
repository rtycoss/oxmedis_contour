from keras import *
from keras import backend as K
import numpy as np
import math
import matplotlib.path as mpath
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import bezier

from utils import *
closed = True

class single_curve:
    def __init__(self, this_knot):
        self.p0 = this_knot.k.c
        self.p1 = this_knot.k.h2
        self.p2 = this_knot.k1.h1
        self.p3 = this_knot.k1.c

        self.nodes = np.asfortranarray([
                    [self.p0.x, self.p1.x, self.p2.x, self.p3.x],
                    [self.p0.y, self.p1.y, self.p2.y, self.p3.y],])

    def __eq__(self, other):
        if (self.p0 == other.p0):
            return True
        else:
            return False

    def get_curve(self):
        curve = bezier.Curve(self.nodes, degree=3).reduce_()
        return curve

class curved_shape:
    def __init__(self, chained_knots):
        self.curves = []
        for knot in chained_knots:
            c = single_curve(knot)
            self.curves.append(c.get_curve())
        #print(self.curves)

    def get_poly(self):
        return self.curves
        #self.shape = bezier.CurvedPolygon(edges=tuple(self.curves))

def average_dist(truth_pixels, poly):
    distances = []
    last_p = point(0,0)
    for curve in poly:
        for i in np.arange(0,1,0.05):
            eval = curve.evaluate(i)
            p = point(round(eval[0,0]), round(eval[1,0]))
            if not(p == last_p):
                #print(p.x, p.y)
                last_p = p
                smallest = 1000
                for points in truth_pixels:
                    if distance(p, points) < smallest:
                        smallest = distance(p, points)
                distances.append(smallest)
                #print(smallest)
    return sum(distances)/len(distances)

def drawCurve(poly, distinctMap, colour):
    for curve in poly:
        for i in np.arange(0,1,0.05):
            eval = curve.evaluate(i)
            #print(eval)
            distinctMap = addSquare(distinctMap, point(round(eval[0,0]), round(eval[1,0])), False, colour)
    return distinctMap
