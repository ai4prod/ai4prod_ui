
#vcpg set before project
set(CMAKE_TOOLCHAIN_FILE "${CMAKE_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")

message(" TOOLCHANIN ${CMAKE_SOURCE_DIR}/vcpkg/scripts/buildsystems/vcpkg.cmake")

cmake_minimum_required(VERSION 3.10)

project(imgui_example)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED)

find_package(OpenCV 4.4 EXACT REQUIRED PATHS deps/opencv/Release/)


set(PRJ_LIBRARIES 
    fmt::fmt
    #glfw
    glfw
    # imgui
    imgui::imgui
    # opengl
    OpenGL::GL
    ${OpenCV_LIBS}
    #OpenGL extension library
    GLEW::GLEW
)

find_package(imgui CONFIG REQUIRED)
find_package(OpenGL REQUIRED)
find_package(GLEW REQUIRED)

# add dependency find_package calls and similar here
find_package(fmt CONFIG REQUIRED)

add_executable(imgui_example main.cpp)

target_link_libraries(imgui_example PRIVATE ${PRJ_LIBRARIES} )
