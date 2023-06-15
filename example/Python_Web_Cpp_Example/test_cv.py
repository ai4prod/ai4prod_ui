import opencv_module
import cv2

# Create a cv::Mat in C++
cv_mat = cv2.imread('dog.jpg')


# Convert NumPy array to cv::Mat
new_cv_mat = opencv_module.passBGRToPython("dog.jpg")

# # Convert cv::Mat to NumPy array
# numpy_array = opencv_module.cvMatToNumpy(cv_mat)



# Verify the conversion by displaying the image
cv2.imshow('New Image', new_cv_mat)
cv2.waitKey(0)
cv2.destroyAllWindows()