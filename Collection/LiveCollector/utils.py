import cv2
import numpy as np
from typing import Tuple, Union

def mse(img1: np.ndarray, img2: np.ndarray) -> Tuple[Union[float, np.floating], np.ndarray]:
    """Compute Mean Squared Error between two images"""
    h, w = img1.shape[:2]
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff**2)
    mse = err/(float(h*w))
    return mse, diff
