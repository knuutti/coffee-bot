import cv2 as cv

filename = 'kmeans.png'
img = cv.imread(filename)
img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)

ret,thresh1 = cv.threshold(img,50,255,cv.THRESH_BINARY)

cv.imwrite("global.png", thresh1)