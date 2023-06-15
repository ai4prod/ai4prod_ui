

#include <imgui.h>
#include <imgui_impl_glfw.h>
#include <imgui_impl_opengl3.h>
#include <GLFW/glfw3.h>

#include <opencv2/opencv.hpp>
#include <cstdio>

int main()
{
    // Initialize GLFW
    glfwInit();
    GLFWwindow *window = glfwCreateWindow(800, 600, "ImGui Example", nullptr, nullptr);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1); // Enable vsync

    // Initialize ImGui
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO &io = ImGui::GetIO();
    (void)io;

    ImGui::StyleColorsDark();

    // Initialize ImGui GLFW and OpenGL3 backend
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init("#version 330");

    cv::Mat cvImage;
    cvImage= cv::imread("../dog.jpg");
    
    // Main loop
    while (!glfwWindowShouldClose(window))
    {
        glfwPollEvents();

        // Start the ImGui frame
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        // Create a simple window
        ImGui::Begin("Hello, ImGui!");

        // Add a button
        if (ImGui::Button("Click Me!"))
        {
            // Button is clicked, perform some action
            // (For this example, we will just print a message)
            printf("Button is clicked!\n");
        }

        cv::Mat cvImageRGBA;
        cv::cvtColor(cvImage, cvImageRGBA, cv::COLOR_BGR2RGBA);
        const unsigned char *imagePixels = cvImageRGBA.ptr<unsigned char>();

        // Get the image dimensions
        int imageWidth = cvImage.cols;
        int imageHeight = cvImage.rows;

        // Create an ImGui texture from the image data
        ImTextureID textureID = ImGui::GetIO().Fonts->TexID;
        ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
        textureID = ImGui::GetIO().Fonts->TexID;
        ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
        ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;
        ImGui::GetIO().Fonts->TexID = (void *)(intptr_t)textureID;

        // Display the image using ImGui
        ImGui::Image(textureID, ImVec2(imageWidth, imageHeight));

        // Restore the original ImGui texture ID
        ImGui::GetIO().Fonts->TexID = textureID;

        ImGui::End();

        // Rendering
        ImGui::Render();
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
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