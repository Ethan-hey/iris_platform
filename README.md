# iris_platform

This project builds an iris image platform that allows users to register, login into the webiste and upload their iris image.

After the upload, the image would first be validated(either accepted or rejected). After that, the iris part of the image would be detected based on Hough Transform, then normalized and flattened. 

The intention of the project is that it could become a iris image database, which provides iris training data for data scientists. 
