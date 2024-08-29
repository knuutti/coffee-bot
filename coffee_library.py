import cv2
import numpy as np
import image_processing_library as ipl

def analyse(img):
	
    # Rotates and zooms the original image
	img_transformed = ipl.transform_image(img)
	
    # Processes the image in order to find edges and the black areas
	img_kmeans, img_edges, img_global = ipl.image_edges(img_transformed, 3, 30, 5)
	
	cv2.imwrite('coffee.jpg', img_transformed)
	cv2.imwrite('coffeek.jpg', img_kmeans)
	cv2.imwrite('coffeee.jpg', img_edges)
	cv2.imwrite('coffeeg.jpg', img_global)
	
    # Checks if the image is has too much black
	#if not validate_image(img_global):
	#	print("Error: Too dark image.")
	#	return -1
	
    # Finding the boundaries of the coffee machine
	top, bottom, left, right = find_boundaries(img_edges)
	
    # Using the boundary info for defining the boundaries of the coffee pot
	t = top + int(0.54*(bottom-top))
	b = top + int(0.83*(bottom-top))
	l1 = (left+right)//2
	l2 = left+int(0.72*(right-left))
	r1 = left+int(0.78*(right-left))
	r2 = right

	# Checking if boundary sizes make sense
	if (bottom-top) < 370 or (bottom-top) > 430: 
		print("Rejecting: bottom/top size is bad.")
		return -1
	if (right-left) < 280 or (right-left) > 320: 
		print("Rejecting: right/left size is bad.")
		return -1

    # Calculate the coffee level with the boundary data and the black/white image
	coffee_coefficient = find_coffee_level(l1, l2, r1, r2, b, t, img_global)	
	
	# Normalize the coefficient value
	#coffee_coefficient = (coffee_coefficient-0.03)/(.85-0.03)
	#if coffee_coefficient > 1: coffee_coefficient = 1
	#elif coffee_coefficient < 0: coffee_coefficient = 0
	return coffee_coefficient


def validate_image(img_global):
	# Checks if the black/white image has less than 20% black pixels
    # If the image has more than that, there is likely something blocking the
    # coffee machine and the image is not valid
	
	height, width, _ = img_global.shape
	N = height*width
	total = 0
	for level in range(0, height):
		row = img_global[level,0:width,0]
		total += sum(map(lambda x: 1 if x==0 else 0, row))
	
	return total < 0.2*N



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


def find_coffee_level(l1, l2, r1, r2, b, t, img_global):
	levels = [t, t]
	left = [l1, r1]
	right = [l2, r2]
	
    # Finding the coffee level of both of the sides of the coffee pot individually
	for i in [0, 1]:
		for level in range(b, t, -1):
			area = img_global[level, left[i]:right[i], 0]
			if sum(map(lambda x: 1 if x>0 else 0, area)) > 0.9*(right[i]-left[i]):
				levels[i] = level
				break
	
    # True level is the highest one (the other one may have reflections etc.)
	coffee_level = max(levels)
	
    # Calculating the coefficient (value in range 0-1) from the coffee level
	coffee_coefficient = 1-(coffee_level-t)/(b-t)
	
	return coffee_coefficient

