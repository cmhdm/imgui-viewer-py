# Imgui-Viewer for Python

Goal: Open new window with minimal controls and precise pixel representation

## Pyglet
https://pyglet.readthedocs.io/en/latest/index.html
Pyglet ist used as a first approach to achieve the goal.
Pyglet - Numpy
At the moment Numpy can not access Image Data.
https://stackoverflow.com/questions/3165379/how-to-display-a-numpy-array-with-pyglet

Pyglet is not used for further development -> Pyimgui

## Pyimgui
Pyimgui in combination with GLFW and Open GL is used. Pyimgui is a python wrapper for imgui (https://pyimgui.readthedocs.io/en/latest/#).
The main function generates a new window on the desktop with windows inside to display the image.

## Fully functional version
multi_image_viewer.py allows for multiple images to be displayed. Because of multithread the Jupyter-Notebook can operate and add images to be displayed while the Viewer-Window is open. The Jupyter-Notebook "multithreaded_test.ipynb" is exemplarily for how to work with multi_image_viewer.py.

## Zoom and Drag
Zoom implemented with a dragbar is working. -> imgui-v001.py
Zoom with Scroll and Drag with Click and Drag. 
Max and Min for both Zoom an Drag

Zoom and Drag Image is under development. Current issues:
- zoom with mousewheel gets stuck when scrolling down
- drag image extends texture instead of moving the image

## 10 Bit Data
Solution by irieger: If Display allows 10bit, 10bit will be displayed. Generates also output at what bitdepth the image is displayed
