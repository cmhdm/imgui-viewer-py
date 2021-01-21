# Image_Imgui displays a numpy array in an external window
# Only 8bit RGB-images work. Data can be both float and uint
# Only one image can be displayed at a time. Python interpreter paused while Window is open
# Zoom is fixed by Zoom-slider from 1% to 200%
# TODO: - multiple images displeyed simultaniously.
#       - mouse zoom and scroll
#       - 10bit image display
#       - grayscale Array
#       - reset scale to 100% "pressing button"
#       - optimize Zoom 1% - 1000% Log_scale 100% midpoint

# Dependencies numpy, Imgui[glfw], OpenGL use !pip install
import numpy as np

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

# display functions calls main() and transmits imagedata to Renderer
# standard zoom is 100 which is a 1:1 display
# zoom can be changed interactivly and while calling display function
def display(bild, zoom = 100):
    '''
    Display Image via Imgui
    '''
    # multiple pictures?
    # float or int: GL_FLOAT, or  GL_UNSIGNED_BYTE
    dt = bild.dtype
    texture_data = bild[:,:,:3]
    width = texture_data.shape[1]
    height = texture_data.shape[0]
    texture_id = None
    # print(dt)
    main(width, height, texture_data, texture_id, zoom, dt)

# main function that generates the window and image output    
def main(width, height, texture_data, texture_id, zoom, dt):
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

    tex_data_converted = None
    dt_str = str(dt)
    if 'int' in dt_str:
        tex_data_converted = np.float32(texture_data) / np.iinfo(dt).max
    elif dt_str.startswith('float'):
        tex_data_converted = np.float32(texture_data)
    else:
        print("Image array must have a float or integer type. Not:", dt)
        raise TypeError

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB32F, width, height, 0, gl.GL_RGB,
        gl.GL_FLOAT, tex_data_converted)
    
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

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)

    # OS X supports only forward-compatible core profiles from 3.2
    # # Original setup for mac compatibility. Doesn't allow checking bit
    # # depth on Linux at least thus commented out
    # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    redBits = gl.glGetIntegerv(gl.GL_RED_BITS)
    greenBits = gl.glGetIntegerv(gl.GL_GREEN_BITS)
    blueBits = gl.glGetIntegerv(gl.GL_BLUE_BITS)
    alphaBits = gl.glGetIntegerv(gl.GL_ALPHA_BITS)
    print('opengl bit depths [RGBA]: ', redBits, greenBits, blueBits, alphaBits)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

if __name__ == "__main__":
        main()