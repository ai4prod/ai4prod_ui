
# How to Install Dev Environment

1) Install Vcpkg
``` 
./vcpkg/bootstrap-vcpkg.sh
```
2) Install Library Deps

``` 
$ sudo apt install libxinerama-dev libxcursor-dev xorg-dev libglu1-mesa-dev pkg-config mesa-utils libibus-1.0-dev libx11-dev libxft-dev libxext-dev ibwayland-dev libxkbcommon-dev libegl1-mesa-dev libasound2-dev libpulse-dev libglfw3 libglfw3-dev xorg-dev
```
3) Check if OpenGL is installed

```
$ glxinfo | grep "OpenGL version"
output: OpenGL version string: 4.6.0 NVIDIA 515.65.01
```

How to build

``` 
    $ mkdir build
    $ cd build
    $ cmake ..

```

# References

vcpkg : https://stackoverflow.com/questions/70254678/installing-dear-imgui-with-vcpkg-on-windows-10
imgui_from_scratch: https://www.youtube.com/watch?v=VRwhNKoxUtk&ab_channel=VictorGordan

