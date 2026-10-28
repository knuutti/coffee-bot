import cv2
import datetime
import time
import numpy as np
import requests

def main():

	visual = False

	cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
	cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

	while True: 

		# New image after every 15 seconds
		#time.sleep(15)
		
		# Read video frame by frame 
		_, img = cap.read()

		img = rotate_image(img, 2.5)
		img = resize_image(img)

		img_kmeans = kmeans_process(img, 3)
		img_global = global_thresholding(img_kmeans, 30)
		img_edges = laplace_process(img_global, 5)
		valid = validate_image(img_global)
		
		top, bottom, left, right = find_boundaries(img_edges)

		t = top + int(0.54*(bottom-top))
		b = top + int(0.83*(bottom-top))
		l1 = (left+right)//2
		l2 = left+int(0.72*(right-left))
		r1 = left+int(0.78*(right-left))
		r2 = right

		level = find_coffee_level(l1, l2, r1, r2, b, t, img_kmeans)

		# Post new data point
		if b != t:
			time_stamp = datetime.datetime.now()
			coffee_coefficient = 1-(level-t)/(b-t)
			url = "http://localhost:8000"
			myobj = {"data": {"time": str(time_stamp), "coffee": str(coffee_coefficient)}}
			requests.post(url, json = myobj)

		if visual:
			img_process = img
			
			# Add lines to the visualized image
			img_process[top,left:right,:] = [0,0,255]
			img_process[bottom,left:right,:] = [0,0,255]
			img_process[top:bottom,left,:] = [0,0,255]
			img_process[top:bottom,right,:] = [0,0,255]
			img_process[t,l1:r2,:] = [0,255,0]
			img_process[b,l1:r2,:] = [0,255,0]
			img_process[level,l1:r2,:] = [255,255,0]
			img_process[t:b,l1,:] = [0,255,0]
			img_process[t:b,r2,:] = [0,255,0]
			img_process[t:b,l2,:] = [0,255,0]
			img_process[t:b,r1,:] = [0,255,0]

			cv2.imshow('Coffee Cam', img_process)
		if cv2.waitKey(1) == 27:
			break  # esc to quit
		

def validate_image(img_global):
	height, width, _ = img_global.shape
	N = height*width
	total = 0
	for level in range(0, height):
		row = img_global[level,0:width,0]
		total += sum(map(lambda x: 1 if x==0 else 0, row))
	print(total, N)
	return total < 0.2*N
		

# EDIT THIS IF CAMERA POSITION CHANGES
# Modify the original image to zoom the coffee machine
def resize_image(img):
	scale = 9

	#get the webcam size
	height, width, _ = img.shape

	#prepare the crop
	centerX,centerY=int(0.38*height),int(0.26*width)
	radiusX,radiusY= int(scale*height/100),int(scale*width/100)

	minX,maxX=centerX-radiusX,centerX+radiusX
	minY,maxY=centerY-radiusY,centerY+radiusY

	cropped = img[minX:maxX, minY:maxY]
	return cv2.resize(cropped, (width, height)) 

def rotate_image(image, angle):
	image_center = tuple(np.array(image.shape[1::-1]) / 2)
	rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
	result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
	return result

def kmeans_process(img, k):
	# Source code: https://thepythoncode.com/article/kmeans-for-image-segmentation-opencv-python

	# reshape the image to a 2D array of pixels and 3 color values (RGB) and convert to float
	pixel_values = img.reshape((-1, 3))
	pixel_values = np.float32(pixel_values)

	# Perform k-means clustering on the pixel values.
	# compactness is the sum of squared distance from each point to their corresponding centers
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
	compactness, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
	centers = np.uint8(centers)
	
	# Use arbitary colors for kmeans image
	color_sums = [sum(color) for color in centers]
	# new_colors = [0, 126, 255]
	# for color in sorted(color_sums):
	# 	centers[color_sums.index(color)] = [new_colors.pop(0)]
	centers[color_sums.index(min(color_sums))] = [0]
	centers[color_sums.index(max(color_sums))] = [255]
		
	# create the segmented image using the cluster centroids
	segmented_image = centers[labels.flatten()]

	return segmented_image.reshape(img.shape)

def global_thresholding(img, threshold):
	_,img = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY)
	return img

def laplace_process(img, kernel_size):
	# Source code: https://docs.opencv.org/3.4/d5/db5/tutorial_laplace_operator.html
	
    # Declare the variables we are going to use
    ddepth = cv2.CV_16S

    # Remove noise by blurring with a Gaussian filter
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # Convert the image to grayscale
    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
	# Apply Laplace function
    dst = cv2.Laplacian(src_gray, ddepth, ksize=kernel_size)

    # converting back to uint8
    return cv2.convertScaleAbs(dst)

def find_boundaries(img):
	top, bottom, left, right = 100,100,100,100
	height, width = img.shape

	for i in range(height):
		if sum(img[i][int(0.2*width):int(0.8*width)]) >= 1:
			top = i
			break

	for i in range(int(0.1*width),width):
		if sum(img[0:int(0.2*height),i]) >= 1:
			left = i
			break
	for i in range(int(0.5*width),width):
		if sum(img[0:int(0.4*height),i]) < 1:
			right = i
			break

	for i in range(height-1, -1, -1):
		if sum(img[i][int(0.2*width):int(0.5*width)]) >= 1:
			bottom = i
			break
			
	return top, bottom, left, right


def find_coffee_level(l1, l2, r1, r2, b, t, img_edges):
	level_l = t
	level_r = t
	for level in range(b, t, -1):
		
		area = img_edges[level,l1:l2,0]
		#print(level)
		#print(sum(map(lambda x: 1 if x<255 else 0, area)))
		#print(area)
		if sum(map(lambda x: 1 if x>0 else 0, area)) > 0.9*(l2-l1):
			level_l = level
			break
	for level in range(b, t, -1):
		
		area = img_edges[level,r1:r2,0]
		if sum(map(lambda x: 1 if x>0 else 0, area)) > 0.9*(r2-r1):
			level_r = level
			break
	
	level = max([level_l, level_r])
	print(level_l, level_r)
	#print(level, b, t)
	return level




if __name__ == "__main__":
	main()