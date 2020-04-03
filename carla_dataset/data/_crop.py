import cv2
import numpy as np

from carla_dataset.intrinsics import PinholeIntrinsics

_new_size = 2 * PinholeIntrinsics().f_x * np.tan(np.pi / 4)
_scale_factor = 768 / _new_size


def crop_pinhole_to_90(image):
    # use https://www.tensorflow.org/api_docs/python/tf/image/crop_and_resize  ?

    image = cv2.resize(image, dsize=(0, 0), fx=_scale_factor, fy=_scale_factor)
    center = tuple(p // 2 for p in image.shape[:2])

    image = cv2.getRectSubPix(image, (768, 768), center)
    return image
