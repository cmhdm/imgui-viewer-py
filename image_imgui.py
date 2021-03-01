# Image_Imgui displays a numpy array in an external window
# Only 8bit RGB-images work. Data can be both float and uint
# Only one image can be displayed at a time. Python interpreter paused while Window is open
# Zoom is fixed by Zoom-slider from 1% to 200%
# TODO: - multiple images displayed simultaniously. Multithreading / thread
#       - mouse zoom and scroll

# Dependencies numpy, Imgui[glfw], OpenGL use !pip install
import numpy as np

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

# display functions calls main() and transmits imagedata to Renderer
# standard zoom is 100 which is a 1:1 display
# zoom can be changed interactivly and while calling display function

# display can except multiple images args* -> what modifications in main
# same zoom? easier...

def display(bild, zoom = 100):
    '''
    Display Image via Imgui
    '''
    # multiple pictures?
    # float or int: GL_FLOAT, or  GL_UNSIGNED_BYTE
    bild = check_dim(bild)
    dt = bild.dtype
    texture_data = bild[:,:,:3]
    width = texture_data.shape[1]
    height = texture_data.shape[0]
    texture_id = None
    # print(dt)
    main(width, height, texture_data, texture_id, zoom, dt)

def zoom_factor(z):
    z = z/100
    if z >= 1:
        return z ** 3.322
    elif z < 1:
        return z*0.9 + 0.1
    else:
        return 1

def check_dim(a):
    if isinstance(a, np.ndarray):
        s = a.shape
        if len(s) == 3:
            if s[2] == 3:
                return a
            elif s[2] == 1:
                return np.repeat(a, 3, axis=2)
            else:
                print('Fehler_3D, Dimension des Input-Arrays inkompatibel')
        elif len(s) == 2:
            return np.repeat((np.reshape((a), (s[0],s[1],1))), 3, axis=2)
        else:
            print('Fehler_3D_2D, Dimension des Input-Arrays inkompatibel')
    else:
        print('Fehler, Input ist kein Array.')

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

    # Make sure the supplied image is converted to float32 and normalized if input data is
    # in an integer format.
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
        imgui.image(texture_id, float(width*zoom_factor(zoom)), float(height*zoom_factor(zoom)))
        imgui.end()

        # Slider
        imgui.begin("Zoom", True)
        imgui.set_window_size(250, 150, imgui.FIRST_USE_EVER)
        changed, zoom = imgui.slider_int("Zoom 10% - 1000%", zoom, min_value=1, max_value=200, 
                                        format="{}".format(str(int(zoom_factor(zoom)*100)) ) )
        imgui.text("Changed: %s" % (changed))
        # reset Zoom
        z_reset =  imgui.button("Zoom 100%", 80, 40)
        imgui.end()

        if z_reset:
            zoom = 100

        gl.glClearColor(.25, .25, .25, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    fenster = glfw.get_window_size(window)
    print(fenster)
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

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    # For debugging, just to check if 10, 10, 10, 2 rendering surface or 8, 8, 8, 8
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