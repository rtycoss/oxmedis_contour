#import matplotlib.pyplot as plt
from keras import *
from keras import backend as K
import numpy as np
import math
import os
from keras.preprocessing.image import save_img


from utils import *

closed = True
tau = 7


#h1 = north handle
#h2 = south handle
class knot:
    def __init__(self, center, h1, h2, c_center):
        self.c = center
        if getAngle(h1, c_center, h2) < 180:
            self.h1 = h1
            self.h2 = h2
        else:
            self.h1 = h2
            self.h2 = h1

    def __eq__(self, other):
        if self.c == other.c:
            return True
        else:
            return False

#k = this knot
#k1 = knot after (north)
#k2 = knot before (south)
class chained_knot:
    def __init__(self, k, k1, k2):
        self.k = k
        self.k1 = k1
        self.k2 = k2

def inPlane(c, h, p):
    #angle from h to p around c counter clockwise
    angle = getAngle(h,c,p)
    if (angle <= 180): return True
    else: return False

def simplify(csp_list):
    for [k, nk, sk, solved] in csp_list:
        if not(solved):
            if len(nk) > 1:
                nk.sort(key = lambda val: distance(k.c, val.c))
                rem = nk.pop()
                #print("popped: " + str(rem.c.x) + " and " + str(rem.c.y))
                #print("from: " + str(k.c.x) + " and " + str(k.c.y))
            if len(sk) > 1:
                sk.sort(key = lambda val: distance(k.c, val.c))
                rem = sk.pop()
                #print("popped: " + str(rem.c.x) + " and " + str(rem.c.y))
                #print("from: " + str(k.c.x) + " and " + str(k.c.y))
    return csp_list

def remove_knot(knot, this_knot, list):
    if len(list) > 1:
        if knot in list:
            #print("removing: (" + str(knot.c.x) + ", " + str(knot.c.y) + ") from:  (" + str(this_knot.c.x) + ", " + str(this_knot.c.y) + ")")
            list.remove(knot)
    return list
def adjust_handle(h1, c, h2, total, tau):
    #print("blahhh")
    #print(h1.x, h1.y)
    #print((distance(h2, h1)))

    new_x = h1.x + tau*(h1.x - c.x)*(distance(h2, h1)/total)
    new_y = h1.y + tau*(h1.y - c.y)*(distance(h2, h1)/total)
    #print(new_x, new_y)
    return point(round(new_x), round(new_y))

def norm_vals(knots):
    total = 0
    for knot in knots:
        total = total + (distance(knot.k1.h2, knot.k.h1))**2 + (distance(knot.k2.h1, knot.k.h2))**2
    total = math.sqrt(total)
    for knot in knots:
        knot.k.h1 = adjust_handle(knot.k.h1, knot.k.c, knot.k2.h1, total, tau)
        knot.k.h2 = adjust_handle(knot.k.h2, knot.k.c, knot.k1.h2, total, tau)
    return knots

def knot_sorter(knots, cluster_center):
    csp = []
    wc = Wildcard()
    low_x, high_x, knot_dist = 9000, 0, 1

    for knot in knots:
        if knot.c.x < low_x:
            low_x = knot.c.x
        if knot.c.x > high_x:
            high_x = knot.c.x
        #print("I am: " + str(knot.c.x) + " and " + str(knot.c.y))
        north_knots = [k for k in knots if (inPlane(cluster_center, knot.c, k.c) and (knot.c != k.c))]
        #for nk in north_knots:
        #    print("nk: " + str(nk.c.x) + " and " + str(nk.c.y))
        south_knots = [k for k in knots if (not(inPlane(cluster_center, knot.c, k.c)) and (knot.c != k.c))]
        #for sk in south_knots:
        #    print("sk: " + str(sk.c.x) + " and " + str(sk.c.y))
        csp.append([knot, north_knots, south_knots, False])
    if not(closed):
        knot_dist = high_x - low_x
        for knot in knots:
            k_index = csp.index([knot, wc, wc, wc])
            if knot.c.x == low_x:
                csp[k_index][1] = [knot]
            if knot.c.x == high_x:
                csp[k_index][2] = [knot]

    solved = []
    while len(solved) < len(knots):
        #print([(knot[0], len(knot[1]), len(knot[2])) for knot in csp])
        for knot in csp:
            if not(knot[3]):
                if len(knot[1]) == 1:
                    #desk_knot - the knot found
                    dest_knot = knot[1][0]
                    current_dest_index = csp.index([dest_knot, wc, wc, wc])
                    #csp[current_dest_index][2] = [knot[0]]
                    for i in range(len(csp)):
                        if csp[i][0] != knot[0] and csp[i][0] != dest_knot:
                            csp[i][1] = remove_knot(dest_knot, csp[i][0], csp[i][1])
                            csp[i][2] = remove_knot(knot[0], csp[i][0], csp[i][2])

                if len(knot[2]) == 1:
                    dest_knot = knot[2][0]
                    current_dest_index = csp.index([dest_knot, wc, wc, wc])
                    #csp[current_dest_index][1] = [knot[0]]
                    for i in range(len(csp)):
                        if csp[i][0] != knot[0] and csp[i][0] != dest_knot:
                            csp[i][1] = remove_knot(knot[0], csp[i][0], csp[i][1])
                            csp[i][2] = remove_knot(dest_knot, csp[i][0], csp[i][2])

                if (len(knot[1]) == 1) and (len(knot[2]) == 1):
                    solved_knot = chained_knot(knot[0], knot[1][0], knot[2][0])
                    solved.append(solved_knot)
                    csp[csp.index(knot)][3] = True
        '''
        for [knot, north_knots, south_knots, state] in csp:
            print("I am: " + str(knot.c.x) + " and " + str(knot.c.y))
            for nk in north_knots:
                print("nk: " + str(nk.c.x) + " and " + str(nk.c.y))
            for sk in south_knots:
                print("sk: " + str(sk.c.x) + " and " + str(sk.c.y))
        print("simplify time")
        '''
        csp = simplify(csp)
    #for knot in solved:
        #print("my co-ords are: " + str(knot.k.c.x) + " and " + str(knot.k.c.y))
        #print("my north neighbour coords are: " + str(knot.k1.c.x) + " and " + str(knot.k1.c.y))
        #print("my south neighbour coords are: " + str(knot.k2.c.x) + " and " + str(knot.k2.c.y) + '\n')

    return (solved, knot_dist)



class cluster:
    def __init__(self, distinct, x, y):
        x_sum, y_sum = 0, 0
        for [c, [h1, h2]] in distinct:
            x_sum = x_sum + c.x
            y_sum = y_sum + c.y
        if closed:
            cluster_center = point(round(x_sum/len(distinct)), round(y_sum/len(distinct)))
        else:
            cluster_center = point(round(x_sum/len(distinct)), round(y/2))
        #print(cluster_center.x, cluster_center.y)
        self.knots = []
        self.knot_dist = 1
        for [c, [h1, h2]] in distinct:
            self.knots.append(knot(c, h1, h2, cluster_center))
        (self.sorted_knots, self.knot_dist) = knot_sorter(self.knots, cluster_center)
        self.sorted_knots = norm_vals(self.sorted_knots)

    def get_knots(self):
        return self.sorted_knots

    def get_dist(self):
            return self.knot_dist


#############################
#KNOT CLUSTER FUNCTIONS
#############################




#############################
