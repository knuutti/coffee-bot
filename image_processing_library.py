import cv2
import numpy as np

def image_edges(img, clusters: int, threshold: float, size: int):
	img_kmeans = kmeans_process(img, clusters)
	img_global = global_thresholding(img_kmeans, threshold)
	img_edges = laplace_process(img_global, size)
	return img_kmeans, img_edges, img_global

def transform_image(img):
	rotation = -5
	scale = 9.6
	x = 0.46
	y = 0.53
	img = rotate_image(img, rotation)
	img = resize_image(img, scale, x, y)
	return img

def resize_image(img, scale: float, x_position: float, y_position: float):

	# Get the image size
	height, width, _ = img.shape

	# Prepare the crop
	centerX,centerY=int(x_position*width),int(y_position*height)
	radiusX,radiusY= int(scale*height/100),int(scale*width/100)
	minX,maxX=centerX-radiusX,centerX+radiusX
	minY,maxY=centerY-radiusY,centerY+radiusY

    # Create the cropped image
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