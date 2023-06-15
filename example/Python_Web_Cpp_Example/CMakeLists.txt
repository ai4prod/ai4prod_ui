cmake_minimum_required(VERSION 3.4...3.18)
project(opencv_module)

find_package(OpenCV 4.4 EXACT REQUIRED PATHS deps/opencv/Release/)

add_subdirectory(pybind11)

# add_library(mylib STATIC src/myfile.cpp include/myfile.h)
# target_include_directories(mylib PRIVATE include/ src/)
# target_link_libraries(mylib PRIVATE ${OpenCV_LIBS})
#set_target_properties(mylib PROPERTIES POSITION_INDEPENDENT_CODE ON)

pybind11_add_module(opencv_module src/main.cpp)

target_link_libraries(opencv_module PRIVATE ${OpenCV_LIBS})


#target_link_libraries(cmake_example PRIVATE mylib)
