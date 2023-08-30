# importing the opencv(cv2) module
import cv2
import numpy as np

def rotate(image, angle, center = None, scale = 1.0):
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h), borderValue=(255,255,255))

    return rotated

rot = 13
height = 512
width = 512
blank_image = np.zeros((height,width,3), np.uint8)
blank_image[:,0:width//2] = (255,0,0)      # (B, G, R)
blank_image[:,width//2:width] = (0,255,0)
# reading the image
image = cv2.imread('test.bmp')
replicate = cv2.copyMakeBorder(src=image, top=50, bottom=50, left=50, right=50, borderType=cv2.BORDER_REPLICATE)
replicate = rotate(replicate,rot)


#replicate[256:357, 0:611] = (0, 55, 0)
for x in range(512):
    for y in range(512):
        (b, g, r) = replicate[x, y]
        if b == 0 and g == 0 and r == 0:
            replicate[x][y] = (128, 55, 0)

replicate = rotate(replicate,-rot)

x= 50
y=50
w=512

h=512
cropped_image = replicate[y:y+h, x:x+w]
# changing the color space
#gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# showing the resultant image
cv2.imshow('mask', image)
cv2.imshow('output', cropped_image )
(b, g, r) = image[0, 0]
print("Pixel at (0, 0) - Red: {}, Green: {}, Blue: {}".format(r, g, b))

# waiting until key press
cv2.waitKey()
# destroy all the windows
cv2.destroyAllWindows()

