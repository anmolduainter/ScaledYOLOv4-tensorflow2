

"""Transforms for YOLO series."""
from __future__ import absolute_import
import copy
import numpy as np
import cv2

from utils import bbox2_gluoncv as tbbox
from utils import image_gluoncv as image
from utils.bbox_gluoncv import random_crop_with_constraints
from utils import image1_gluoncv as timage
class YOLO3DefaultTrainTransform(object):
    """Default YOLO training transform which includes tons of image augmentations.
    Parameters
    ----------
    width : int
        Image width.
    height : int
        Image height.
    net : mxnet.gluon.HybridBlock, optional
        The yolo network.
        .. hint::
            If net is ``None``, the transformation will not generate training targets.
            Otherwise it will generate training targets to accelerate the training phase
            since we push some workload to CPU workers instead of GPUs.
    mean : array-like of size 3
        Mean pixel values to be subtracted from image tensor. Default is [0.485, 0.456, 0.406].
    std : array-like of size 3
        Standard deviation to be divided from image. Default is [0.229, 0.224, 0.225].
    iou_thresh : float
        IOU overlap threshold for maximum matching, default is 0.5.
    box_norm : array-like of size 4, default is (0.1, 0.1, 0.2, 0.2)
        Std value to be divided from encoded values.
    """
    def __init__(self, width, height, net=None, mean=(0.485, 0.456, 0.406),
                 std=(0.229, 0.224, 0.225), mixup=False, **kwargs):
        self._width = width
        self._height = height
        self._mean = mean
        self._std = std
        self._mixup = mixup
        self._target_generator = None

    def __call__(self, src, label):
        """Apply transform to training image/label."""

        # print("s111:", src.shape , label)
        # random color jittering
        img = image.np_random_color_distort(src)
        # return img, label
        # random expansion with prob 0.5
        if np.random.uniform(0, 1) > 0.5:
            img, expand = timage.random_expand(img, fill=[m * 255 for m in self._mean])
            bbox = tbbox.translate(label, x_offset=expand[0], y_offset=expand[1])
        else:
            img, bbox = img, label

        # # random horizontal flip
        # h, w, _ = img.shape
        # img, flips = timage.random_flip(img, px=0.5)
        # bbox = tbbox.flip(bbox, (w, h), flip_x=flips[0])

        # # resize with random interpolation
        # h, w, _ = img.shape
        # interp = np.random.randint(0, 5)
        # img = timage.imresize(img, self._width, self._height, inter=interp)
        # bbox = tbbox.resize(bbox, (w, h), (self._width, self._height))
        # # return img, bbox

        # random cropping
        h, w, _ = img.shape
        # print("s000:",bbox,  h, w)
        bbox, crop = random_crop_with_constraints(bbox, (w, h))
        x0, y0, w, h = crop
        # print("s0:", bbox, crop)

        img = img[y0:y0+h,x0:x0+w,:]

        # resize with random interpolation
        h, w, _ = img.shape
        interp = np.random.randint(0, 5)
        #
        img = timage.imresize(img, self._width, self._height, inter=interp)
        bbox = tbbox.resize(bbox, (w, h), (self._width, self._height))
        # print("s1:",bbox)
        # random horizontal flip
        h, w, _ = img.shape
        img, flips = timage.random_flip(img, px=0.5)
        bbox = tbbox.flip(bbox, (w, h), flip_x=flips[0])
        # print("s2:", bbox)
        return img,bbox

#
# import os
# os.environ['CUDA_VISIBLE_DEVICES']='-1'
# cv_img = cv2.imread('/home/wangem1/t1.jpg')
# cv_img = cv2.resize(cv_img, (416, 416))
# cv2.rectangle(cv_img,(1,1),(50,50),(255,0,0))
# cv2.imshow("d1",cv_img)
#
#
# sss = YOLO3DefaultTrainTransform(416,416)
# while True:
#     img,box = sss(cv_img,np.array([[1,1,50,50,3]]))
#     cv2.rectangle(img,(box[0][0],box[0][1]),(box[0][2],box[0][3]),(255,0,0))
#     cv2.imshow("d2",img)
#     cv2.waitKey(0)

#
# image_group  = np.expand_dims(cv_img,axis=0)
# annotations_group=[{'bboxes':[[50,50,200,200]],'labels':[1]}]
#
# boxes_and_labels = np.concatenate([annotations_group[0]['bboxes'],
#                                    np.expand_dims(annotations_group[0]['labels'], 0)], axis=-1)
# print(boxes_and_labels)
# image_group[0], boxes_and_labels = sss(image_group[0], boxes_and_labels)
#
# # annotations_group[0]['bboxes'] = boxes_and_labels[:, 0:4]
# # annotations_group[0]['labels'] = boxes_and_labels[:, 4]