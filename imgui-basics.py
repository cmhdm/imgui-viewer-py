# This is the imgui-sample reduced to the minimum

# install all dependecies for imgui "pip install imgui[glfw, pygame, pyglet, opengl]"

import numpy as np
import imageio
#import pyautogui # used only for display size -> glfw has class monitor

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

# execute once
# imageio.plugins.freeimage.download()

image = imageio.imread('Assets/Exercise_01_Peppers.png') # 16bit does not result in a correct representation
texture_data = image[:,:,:3]
width_image = texture_data.shape[1]
height_image = texture_data.shape[0]

# check size of current display DEPENDECY PYAUTOGUI (pip install pyautogui)
display_size = pyautogui.size()
width_display = display_size.width
height_display = display_size.height

# compare image-size to display-size
if width_display < width_image:
    width = width_display
else:
    width = width_image

if height_display < height_image:
    height = height_display
else:
    height = height_image

texture_id = None

# calculate zoom-factor
def zoom_factor(mouse_input):
    zoom_min = 0.1
    zoom_max = 100.0
    zoom_default = 1.0

    zoom = default_zoom
    
    if zoom > zoom_max:
        zoom = zoom_max
    
    if zoom < zoom_min:
        zoom = zoom_min

    return zoom
    
def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    texture_id = gl.glGenTextures(1)
    gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width_image, height_image, 0, gl.GL_RGB,
        gl.GL_UNSIGNED_BYTE, texture_data)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        imgui.begin("image", True)
        zoom = 1
        print(imgui.core.get_scroll_y())
        imgui.image(texture_id, float(width_image*zoom), float(height_image*zoom))
        imgui.end()

        gl.glClearColor(.25, .25, .25, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = width_display, height_display
    window_name = "ImGui"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

if __name__ == "__main__":
    main()