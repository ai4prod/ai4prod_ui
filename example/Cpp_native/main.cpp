

#include <GL/glew.h>
#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>
#include <opencv2/opencv.hpp>
#include <iostream>

// Helper function to convert OpenCV Mat to ImGui-compatible texture
// ImTextureID return an ID used by Imgui to rendere the texture. Usually is converted to INT
ImTextureID MatToTextureID(const cv::Mat &image)
{
    GLuint textureID;
    glGenTextures(1, &textureID);
    // attach texture to current context
    glBindTexture(GL_TEXTURE_2D, textureID);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    // This create the texture with the correct format GL_RGB = RGB image
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.cols, image.rows, 0, GL_BGR, GL_UNSIGNED_BYTE, image.ptr());
    // detach texture from current context
    glBindTexture(GL_TEXTURE_2D, 0);

    // identifier used by imgui to rendere texture
    return (ImTextureID)(intptr_t)textureID;
}

static void MouseButtonCallback(GLFWwindow *window, int button, int action, int mods);

void draw_rectangle(cv::Mat &image)
{

    cv::Point p1(30, 30);

    // Bottom Right Corner
    cv::Point p2(255, 255);

    int thickness = 2;

    // Drawing the Rectangle
    rectangle(image, p1, p2,
              cv::Scalar(255, 0, 0),
              thickness, cv::LINE_8);
}

int main()
{
    // Initialize GLFW and create a window
    glfwInit();
    GLFWwindow *window = glfwCreateWindow(800, 600, "ImGui OpenCV Example", nullptr, nullptr);
    glfwMakeContextCurrent(window);

    // Initialize GLEW
    glewInit();

    // Initialize ImGui
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    // setup glfw mouse event
    // glfwSetMouseButtonCallback(window, MouseButtonCallback);

    // OpenCV image loading
    cv::Mat cvImage = cv::imread("/media/dati/Develop/ai4prod_repo/Coding/ai4prod_ui/example/Cpp_native/dog.jpg");

    // Main loop
    while (!glfwWindowShouldClose(window))
    {
        glfwPollEvents();

        // Start ImGui frame
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        // clear any previous state and start building UI for current frame
        ImGui::NewFrame();

        ImGui::Begin("Window 2", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse);

        // Display the OpenCV image in ImGui
        ImTextureID textureID = MatToTextureID(cvImage);
        //ImGui::Image(textureID, ImVec2(cvImage.cols, cvImage.rows));

        // Handle dragging the bounding box
        static ImVec2 bboxPos(50, 50);
        static ImVec2 bboxSize(100, 100);

        // Handle dragging the bounding box
        if (ImGui::IsMouseDragging(ImGuiMouseButton_Left) && ImGui::IsItemHovered()) {
            std::cout <<"mouse dragging"<<std::endl;

            ImVec2 mouseDelta = ImGui::GetIO().MouseDelta;
            bboxPos.x += mouseDelta.x;
            bboxPos.y += mouseDelta.y;
        }

        // Draw the bounding box
        ImDrawList* drawList = ImGui::GetWindowDrawList();
        drawList->AddRect(bboxPos, ImVec2(bboxPos.x + bboxSize.x, bboxPos.y + bboxSize.y), IM_COL32(255, 0, 0, 255));
 

        ImGui::End();

        // This will create a new Docking Windows
        ImGui::Begin("Window 1", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse);

        if (ImGui::Button("Draw Rectangle"))
        {
            // Button was clicked, perform some action
            // This code block will be executed when the button is clicked
            // Add your desired code or functionality here
            std::cout << "clicked" << std::endl;
            draw_rectangle(cvImage);
        }

        ImGui::End();

        // ImGui::Begin("Window 2", nullptr, ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoCollapse);
        // // Window contents
        // ImGui::End();

        // Render ImGui
        ImGui::Render();

        glViewport(0, 0, (int)ImGui::GetIO().DisplaySize.x, (int)ImGui::GetIO().DisplaySize.y);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        // Rendere the Imgui Data using OPenGL backend
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
    }

    // Cleanup
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}

static void MouseButtonCallback(GLFWwindow *window, int button, int action, int mods)
{
    if (button == GLFW_MOUSE_BUTTON_LEFT && action == GLFW_PRESS)
    {
        ImGui_ImplGlfw_MouseButtonCallback(window, button, action, mods);
    }
}

// #include <imgui.h>
// #include <imgui_impl_glfw.h>
// #include <imgui_impl_opengl3.h>
// #include <GLFW/glfw3.h>

// #include <opencv2/opencv.hpp>
// #include <cstdio>

// int main()
// {
//     // Initialize GLFW
//     glfwInit();
//     GLFWwindow *window = glfwCreateWindow(800, 600, "ImGui Example", nullptr, nullptr);
//     glfwMakeContextCurrent(window);
//     glfwSwapInterval(1); // Enable vsync

//     // Initialize ImGui
//     IMGUI_CHECKVERSION();
//     ImGui::CreateContext();
//     ImGuiIO &io = ImGui::GetIO();
//     (void)io;

//     ImGui::StyleColorsDark();

//     // Initialize ImGui GLFW and OpenGL3 backend
//     ImGui_ImplGlfw_InitForOpenGL(window, true);
//     ImGui_ImplOpenGL3_Init("#version 330");

//     cv::Mat cvImage;
//     cvImage= cv::imread("/media/dati/Develop/ai4prod_repo/Coding/ai4prod_ui/example/Cpp_native/dog.jpg");

//     // Main loop
//     while (!glfwWindowShouldClose(window))
//     {
//         glfwPollEvents();

//         // Start the ImGui frame
//         ImGui_ImplOpenGL3_NewFrame();
//         ImGui_ImplGlfw_NewFrame();
//         ImGui::NewFrame();

//         // Create a simple window
//         ImGui::Begin("Hello, ImGui!");

//         // Add a button
//         if (ImGui::Button("Click Me!"))
//         {
//             // Button is clicked, perform some action
//             // (For this example, we will just print a message)
//             printf("Button is clicked!\n");
//         }

//         cv::Mat cvImageRGBA;
//         cv::cvtColor(cvImage, cvImageRGBA, cv::COLOR_BGR2RGBA);
//         const unsigned char *imagePixels = cvImageRGBA.ptr<unsigned char>();

//         // Get the image dimensions
//         int imageWidth = cvImage.cols;
//         int imageHeight = cvImage.rows;

//         // Create an ImGui texture from the image data
//         ImTextureID textureID = ImGui::GetIO().Fonts->TexID;
//         ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
//         textureID = ImGui::GetIO().Fonts->TexID;
//         ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
//         ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
//         ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;

//         // Display the image using ImGui
//         ImGui::Image(textureID, ImVec2(imageWidth, imageHeight));

//         // Restore the original ImGui texture ID
//         ImGui::GetIO().Fonts->TexID = textureID;

//         ImGui::End();

//         // Rendering
//         ImGui::Render();
//         int display_w, display_h;
//         glfwGetFramebufferSize(window, &display_w, &display_h);
//         glViewport(0, 0, display_w, display_h);
//         glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
//         glClear(GL_COLOR_BUFFER_BIT);
//         ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
//         glfwSwapBuffers(window);
//     }

//     // Cleanup
//     ImGui_ImplOpenGL3_Shutdown();
//     ImGui_ImplGlfw_Shutdown();
//     ImGui::DestroyContext();
//     glfwDestroyWindow(window);
//     glfwTerminate();

//     return 0;
// }