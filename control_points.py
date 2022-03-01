import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
import csv
import os

from utils import *
from clusters import *
from splines import *
from keras.preprocessing import image

input_path = './data/heatmaps'
output_path = './outputs'
img_rows, img_cols = 800, 640
high_threshold = 200
low_threshold = 100


def find_distinct(image, truth, name):
    count = 0
    pixels = []
    truth_pixels = []
    distinct = []
    x, y = image.shape[0], image.shape[1]
    distinctMap = np.zeros([x, y, 3])
    for i in range(x):
        for j in range(y):
            val = int(image[i,j,:])
            if val > low_threshold:
                pixels.append([ val, point(i, j)])
            [valr, valg, valb] = truth[i, j, :]
            if (valr > 150) and (valg < 80) and (valb < 105):
                truth_pixels.append(point(i,j))
                #addSquare(distinctMap, point(i,j), False, [0, 255, 0])
    #pixels = all pixels with intesity above low_threshold
    pixels.sort(key = lambda a: [a[0], a[1].x, a[1].y])
    while pixels:
        #checked = pixels part of the same landmark where neighbours have been checked
        checked = []
        #working = pixels in the same landmark as checked that have yet to have neighbours checked
        working = [pixels.pop()]
        wc = Wildcard()
        while working:
            #print(len(working))
            next_working = []
            for pix1 in working:
                neighbour_pix = neighbours(pix1[1], x, y)
                for pix2 in neighbour_pix:
                    if [wc, pix2] in pixels:
                        pix_index = pixels.index([wc, pix2])
                        next_working.append(pixels.pop(pix_index))
                checked.append(pix1)
            working = next_working
            pixels = [pix for pix in pixels if pix not in next_working]
        checked.sort(key = lambda a: [a[0], a[1].x, a[1].y], reverse=True)
        #print(len(checked))
        if checked[0][0] > high_threshold:
            c_center = center_point(checked)
            handle_pair = find_first_handle(getBoundary(checked, x, y), c_center)
            distinct.append([c_center, handle_pair])
            distinctMap = addSquare(distinctMap, c_center, True, [0, 255, 0])
        #else:
            #print("not high enough")
    print(len(distinct))
    chain = cluster(distinct, x, y)
    for knot in chain.get_knots():
        distinctMap = addSquare(distinctMap, knot.k.h1, True, [255, 0, 0])
        distinctMap = addSquare(distinctMap, knot.k.h2, True, [0, 0, 255])
    #distinctMap = addSquare(distinctMap, point(100, 100), True, [255, 0, 0])
    #distinctMap = addSquare(distinctMap, point(200, 200), True, [0, 0, 255])
    poly = curved_shape(chain.get_knots())
    distinctMap = drawCurve(poly.get_poly(), distinctMap, [255, 0, 0])
    result = 100*average_dist(truth_pixels, poly.get_poly())/chain.get_dist()
    with open(os.path.join('./outputs', "results.csv"), 'a', newline='\n') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                csvwriter.writerow([os.path.basename(name)[:3], result])
                csvfile.write('\n')
                csvfile.close()
    save_an_image(layerMaps(image, distinctMap), name, './outputs')
    return distinct


def main():
    fnames=[]
    xs=[]
    xs2 = []
    for path, subdirs, files in os.walk(input_path):
        for name in files:
            fname=(os.path.join(path, name))
            if fname.endswith('.jpg') or fname.endswith('.png') or fname.endswith('.jpeg'):
                if 'image' not in os.path.basename(fname):
                    num = os.path.basename(fname)[:3]

                    x=image.load_img(fname, target_size = (img_rows, img_cols), color_mode = "grayscale")
                    x=np.expand_dims(x,axis=2)
                    x=np.expand_dims(x,axis=0)
                    #print(np.shape(x))
                    for name2 in files:
                        fname2=(os.path.join(path, name2))
                        if (str(num) in fname2) and ('image' in fname2):
                            x2=image.load_img(fname2, target_size = (img_rows, img_cols))
                            x2=np.expand_dims(x2,axis=0)
                    xs.append(x)
                    xs2.append(x2)
                    fnames.append(fname[:len(fname) - 7])
    xs=np.vstack(xs)
    xs = xs.reshape(xs.shape[0], img_rows, img_cols, 1)
    xs2=np.vstack(xs2)
    xs2 = xs2.reshape(xs2.shape[0], img_rows, img_cols, 3)
    print ('\n[Total data loaded: {0}]'.format(len(xs)))


    di=output_path # output dir
    if not(os.path.isdir(di)):
        os.system('mkdir -p {0}'.format(di))


    for index in range(len(xs)):
        name=fnames[index]
        print(os.path.basename(name))
        x=xs[index]
        x2 = xs2[index]
        print(find_distinct(x, x2, name))

main()
