# Image_Imgui displays a numpy array in an external window
# Only 8bit RGB-images work. Data can be both float and uint
# Only one image can be displayed at a time. Python interpreter paused while Window is open
# Zoom is fixed by Zoom-slider from 1% to 200%
# TODO: - multiple images displayed simultaniously. Multithreading / thread
#       - mouse zoom and scroll
#       - 10bit image display
#       - grayscale Array 2D to 3D  [:,:,none]

# Dependencies numpy, Imgui[glfw], OpenGL use !pip install
import numpy as np

import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

from multiprocessing import Process, current_process, Queue



def zoom_factor(z):
    z = z/100
    if z >= 1:
        return z ** 3.322
    elif z < 1:
        return z*0.9 + 0.1
    else:
        return 1

# display functions calls main() and transmits imagedata to Renderer
# standard zoom is 100 which is a 1:1 display
# zoom can be changed interactivly and while calling display function

# display can except multiple images args* -> what modifications in main
# same zoom? easier...

def imguiThreadWorker(queue, window_name = 'PyImageViewer'):
    running = True

    zoom = 100

    imgui.create_context()
    window = impl_glfw_init(window_name=window_name)
    impl = GlfwRenderer(window)

    textures = []  # List of texture IDs + labels
    
    loop_count = 0
    img_cnt = 0

    while (not glfw.window_should_close(window)) and running:
        # Poll queue
        try:
            entry = queue.get(block=False)
            if isinstance(entry, str) and entry == 'STOP':
                running = False
            elif type(entry) is tuple:
                print('New image: ', entry[0].shape, entry[0].dtype, entry[1])
                texture_id = gl.glGenTextures(1)
                gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
                gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
                gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
                gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

                texture_data = entry[0]
                width = texture_data.shape[1]
                height = texture_data.shape[1]
                tex_data_converted = None
                dt = texture_data.dtype
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
                # gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

                textures.append((texture_id, 'Image' + str(img_cnt) + ': ' + entry[1]))
        except:
            pass

        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        
        # Images
        # if loop_count == 0:
        #     print('Num textures: ', len(textures))
        # loop_count = (loop_count + 1) % 150
        for image_idx in range(len(textures)):
            # if image_idx > 0:
            #     print('Image IDX > 0')
            tex = textures[image_idx]
            imgui.begin(tex[1], True, flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
            imgui.image(tex[0], float(width*zoom_factor(zoom)), float(height*zoom_factor(zoom)))
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

    impl.shutdown()
    glfw.terminate()

class ImageViewer:
    def __init__(self, image = None, label = None):
        self.queue = Queue(3)
        if image:
            self.display(image, label)
        
        self.worker_process = Process(target = imguiThreadWorker,
                args = (self.queue,),
                name = 'ImGui worker thread',
                daemon = True)
        self.worker_process.start()

    def __del__(self):
        self.queue.put('STOP')
        self.worker_process.join()
        

    def display(self, image, label = ''):
        self.queue.put((image, label))


# shared_iv = None

# def display(image, label = ''):
#     '''
#     Display Image via Imgui
#     '''
#     global shared_iv
#     if shared_iv is None:
#         shared_iv = ImageViewer()
#     shared_iv.display(image, label)
    


# def zoom_factor(z):
#     z = z/100
#     if z >= 1:
#         return z ** 3.322
#     elif z < 1:
#         return z*0.9 + 0.1
#     else:
#         return 1

# def check_dim(a):
#     # check if array if not return Error
#     # check what dimension 2D, 3D? All else Error (1D?)
#     # if 3D how many values in 3. Dimension
#     # do: modify arrays
#     # return modified array
#     pass

# # main function that generates the window and image output    
# def main(width, height, texture_data, texture_id, zoom, dt):
#     imgui.create_context()
#     window = impl_glfw_init()
#     impl = GlfwRenderer(window)

#     texture_id = gl.glGenTextures(1)
#     gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
#     gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
#     gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
#     gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
#     gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
#     gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

#     # Make sure the supplied image is converted to float32 and normalized if input data is
#     # in an integer format.
#     tex_data_converted = None
#     dt_str = str(dt)
#     if 'int' in dt_str:
#         tex_data_converted = np.float32(texture_data) / np.iinfo(dt).max
#     elif dt_str.startswith('float'):
#         tex_data_converted = np.float32(texture_data)
#     else:
#         print("Image array must have a float or integer type. Not:", dt)
#         raise TypeError

#     gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB32F, width, height, 0, gl.GL_RGB,
#         gl.GL_FLOAT, tex_data_converted)
    
#     gl.glGenerateMipmap(gl.GL_TEXTURE_2D)


#     while not glfw.window_should_close(window):
#         glfw.poll_events()
#         impl.process_inputs()
#         imgui.new_frame()
        
#         # Image
#         imgui.begin("Image", True, flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
#         imgui.image(texture_id, float(width*zoom_factor(zoom)), float(height*zoom_factor(zoom)))
#         imgui.end()

#         # Slider
#         imgui.begin("Zoom", True)
#         imgui.set_window_size(250, 150, imgui.FIRST_USE_EVER)
#         changed, zoom = imgui.slider_int("Zoom 10% - 1000%", zoom, min_value=1, max_value=200, 
#                                         format="{}".format(str(int(zoom_factor(zoom)*100)) ) )
#         imgui.text("Changed: %s" % (changed))
#         # reset Zoom
#         z_reset =  imgui.button("Zoom 100%", 80, 40)
#         imgui.end()

#         if z_reset:
#             zoom = 100

#         gl.glClearColor(.25, .25, .25, 1)
#         gl.glClear(gl.GL_COLOR_BUFFER_BIT)

#         imgui.render()
#         impl.render(imgui.get_draw_data())
#         glfw.swap_buffers(window)

#     impl.shutdown()
#     glfw.terminate()


def impl_glfw_init(window_name):
    width, height = 1280, 720

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

# # if __name__ == "__main__":
# #         main()