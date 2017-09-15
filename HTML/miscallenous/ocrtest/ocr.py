import sys
sys.path.append('/usr/local/Cellar')

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract #NOTE for this to work you must also install tesseract-ocr,    pip install -U tesseract-ocr


def read_captcha():

    image_file = Image.open("out.png") # open colour image
    image_file = image_file.convert('1') # convert image to black and white
    image_file = image_file.resize((150, 45))
    image_file.save('out.png')

    text = pytesseract.image_to_string(Image.open('out.png'))

    print text

#GOD DAMN IT WORKS

read_captcha()


















#
# # Path of working folder on Disk
# src_path = "/Users/potato/Desktop/HTMLREADER/ocrtest/res/"
#
# def get_string(img_path):
#     # Read image with opencv
#     img = cv2.imread(img_path)
#
#     # Convert to gray
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#
#     print 'converted to grey'
#
#     # Apply dilation and erosion to remove some noise
#     kernel = np.ones((1, 1), np.uint8)
#     img = cv2.dilate(img, kernel, iterations=1)
#     img = cv2.erode(img, kernel, iterations=1)
#
#     print 'applied dilation and erosion'
#
#     # Write image after removed noise
#     cv2.imwrite(src_path + "removed_noise.png", img)
#
#     print 'got to here'
#     #  Apply threshold to get image with only black and white
#     img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
#
#     print 'get balck and white'
#     # Write the image after apply opencv to do some ...
#     cv2.imwrite(src_path + "thres.png", img)
#
#     print 'something thres'
#     # Recognize text with tesseract for python
#     result = pytesseract.image_to_string(Image.open(src_path))
#
#     print 'writing result'
#     # Remove template file
#     #os.remove(temp)
#     return result
#
#
# print '--- Start recognize text from image ---'
# print get_string(src_path + "2.png")
#
# print "------ Done -------"
