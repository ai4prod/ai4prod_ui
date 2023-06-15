# Python_Cpp_Example

This example use pybind to pass all the information from C++ to Python.
This could be used to build a GUI in a python gui framework, while using C++ for inference.


# How it Works

We use Pybind11 to create wrappers around C++ function and get the results back in Python.

# STEPS

1) Compile ai4prod. Need to add opencv build like deps/opencv in order to compile the project
2) Create your custom pybind11 using main.cpp
3) mkdir build && cmake ..
4) python3 setup.py bdist_wheel
5) pip install dist/{module_name}.whl
6) Use python test_cv.py to make some test


# Warning

Python module inside setup.py needs to have the same name as cmake_project otherwise will not work 

# Reference 

https://www.youtube.com/watch?v=H2wOlriHGmM&ab_channel=FacileTutorials
