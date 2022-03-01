#import matplotlib.pyplot as plt
from keras import *
from keras import backend as K
import numpy as np
import math
import os
from keras.preprocessing.image import save_img

center_range = 1
#converts a 2D image to a 1D list of values (x_coord, y_coord, intensity)
#find distinct heatmaps and return the centre point for each one
#centre point is returned as in integer
class point:
    def __init__(self, x_val, y_val):
        self.x = x_val
        self.y = y_val

    def __eq__(self, other):
        if (self.x == other.x) and (self.y == other.y):
            return True
        else:
            return False

class Wildcard:
    def __eq__(self, anything):
        return True

#############################
#MATHEMATICAL FUNCTIONS
#############################
def distance(p1, p2):
    temp = (p2.x-p1.x)**2 + (p2.y-p1.y)**2
    if temp <= 0:
        return 0
    else:
        return math.sqrt(temp)

#is point P on the right of the line from A to B
def rightOf(A, B, P):

    # Subtracting co-ordinates of
    # point A from B and P, to
    # make A as origin
    B.x -= A.x
    B.y -= A.y
    P.x -= A.x
    P.y -= A.y

    cross_product = B.x * P.y - B.y * P.x

    # if cross product is positive P is on the right of the line
    if (cross_product > 0):
        return True
    else:
        return False


#angle from A to P around B counter-clockwise
def getAngle(A, B, P):
    ang = math.degrees(math.atan2(P.y-B.y, P.x-B.x) - math.atan2(A.y-B.y, A.x-B.x))
    return ang + 360 if ang < 0 else ang

def angleOrdered(c, p0, ang, p1):
    angle = getAngle(p0, c, p1)
    return abs(angle - ang)


def adjacent(pix1, pix2, hops):
    [val1, p1] = pix1
    [val2, p2] = pix2
    if distance(p1, p2) <= hops:
        return True
    else:
        return False


#############################


#############################
#LANDMARK FUNCTIONS
#############################
def neighbours(pix, max_x, max_y):
    neighbour_list = []
    if pix.x > 0:
        neighbour_list.append(point((pix.x - 1), (pix.y)))
        if pix.y > 0:
            neighbour_list.extend([point((pix.x - 1), (pix.y - 1)), point((pix.x), (pix.y - 1))])
        if pix.y + 1 < max_y:
            neighbour_list.extend([point((pix.x - 1), (pix.y + 1)), point((pix.x), (pix.y + 1))])
    if pix.x + 1 < max_x:
        neighbour_list.append(point((pix.x + 1), (pix.y)))
        if pix.y > 0:
            neighbour_list.append(point((pix.x + 1), (pix.y - 1)))
        if pix.y + 1 < max_y:
            neighbour_list.append(point((pix.x + 1), (pix.y + 1)))
    return neighbour_list

def center_point(pixels):
    pixels.sort(key = lambda a: [a[0], a[1].x, a[1].y], reverse=True)
    [val, location] = pixels[0]
    center_pixels = [p for [val0, p] in pixels if (val - val0) <= center_range]
    center_len = len(center_pixels)

    x_sum, y_sum = 0, 0
    for p in center_pixels:
        x_sum = x_sum + p.x
        y_sum = y_sum + p.y
    return point(round(x_sum/center_len), round(y_sum/center_len))

def onBoundary(pix, pixels, max_x, max_y):
    to_check = neighbours(pix, max_x, max_y)
    for nextdoor in to_check:
        if nextdoor not in pixels: return True
    return False

def getBoundary(pixels, max_x, max_y):
    boundary = []
    just_points = [p for [v, p] in pixels]
    for [v, p] in pixels:
        if onBoundary(p, just_points, max_x, max_y):
            boundary.append(p)
    return boundary

def op_point(p, c, boundary):
    boundary.sort(key = lambda val: angleOrdered(c, p, 180, val))
    best_point = boundary[0]
    angle = angleOrdered(c, p, 180, best_point)
    dist = distance(p, best_point)
    for point in boundary:
        if (angleOrdered(c, p, 180, point) < angle + 5) and (distance(p, point) > dist):
            best_point = point
            dist = distance(p, point)
    return best_point
#############################


#############################
#IMAGE FUNCTIONS
#############################
def addSquare(map, center, big, colour):
    map[center.x, center.y, :] = colour
    if big:
        for nextdoor in neighbours(center, map.shape[0], map.shape[1]):
            map[nextdoor.x, nextdoor.y, :] = colour
    return map

#combine maps such that map1 occurs 'beneath' map2
def layerMaps(map1, map2):
    x, y, z = int(map1.shape[0]), int(map1.shape[1]), int(map1.shape[2])
    if z == 1:
        map1 = np.broadcast_to(map1, (x, y, 3))
    newMap = np.zeros([x, y, 3])
    for i in range(x):
        for j in range(y):
            if (np.array_equal(map2[i, j, :], np.array([255, 0, 0]))) or (np.array_equal(map2[i, j, :], np.array([0, 255, 0]))) or (np.array_equal(map2[i, j, :], np.array([0, 0, 255]))):
                newMap[i, j, :] = map2[i, j, :]
            else:
                newMap[i, j, :] = map2[i, j, :]
    return newMap


def save_an_image(im, title, di='./'):
  print(os.path.basename(title))
  if not di.endswith('/'):
    di+='/'
  save_img((di+os.path.basename(title)+'.jpg'), im)
#############################



#############################
#MAIN FUNCTIONS
#############################
def find_first_handle(boundary, center):
    top_point = center
    current_best_val = 0
    for p in boundary:
        if (p.x == top_point.x) and (p.y > top_point.y):
            top_point = p
    current_best_points = [top_point, op_point(top_point, center, boundary)]
    stop_point = op_point(top_point, center, boundary)
    ac_boundary = sorted(boundary, key = lambda val: angleOrdered(center, top_point, 0, val))
    for current_point in ac_boundary:
        if current_point == stop_point:
            return current_best_points
        else:
            opposite = op_point(current_point, center, boundary)
            if distance(current_point, opposite) > current_best_val:
                if current_best_val == 0:
                    stop_point = opposite
                current_best_val, current_best_points = distance(current_point, opposite), [current_point, opposite]
    return current_best_points
