#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <opencv2/opencv.hpp>

namespace py = pybind11;

py::array_t<uint8_t> passGrayscaletToPython(const std::string& filename)
{
    // Create a cv::Mat object
    cv::Mat cv_mat = cv::imread(filename);

     // Check if the image was successfully loaded
    if (cv_mat.empty())
    {
        throw std::runtime_error("Failed to load image: " + filename);
    }

    // Convert cv::Mat to NumPy array
    py::array_t<uint8_t> numpy_array({ cv_mat.rows, cv_mat.cols }, cv_mat.data);

    return numpy_array;
}


py::array_t<uint8_t> passBGRToPython(const std::string& filename)
{
    // Create a cv::Mat object
    cv::Mat cv_mat = cv::imread(filename);

     // Check if the image was successfully loaded
    if (cv_mat.empty())
    {
        throw std::runtime_error("Failed to load image: " + filename);
    }

    // Convert cv::Mat to NumPy array
    py::array_t<uint8_t> numpy_array({cv_mat.rows, cv_mat.cols, cv_mat.channels()}, cv_mat.data);

    return numpy_array;
}

// Bindings for the passCvMatToPython function
PYBIND11_MODULE(opencv_module, m)
{
    
    m.def("passGrayscaletToPython", &passGrayscaletToPython, "Pass cv::Mat from C++ to Python");
    m.def("passBGRToPython", &passBGRToPython, "Pass cv::Mat from C++ to Python");
 
    m.attr("__version__") = "0.0.2";

}

// PYBIND11_MODULE(cmake_example, m) {
//     m.doc() = R"pbdoc(
//         Pybind11 example plugin
//         -----------------------

//         .. currentmodule:: cmake_example

//         .. autosummary::
//            :toctree: _generate

//            add
//            subtract
//     )pbdoc";
    
//     m.def("cvMatToNumpy", &cvMatToNumpy, "Convert cv::Mat to NumPy array");
//     m.def("numpyToCvMat", &numpyToCvMat, "Convert NumPy array to cv::Mat");
//     m.def("add", &add, R"pbdoc(
//         Add two numbers

//         Some other explanation about the add function.
//     )pbdoc");

//     m.def("subtract", [](int i, int j) { return i - j; }, R"pbdoc(
//         Subtract two numbers

//         Some other explanation about the subtract function.
//     )pbdoc");


//     m.attr("__version__") = "0.0.1";
// }
