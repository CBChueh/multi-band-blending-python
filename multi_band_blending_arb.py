#!/usr/bin/python
import numpy as np
import cv2
import sys
import argparse


def preprocess(imgs, sep):

    Shape = np.array(imgs[0].shape)
    if Shape[0]%sep != 0:
        print ("error: sep should be power of 2 error")
        sys.exit()
    subs=[[np.zeros(Shape)]*sep]*sep
    masks=subs
    shape=Shape/sep
    for ind, sub in enumerate(subs):
        x=ind//sep
        y=ind%sep
        sub[x*shape:(x+1)*shape,y*shape:(y+1)*shape]=imgs[ind%2][x*shape:(x+1)*shape,y*shape:(y+1)*shape]
        masks[x,y][x*shape:(x+1)*shape,y*shape:(y+1)*shape]=1
    return subs, mask

def GaussianPyramid(masks, leveln):
    # return GPs: [imgs][levs]
    GPs=[] 
    for mask in masks:
        GP = [mask]
        for i in range(leveln - 1):
            GP.append(cv2.pyrDown(GP[i]))
        GPs.append(GP)
    return GPs


def LaplacianPyramid(imgs, leveln):
    # return LPs: [imgs][levs]
    LP = []
    LPs=[]
    for img in imgs:
        for i in range(leveln - 1):
            next_img = cv2.pyrDown(img)
            LP.append(img - cv2.pyrUp(next_img, img.shape[1::-1]))
            img = next_img
        LP.append(img)
        LPs.append(LP)
    return LPs


def blend_pyramid(LPs, MPs):
    blended = []
    for i, MP in enumerate(MPs[0]):
        for 
        blended.append(LPA[i] * MP + LPB[i] * (1.0 - MP))
    return blended


def reconstruct(LS):
    img = LS[-1]
    for lev_img in LS[-2::-1]:
        img = cv2.pyrUp(img, lev_img.shape[1::-1])
        img += lev_img
    return img


def multi_band_blending_arb(img1, img2, sep, leveln=None):
    # assume img1 and img2 are same size
    imgs=[img1,img2]

    if sep < 0 :
        print ("error: sep should be a positive integer")
        sys.exit()

    subs, masks = preprocess(imgs, sep)

    max_leveln = int(np.floor(np.log2(min(imgs[0].shape[0], imgs[0].shape[1],))))
    if leveln is None:
        leveln = max_leveln
    if leveln < 1 or leveln > max_leveln:
        print ("warning: inappropriate number of leveln")
        leveln = max_leveln

    # Get Gaussian pyramid and Laplacian pyramid
    MP = GaussianPyramid(masks, leveln)
    LPs = LaplacianPyramid(subs, leveln)

    # Blend two Laplacian pyramidspass
    blended = blend_pyramid(LPs, MP)

    # Reconstruction process
    result = reconstruct(blended)
    result[result > 255] = 255
    result[result < 0] = 0

    return result.astype(np.uint8)

if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser(
        description="A Python implementation of multi-band blending")
    ap.add_argument('-f', '--first', required=True,
                    help="path to the first (left) image")
    ap.add_argument('-s', '--second', required=True,
                    help="path to the second (right) image")
    ap.add_argument('-m', '--mask', required=False,
                    help="path to the mask image")
    ap.add_argument('-o', '--overlap', required=True, type=int,
                    help="width of the overlapped area between two images, \
                          even number recommended")
    ap.add_argument('-l', '--leveln', required=False, type=int,
                    help="number of levels of multi-band blending, \
                          calculated from image size if not provided")
    ap.add_argument('-H', '--half', required=False, action='store_true',
                    help="option to blend the left half of the first image \
                          and the right half of the second image")
    args = vars(ap.parse_args())

    flag_half = args['half']
    img1 = cv2.imread(args['first'])
    img2 = cv2.imread(args['second'])
    if args['mask'] != None:
        mask = cv2.imread(args['mask'])
        mask = mask//255
        need_mask = False
    else:
        mask = None
        need_mask =True
    overlap_w = args['overlap']
    leveln = args['leveln']
    print('args: ', args)
    
    result = multi_band_blending(img1, img2, mask, overlap_w, leveln, flag_half, need_mask)
    cv2.imwrite('result.png', result)
    print("blending result has been saved in 'result.png'")
