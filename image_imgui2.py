import numpy as np

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

def test_func(bild):
    print(bild)

def display(bild, zoom = 100):
    '''
    Display Image via Imgui
    '''
    # multiple pictures?
    # check if float or int: GL_FLOAT, or  GL_UNSIGNED_BYTE
    texture_data = bild[:,:,:3]
    width = texture_data.shape[1]
    height = texture_data.shape[0]
    texture_id = None
    main(width, height, texture_data, texture_id, zoom)
    
def main(width, height, texture_data, texture_id, zoom):
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
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB,
    gl.GL_FLOAT, texture_data)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        
        # Image
        imgui.begin("Image", True, flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        imgui.image(texture_id, float(width*(zoom/100.0)), float(height*(zoom/100.0)))
        imgui.end()

        # Slider
        imgui.begin("Zoom", True)
        changed, zoom = imgui.slider_int("slide ints", zoom, min_value=1, max_value=200, format="%d")
        imgui.text("Changed: %s, Values: %s" % (changed, zoom))
        imgui.end()

        gl.glClearColor(.25, .25, .25, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
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