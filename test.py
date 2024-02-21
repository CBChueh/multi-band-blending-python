import torch
import numpy as np
from skimage.color import rgb2gray
from skimage.data import astronaut
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve
import time

img_now = rgb2gray(astronaut())
psf_extent = 128
x = np.linspace(-1, 1, psf_extent)
y = np.linspace(-1, 1, psf_extent).reshape((-1, 1))
# build asymmetric psf so no specific tricks (e.g. separable, DCT, etc.) can be used
sigma_sqd = (x+2)**5 + (y+2)**5
psf_now = np.exp(-((x+.1)**2 + (y+.1)**2)/(1e-3*sigma_sqd))
tp = torch.Tensor.view(torch.from_numpy(img_now), 1, 1, img_now.shape[0], img_now.shape[1])
tp.requires_grad_(False)
pp = torch.Tensor.view(torch.from_numpy(psf_now), 1, 1, psf_now.shape[0], psf_now.shape[1])
pp.requires_grad_(False)

start = time.time()
blur_img = torch.nn.functional.conv2d(tp, pp, padding=psf_now.shape[0] // 2 - 1)
print('pytorch conv2d elapsed: %fs' % (time.time() - start))
start = time.time()
blur_scipy = fftconvolve(img_now, psf_now, mode='same')
print('scipy fftconvolve elapsed: %fs' % (time.time() - start))