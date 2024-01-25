#!/usr/bin/python
import numpy as np
import cv2
import sys
import argparse


def preprocess(imgs, sep, overlap):
    cv2.imwrite('img_1.png', imgs[0])
    cv2.imwrite('img_2.png', imgs[1])
    Shape = np.array(imgs[0].shape)
    if Shape[0]%sep != 0:
        print ("error: sep should be power of 2 error")
        sys.exit()
    subs=[np.zeros(Shape) for i in range(sep*sep)]
    masks=[np.zeros(Shape) for i in range(sep*sep)]
    shape=Shape[0]//sep
    overlap_w=int(overlap*shape)
    for ind, sub in enumerate(subs):
        indx=ind%sep
        indy=ind//sep
        xmin=max(0,indx*shape-overlap_w)
        xmax=min(Shape[0],(indx+1)*shape+overlap_w)
        ymin=max(0,indy*shape-overlap_w)
        ymax=min(Shape[1],(indy+1)*shape+overlap_w)
        sub[xmin:xmax,ymin:ymax]=imgs[abs(indy%2)][xmin:xmax,ymin:ymax]
        masks[ind][indx*shape:(indx+1)*shape,indy*shape:(indy+1)*shape]=1
        temp=np.ndarray.copy(sub)
        # temp[temp==1]=255
        cv2.imwrite('temp_' + str(ind) +'.png', temp)
    return subs, masks

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
    LPs=[]
    for img in imgs:
        LP = []
        for i in range(leveln - 1):
            next_img = cv2.pyrDown(img)
            LP.append(img - cv2.pyrUp(next_img, img.shape[1::-1]))
            img = next_img
        LP.append(img)
        LPs.append(LP)
    return LPs


def blend_pyramid(LPs, MPs):
    blended = []
    for lev in range(len(MPs[0])):
        Tot_M=np.zeros(LPs[0][lev].shape)
        for ind in range(len(MPs)):
            Tot_M+=np.array(MPs[ind][lev]*LPs[ind][lev])
        blended.append(Tot_M)
    return blended


def reconstruct(LS):
    img = LS[-1]
    for lev_img in LS[-2::-1]:
        img = cv2.pyrUp(img, lev_img.shape[1::-1])
        img += lev_img
    return img


def multi_band_blending_arb(img1, img2, sep, overlap, leveln=None):
    # assume img1 and img2 are same size
    imgs=[img1,img2]

    if sep < 0 :
        print ("error: sep should be a positive integer")
        sys.exit()

    subs, masks = preprocess(imgs, sep, overlap)

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
    sep=4
    folder='/Users/chuanborchueh/Documents/Coding/multi-band-blending-python/'
    img1 = cv2.imread('samples/l.jpg')
    img2 = cv2.imread('samples/r.jpg')
    leveln = 8
    overlap = 0.5

    result = multi_band_blending_arb(img1, img2, sep, overlap, leveln)
    cv2.imwrite('result.png', result)
    print("blending result has been saved in 'result.png'")
