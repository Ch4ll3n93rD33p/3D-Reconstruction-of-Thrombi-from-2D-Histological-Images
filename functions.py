import numpy as np
import random 
import os
from statistics import mode
from bisect import bisect
import matplotlib.pyplot as plt
from matplotlib.image import imsave
import cv2
from skimage.color import rgb2gray
import sklearn.cluster as skcl
from skimage import transform as tf
from pystackreg import StackReg
import scipy
import copy
import vtk
from vtk.util import numpy_support # pyright: ignore[reportMissingImports]


############## Images creation ##############

### Volumes

def rectangular_cuboid_vox(centre : np.ndarray, dimensions : np.ndarray, x : np.ndarray, y : np.ndarray, z : np.ndarray, axis: np.ndarray = np.array([0,0,1])) -> np.ndarray :
    '''
    Creates a voxel array representing a rectangular cuboid with a given center, size, and orientation.  

    Parameters :
    - centre (np.ndarray): Coordinates of the cuboid center point.
    - dimensions (np.ndarray): Lengths of the cuboid along its three local axes. The first dimension corresponds to the specified axis, while the other two correspond to the orthogonal directions.
    - x (np.ndarray): Array of x-coordinate values defining the voxel grid.
    - y (np.ndarray): Array of y-coordinate values defining the voxel grid.
    - z (np.ndarray): Array of z-coordinate values defining the voxel grid.
    - axis (np.ndarray, optional): Orientation vector defining the main axis of the cuboid. Default is [0, 0, 1].

    Returns :
    - cuboid (np.ndarray): Boolean voxel array with the same shape as the input coordinate grids. True values indicate voxels located inside the cuboid, and False values indicate voxels outside the cuboid.
    '''

    axis = axis / np.linalg.norm(axis)
    
    # creation of two orthogonal axis
    if abs(axis[0]) < 0.9 :
        arb_vec = np.array([1,0,0]) 
    else : 
        np.array([0,1,0])
    u = np.cross(axis, arb_vec)
    u = u / np.linalg.norm(u)
    v = np.cross(axis, u)


    # projections
    proj_axis = (x-centre[0])*axis[0] + (y-centre[1])*axis[1] + (z-centre[2])*axis[2]
    proj_u = (x-centre[0])*u[0] + (y-centre[1])*u[1] + (z-centre[2])*u[2]
    proj_v = (x-centre[0])*v[0] + (y-centre[1])*v[1] + (z-centre[2])*v[2]

    cuboid = ((np.abs(proj_axis) <= dimensions[0]/2) & (np.abs(proj_u) <= dimensions[1]/2) & (np.abs(proj_v) <= dimensions[2]/2))    
    return cuboid

def cylinder_vox(centre : np.ndarray, radius : int, height : int, x : np.ndarray, y : np.ndarray, z : np.ndarray, axis: np.ndarray = np.array([0,0,1])) -> np.ndarray :
    '''
    Creates a voxel array representing a cylinder with a specified center, radius, height, and orientation.

    Parameters :
    - centre (np.ndarray): Coordinates of the cylinder center point.
    - radius (int): Radius of the cylinder.
    - height (int): Height of the cylinder along its axis.
    - x (np.ndarray): Array of x-coordinate values defining the voxel grid.
    - y (np.ndarray): Array of y-coordinate values defining the voxel grid.
    - z (np.ndarray): Array of z-coordinate values defining the voxel grid.
    - axis (np.ndarray, optional): Orientation vector defining the cylinder axis. Default is [0, 0, 1].

    Returns :
    - cyl (np.ndarray): Boolean voxel array with the same shape as the input coordinate grids. True values indicate voxels located inside the cylinder, and False values indicate voxels outside the cylinder.
    '''
    axis = axis / np.linalg.norm(axis)

    # projection on axis
    proj_axis = (x-centre[0])*axis[0]+(y-centre[1])*axis[1]+(z-centre[2])*axis[2]

    cyl = (np.sqrt(np.maximum(0, (x-centre[0])**2+(y-centre[1])**2+(z-centre[2])**2-proj_axis**2)) <= radius) & (np.abs(proj_axis) <= height/2)

    return cyl

def sphere_vox(centre : np.ndarray, radius : int, x : np.ndarray, y : np.ndarray, z : np.ndarray) -> np.ndarray :
    '''
    Creates a voxel array representing a sphere with a specified center and radius.

    Parameters :
    - centre (np.ndarray): Coordinates of the sphere center point.
    - radius (int): Radius of the sphere.
    - x (np.ndarray): Array of x-coordinate values defining the voxel grid.
    - y (np.ndarray): Array of y-coordinate values defining the voxel grid.
    - z (np.ndarray): Array of z-coordinate values defining the voxel grid.

    Returns :
    - s (np.ndarray): Boolean voxel array with the same shape as the input coordinate grids. True values indicate voxels located inside the sphere, and False values indicate voxels outside the sphere.
    '''
    s = (((x-centre[0])**2+(y-centre[1])**2+(z-centre[2])**2) <= radius**2)

    return s

def torus_vox(centre : np.ndarray, centre_radius : int, tube_radius : int, x : np.ndarray, y : np.ndarray, z : np.ndarray, axis : np.ndarray = np.array([0, 0, 1])) -> np.ndarray :
    '''
    Creates a voxel array representing a torus with a specified center, major radius, tube radius, and orientation.

    Parameters :
    - centre (np.ndarray): Coordinates of the torus center point.
    - centre_radius (int): Distance from the torus center to the center of the tube (major radius).
    - tube_radius (int): Radius of the torus tube (minor radius).
    - x (np.ndarray): Array of x-coordinate values defining the voxel grid.
    - y (np.ndarray): Array of y-coordinate values defining the voxel grid.
    - z (np.ndarray): Array of z-coordinate values defining the voxel grid.
    - axis (np.ndarray, optional): Orientation vector defining the torus axis. Default is [0, 0, 1].

    Returns :
    - t(np.ndarray): Boolean voxel array with the same shape as the input coordinate grids. True values indicate voxels located inside the torus tube, and False values indicate voxels outside the torus.
    
    '''

    axis = axis / np.linalg.norm(axis)
    proj_axis = (x - centre[0])*axis[0] + (y - centre[1])*axis[1] + (z - centre[2])*axis[2]

    t = ((centre_radius-np.sqrt(np.maximum(0, ((x-centre[0])**2+(y-centre[1])**2+(z-centre[2])**2)-proj_axis**2)))**2+proj_axis**2) < tube_radius**2
    
    return t

### Colors operations

def hexa_to_rgb(hexa_str : str) -> tuple[int, int, int] : 
    '''
    Converts a hexadecimal color string into its corresponding RGB color representation.

    Parameters :
    - hexa_str (str): A string starting with # containing the hexadecimal color code.

    Returns :
    - r (int): Red channel value of the color, ranging from 0 to 255.
    - g (int): Green channel value of the color, ranging from 0 to 255.
    - b (int): Blue channel value of the color, ranging from 0 to 255.
    '''
    h = hexa_str.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))

    return r, g, b

def rgb_to_hexa(r : int, g : int, b : int) -> str :
    '''
    Converts an RGB color representation into a hexadecimal color string.

    Parameters :
    - r (int): Red channel value of the color, ranging from 0 to 255.
    - g (int): Green channel value of the color, ranging from 0 to 255.
    - b (int): Blue channel value of the color, ranging from 0 to 255.

    Returns :
    - hexa_str (str): String containing the hexadecimal color code corresponding to the RGB values, starting with #.
    '''
    hexa_str = '#%02x%02x%02x'%(r, g, b)
    return hexa_str

def color_mix(color1 : str, color2 : str) -> str : 
    '''
    Creates a new color by averaging the RGB channel values of two input colors.

    Parameters :
    - color1 (str): First color expressed as a hexadecimal color code string starting with #.
    - color2 (str): Second color expressed as a hexadecimal color code string starting with #.

    Returns :
    - new_color (str): Resulting mixed color expressed as a hexadecimal color code string starting with #.
    '''
    r1, g1, b1 = hexa_to_rgb(color1)
    r2, g2, b2 = hexa_to_rgb(color2)
    r = (r1+r2)//2
    g = (g1+g2)//2
    b = (b1+b2)//2
    new_color = rgb_to_hexa(r, g, b)

    return new_color

### Image transformations

def padding(images : list[np.ndarray], background_color : str = '#ffffff', size : list[int, int] = [None, None], mode : str = 'def') -> list[np.ndarray] :
    '''
    Adds padding around images to ensure that objects remain visible after image transformations. 
    The function supports two padding modes: a default mode that adds padding equal to half the image size on each side, and a resize mode that adds padding to reach a specified target size.
    
    Parameters :
    - images (list[np.ndarray]): List of RGB images to be padded.
    - background_color (str, optional): Background color used for the padding, expressed as a hexadecimal color code string starting with #. Default is '#ffffff'.
    - size (list[int, int], optional): Target image size [x, y] used when mode='resize'. Default is [None, None].
    - mode (str, optional): Padding mode selection. 'def' adds padding equal to half the image dimensions on each side. 'resize' adds padding to reach the specified size. Default is 'def'.

    Returns :
    - new_images (list[np.ndarray]): List of padded RGB images. Each image contains the original image content with additional padding filled with the specified background color.
    '''
    if mode == 'def' :
        x = images[0].shape[0]//2
        y = images[0].shape[1]//2
        p = list(hexa_to_rgb(background_color))
        new_images = []
        for img in images :
            padded= cv2.copyMakeBorder(img, x, x, y, y, cv2.BORDER_CONSTANT, value=p)
            new_images.append(padded)

    elif mode == 'resize' :
        new_images = []
        for img in images :
            x = size[0]-img.shape[0]
            y = size[1]-img.shape[1]
            p = list(hexa_to_rgb(background_color))
            padded= cv2.copyMakeBorder(img, x, 0, y, 0, cv2.BORDER_CONSTANT, value=p)
            new_images.append(padded)
    
    
    return new_images

def translation(image : np.ndarray, t : tuple[int, int] = (None, None)) -> np.ndarray :
    '''
    Computes the transformation matrix required to translate an image. If no translation values are provided, random translation offsets are generated based on half of the image dimensions.
    
    Parameters :
    - image (np.ndarray): Image to be translated.
    - t (tuple[int, int], optional): Tuple (x, y) representing the desired translation offsets along the two image axes. If both values are None, random translation values are generated. Default is (None, None).
    
    Returns :
    - T (np.ndarray): 3×3 transformation matrix representing the translation operation.
    '''
    x, y = t
    if (x, y) == (None, None) :
        x = random.randint(0, image.shape[0]//2)
        y = random.randint(0, image.shape[1]//2)
    T = np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])

    return T

def rotation(image : np.ndarray, theta : float = None) -> np.ndarray : 
    '''
    Computes the transformation matrix required to rotate an image around its center. If no rotation angle is provided, a random angle between 0 and \(2\pi\) radians is generated.

    Parameters :
    - image (np.ndarray): Image to be rotated. The image dimensions are used to determine the rotation center.
    - theta (float, optional): Rotation angle in radians. If None, a random angle between 0 and \(2\pi\) is generated. Default is None.
    
    Returns :
    - T (np.ndarray): 3×3 transformation matrix representing the rotation around the image center.
    '''
    centre = (image.shape[0]/2, image.shape[1]/2)

    if theta == None :
        theta = random.random()*2*np.pi

    t = translation(image, centre)
    revers_t = translation(image, (-centre[0], -centre[1]))
    rotation = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, 1]])
    T = np.dot(np.dot(t, rotation), revers_t)

    return T

def transform(image : np.ndarray, T : np.ndarray) -> np.ndarray :
    '''
    Applies a geometric transformation to an image using a given transformation matrix.

    Parameters :
    - image (np.ndarray): Image to be transformed.
    - T (np.ndarray): 3×3 affine transformation matrix defining the transformation to apply to the image.

    Returns :
    - transfo_image (np.ndarray): Transformed image. Pixels outside the original image boundaries are filled using the edge color of the image.
    '''
    t = tf.AffineTransform(matrix=T)
    transfo_image = tf.warp(image, t, mode = 'edge') # mode : pads the out of bounds points with edge color
    transfo_image = np.array(transfo_image*255, dtype = np.uint8)
    return transfo_image

### Create slices

def inh_container(background : np.ndarray, objects : list[np.ndarray]) -> np.ndarray :
    '''
    Performs an inhibition operation on a background voxel array by removing the regions occupied by other objects.

    Parameters :
    - background (np.ndarray): Boolean voxel array representing the background object that contains the other objects.
    - objects (list[np.ndarray]): List of boolean voxel arrays representing the objects contained inside the background.

    Returns :
    - background (np.ndarray): Updated boolean voxel array representing the background after removing the voxels occupied by the objects.
    '''
    if len(objects) < 0 :
        intern = objects[0]

        for i in range(1, len(objects)) :
            intern = intern | objects[i]
        
        background = np.logical_and(background, np.logical_not(intern))

    return background

def compute_intersections(index : int, objects : list[np.ndarray]) -> tuple[list[int], list[np.ndarray]] :
    '''
    Computes the intersections between a selected object and all other objects in a list of voxel arrays.

    Parameters :
    - index (int): Index of the target object in the objects list for which intersections are computed.
    - objects (list[np.ndarray]): List of boolean voxel arrays representing all objects in the scene.

    Returns :
    - obj_indexes (list[int]): List of indexes corresponding to the objects that intersect with the target object.
    - intersec (list[np.ndarray]): List of boolean voxel arrays representing the intersection regions between the target object and the intersecting objects.

    '''
    obj_indexes = []
    intersec = []

    for i in range(len(objects)) :

        if i == index :
            pass

        else :
            and_obj = np.logical_and(objects[index], objects[i])

            if True in and_obj :
                obj_indexes.append(i)
                intersec.append(and_obj)
    
    return obj_indexes, intersec

def color_objects(background : np.ndarray, objects : list[np.ndarray], colors : list[str], background_color : str = '#ffffff', with_intersections : bool = False) -> np.ndarray :
    '''
    Assigns colors to a background voxel array and a collection of objects, generating a color array corresponding to each voxel. The function supports optional color mixing for voxels where objects overlap.

    Parameters :
    - background (np.ndarray): Boolean voxel array representing the background object. It is used to determine the voxels that should receive the background object color.
    - objects (list[np.ndarray]): List of boolean voxel arrays representing the objects contained within the background.
    - colors (list[str]): List of hexadecimal color strings used to color the background and objects. The first color corresponds to the background, and subsequent colors correspond to the objects.
    - background_color (str, optional): Hexadecimal color string used for voxels outside the background object. The string must start with #. Default is '#ffffff'.
    - with_intersections (bool, optional): If True, overlapping regions between objects are assigned a mixed color obtained by averaging the colors of the intersecting objects. Default is False.

    Returns :
    - facecolor (np.ndarray): Array containing the hexadecimal color value assigned to each voxel. Each voxel is colored according to whether it belongs to the background, an object, or an intersection region.

    '''
    facecolor = np.full(background.shape, background_color)
    c = inh_container(background, objects)
    facecolor[np.where(c)] = colors[0] # background color added

    for i in range(len(objects)) :
        
        obj_indexes = []
        if with_intersections :
            obj_indexes, intersec = compute_intersections(i, objects)

        if len(obj_indexes) == 0 : # no intersections
            facecolor[np.where(objects[i])] = colors[i+1]

        else :
            o = inh_container(objects[i], objects[:i]+objects[i+1:]) # object [i]\intersections
            facecolor[np.where(o)] = colors[i+1]
            for j in range(len(obj_indexes)) :
                new_color = color_mix(colors[i+1], colors[obj_indexes[j]+1])
                facecolor[np.where(intersec[j])] = new_color

    return facecolor

def facecolor_to_rgb(facecolor : np.ndarray) -> np.ndarray : 
    '''
    Converts a 2D array of hexadecimal color strings into an RGB image matrix.

    Parameters :
    - facecolor (np.ndarray): 2D array of hexadecimal color strings representing the color assigned to each voxel in a slice of a 3D color array.

    Returns :
    - rgbcolor (np.ndarray): RGB image matrix corresponding to the input color array. Each pixel contains its red, green, and blue channel values.
    '''
    r = np.zeros(facecolor.shape, dtype = np.uint8)
    g = np.zeros(facecolor.shape, dtype = np.uint8)
    b = np.zeros(facecolor.shape, dtype = np.uint8)

    for i in range(facecolor.shape[0]) :
        for j in range(facecolor.shape[1]) :
            r[i][j], g[i][j], b[i][j] = hexa_to_rgb(facecolor[i][j])
    
    rgbcolor = cv2.merge([r, g, b])

    return rgbcolor

def slice(facecolor : np.ndarray, axis : str = 'z') -> list[np.ndarray] :
    '''
    Extracts 2D image slices from a 3D voxel color array along a specified axis. Each slice is converted from a hexadecimal color representation into an RGB image format.

    Parameters :
    - facecolor (np.ndarray): 3D array of hexadecimal color strings representing the color assigned to each voxel.
    - axis (str, optional): Axis along which the 3D array is sliced. Possible values are 'x', 'y', or 'z'. Default is 'z'.

    Returns :
    - images (list[np.ndarray]): List of RGB image arrays corresponding to the 2D slices extracted from the 3D voxel color array.
    '''
    images = []

    if axis == 'x' :
        for i in range(facecolor.shape[0]) :
            rgbslice = facecolor_to_rgb(facecolor[i, :, :])
            images.append(rgbslice)

    elif axis == 'y' :
        for i in range(facecolor.shape[1]) :
            rgbslice = facecolor_to_rgb(facecolor[:, i, :])
            images.append(rgbslice)

    else :
        for i in range(facecolor.shape[2]) :
            rgbslice = facecolor_to_rgb(facecolor[:, :, i])
            images.append(rgbslice)

    return images

def slice_object(voxelarray : np.ndarray, facecolor : np.ndarray, color : str = '#ffffff') -> list[np.ndarray] : ### UNUSED ?
    '''
    Creates image slices for a specific object by masking voxels that do not belong to the object with a specified color.

    Parameters :
    - voxelarray (np.ndarray): Boolean voxel array representing the object. Voxels with value True belong to the object, while voxels with value False are replaced by the specified color.
    - facecolor (np.ndarray): 3D array of hexadecimal color strings representing the color assigned to each voxel.
    - color (str, optional): Hexadecimal color string used for voxels outside the object. The string must start with #. Default is '#ffffff'.

    Returns :
    - images (list[np.ndarray]): List of RGB image arrays corresponding to the 2D slices of the masked object.
    '''
    new_facecolor = copy.deepcopy(facecolor)
    new_facecolor = np.where(voxelarray == False, color, facecolor)
    
    images = slice(new_facecolor)

    return images

def unaligne_images(images : np.ndarray, max_r : float, max_t : float, background_color : str = '#ffffff') -> np.ndarray :
    '''
    Applies random misalignment transformations to a set of images trying to simulate alignment errors between images.

    Parameters :
    - images (np.ndarray): Array or list of RGB images to be randomly transformed.
    - max_r (float): Maximum absolute rotation angle in radians. The applied rotation is randomly sampled between -max_r and max_r.
    - max_t (float): Maximum translation value along the first translation axis. The applied translation is randomly sampled between -max_t and max_t.
    - background_color (str, optional): Hexadecimal color string used as the padding background color. The string must start with #. Default is '#ffffff'.

    Returns :
    - new_images (list[np.ndarray]): List of transformed RGB images after applying random rotations and translations.
    '''
    images = padding(images, background_color)
    new_images = []
    for img in images :
        
        r = random.uniform(-max_r, max_r)
        T_r = rotation(img, r)
        img = transform(img, T_r)

        t = random.random()
        
        if t <=2/3 :
            x, y = random.uniform(-max_t, max_t), random.uniform(-5, 5)
            T_t = translation(img, (x, y))
            img = transform(img, T_t)
        
        new_images.append(img)
    
    return new_images

def crop_images(images : np.ndarray, max_c : list[int, int], sym : bool = True, proba : float = 1/5) -> np.ndarray :
    '''
    Randomly crops images by removing pixels from their borders.

    Parameters :
    - images (np.ndarray): Array or list of RGB images to be randomly cropped.
    - max_c (list[int, int]): Maximum cropping values along the two image dimensions. The cropping amount is randomly selected between 1 and each corresponding maximum value.
    - sym (bool, optional): Defines whether the cropping should be symmetric. If True, the same amount is removed from opposite sides of the image. If False, the cropping is randomly distributed between the two sides. Default is True.
    - proba (float, optional): Probability that a given image will be cropped. Default is 1/5.

    Returns :
    - new_images (list[np.ndarray]): List of images after applying random cropping. Images that are not selected for cropping are returned unchanged.
    '''
    new_images = []

    for img in images :
        p = random.random()

        if p < proba :
            x = random.randint(1, max_c[0])
            y = random.randint(1, max_c[1])

            if sym :
                c_x = x//2
                c_y = y//2
                new_images.append(img[c_x:img.shape[0]-c_x, c_y:img.shape[1]-c_y, :])

            else :
                left = random.randint(0, x)
                bottom = random.randint(0, y)
                new_images.append(img[left:img.shape[0]-(x-left), bottom:img.shape[1]-(y-bottom), :])

        else : 
            new_images.append(img)
    
    return new_images

############## 3D object reconstruction ##############

### Image preparation

def image_restoration(images : np.ndarray, masks_path : str, masks_name : str, start : int = 0, format : str = 'png', denoising : bool = False, h : int = 10, hColor : int = 10, templateWindowSize : int = 10, searchWindowSize : int = 20) -> list[np.ndarray] :
    '''
    Restores images by removing masked regions using image inpainting and optionaly denoising.

    Parameters :
    - images (np.ndarray): Array or list of RGB images to be restored.
    - masks_path (str): Path to the directory containing the image masks for inpainting.
    - masks_name (str): Base name of the mask files for inpainting. Masks are expected to follow the naming format masks_name_index.format.
    - start (int, optional): Starting index used when loading mask files. Default is 0.
    - format (str, optional): File format extension of the mask images. Default is 'png'.
    - denoising (bool, optional): If True, applies colored image denoising before inpainting. Default is False.
    - h (int, optional): Filter strength for luminance components in the denoising algorithm. Default is 10.
    - hColor (int, optional): Filter strength for color components in the denoising algorithm. Default is 10.
    - templateWindowSize (int, optional): Size of the template patch used for denoising. Default is 10.
    - searchWindowSize (int, optional): Size of the window used to search for similar patches during denoising. Default is 20.

    Returns :
    - new_images (list[np.ndarray]): List of restored RGB images after mask-based inpainting and optional denoising.
    '''
    masks = [cv2.imread(masks_path+masks_name+'_'+str(i)+'.'+format, 0) for i in range(start,len(images)+start)]
    
    new_images = []
    for i in range(len(images)) :
        img = copy.deepcopy(images[i])
        if denoising :
            img = cv2.fastNlMeansDenoisingColored(img,None, h, hColor, templateWindowSize, searchWindowSize)
        
        restored = cv2.inpaint(img,masks[i],3,cv2.INPAINT_TELEA)
        new_images.append(restored)

    return new_images
    
def resize_images(images : np.ndarray, background_color : str = '#ffffff', add_padding : list[int, int] = [0, 0]) -> np.ndarray :
    ''' 
    Resizes a collection of images to a common size by adding padding.

    Parameters :
    - images (np.ndarray): Array or list of RGB images with potentially different dimensions.
    - background_color (str, optional): Hexadecimal color string used to fill the added padding. The string must start with #. Default is '#ffffff'.
    - add_padding (list[int, int], optional): Additional padding added to the maximum image dimensions to avoid losing information during later alignment transformations. Default is [0, 0].

    Returns :
    - new_images (list[np.ndarray]): List of resized RGB images with identical dimensions after padding.
    '''
    shape0= [i.shape[0] for i in images]
    shape1 = [i.shape[1] for i in images]
    new_shape = [np.max(shape0)+add_padding[0], np.max(shape1)+add_padding[0]]
    new_images = padding(images, background_color, new_shape, mode = 'resize')
    
    return new_images

### Align images

def get_transfo(reference : np.ndarray, to_align : np.ndarray) :
    '''
    Computes the rigid body transformation matrix required to align an image with a reference image, using the pyStackReg library.

    Parameters :
    - reference (np.ndarray): Reference image used as the alignment target.
    - to_align (np.ndarray): Image to be aligned with the reference image.

    Returns :
    - T (np.ndarray): Transformation matrix representing the rigid body alignment between to_align and reference.
    '''

    gray_ref = rgb2gray(reference)
    gray_to_align = rgb2gray(to_align)

    sr = StackReg(StackReg.RIGID_BODY) 
    sr.register(gray_ref, gray_to_align)
    T = sr.get_matrix()

    return T

def aligned(images : list[np.ndarray], ref : str = 'P') -> tuple[list[np.ndarray]] :
    '''
    Aligns a sequence of images using image registration, using the pyStackReg library.

    Parameters :
    - images (list[np.ndarray]): List of RGB images to align.
    - ref (str, optional): Reference strategy used for alignment. 'P' aligns each image with the previous aligned image, while 'F' aligns each image with the first image in the sequence. Default is 'P'.

    Returns :
    - aligned_im (list[np.ndarray]): List of aligned RGB images. The first image is kept unchanged, and subsequent images are transformed according to their computed alignment matrices.
    - T_l (list[np.ndarray]): List of transformation matrices used to align each image with its selected reference image.
    '''
    aligned_im = [images[0]]
    T_l = []
    for i in range(1, len(images)) :

        if ref == 'P' : # previous image
            T = get_transfo(aligned_im[i-1], images[i])
        if ref == 'F' : # first image
             T = get_transfo(aligned_im[0], images[i])

        T_l.append(T)
        aligned_im.append(transform(images[i], T))
    
    return aligned_im, T_l

### Create voxels

def color_clustering(image : np.ndarray, n_clusters : int) -> tuple :
    '''
    Groups the colors of an image into a specified number of clusters using the K-means clustering algorithm.

    Parameters :
    - image (np.ndarray): Image represented as an array of pixel color values. The image is converted to floating-point values before clustering.
    - n_clusters (int): Number of color clusters to compute.

    Returns :
    - labels (list[int]): List of cluster labels assigned to each pixel in the input image.
    - centroids (np.ndarray): Array containing the RGB values of the cluster centroids, represented as 8-bit unsigned integers.   
    '''
    img = image.astype(np.float32, copy=False)
    kmeans = skcl.KMeans(n_clusters=n_clusters)
    kmeans.fit_predict(img)
    labels = list(kmeans.labels_)
    
    centroids = np.clip(kmeans.cluster_centers_, 0, 255).round().astype(np.uint8)

    return labels, centroids

def color_classif(image : np.ndarray, colors : np.ndarray) -> list :
    '''
    Assigns each pixel of an image to the closest reference color.

    Parameters :
    - image (np.ndarray): Image represented as an array of pixel RGB values.
    - colors (np.ndarray): Array of reference RGB colors used for pixel classification.

    Returns :
    - labels (list[int]): List of indices identifying the closest reference color for each pixel in the input image.
    
    '''
    img = image.astype(np.float32)
    refs = colors.astype(np.float32)

    dists = np.sum((img[:, None, :] - refs[None, :, :])**2, axis=2)

    labels = np.argmin(dists, axis=1).tolist()

    return labels

def rgb_to_facecolor(rgbcolor : np.ndarray) -> np.ndarray :
    '''
    Converts an RGB image into a 2D array of hexadecimal color strings.

    Parameters :
    - rgbcolor (np.ndarray): RGB image represented as a 3D array of 8-bit unsigned integer pixel values.

    Returns :
    - facecolor (np.ndarray): 2D array of hexadecimal color strings, starting with #, where each element corresponds to the color of a pixel in the input RGB image.
    '''
    r, g, b = cv2.split(rgbcolor)
    facecolor = np.array([[None for _ in range(r.shape[1])] for _ in range(r.shape[0])])

    for i in range(r.shape[0]) :
        for j in range(r.shape[1]) :
            hexa_str = rgb_to_hexa(r[i][j], g[i][j], b[i][j])
            facecolor[i][j] = hexa_str

    return facecolor

def merg_images(images : list[np.ndarray]) -> np.ndarray :
    '''
    Merges a collection of RGB images into a single array of pixel values.

    Parameters :
    - images (list[np.ndarray]): List of RGB images to merge. Each image is reshaped into a list of RGB pixel values before concatenation.

    Returns :
    - glob_img (np.ndarray): Two-dimensional array containing the RGB values of all pixels from the input images. Each row corresponds to one pixel, and each column corresponds to one color channel (R, G, B).    
    '''
    glob_img = np.concatenate([img.reshape(-1, 3) for img in images], axis=0)
        
    return glob_img

def unmerg_images(glob_img : np.ndarray, nb_images : int, img_shape : tuple[int]) -> list[list, np.ndarray] :
    '''
    Reconstructs a collection of RGB images from a merged array of pixel values.

    Parameters :
    - glob_img (np.ndarray): Two-dimensional array containing the RGB values of all pixels from the merged images.
    - nb_images (int): Number of images to reconstruct from the merged pixel array.
    - img_shape (tuple[int]): Shape of each reconstructed image, typically (height, width, channels).

    Returns :
    - images (list[np.ndarray]): List of reconstructed RGB images with the specified shape.   
    '''
    images = []
    nb_pixels = img_shape[0]*img_shape[1]

    images = [ glob_img[i * nb_pixels:(i + 1) * nb_pixels].reshape(img_shape) for i in range(nb_images)]

    return images

def voxelize_images_fast(images : list[np.ndarray], colors : list[str], background_index : int = 0, path : str = '') -> None :
    '''
    Converts a stack of 2D RGB images into 3D voxel objects by detecting connected components for each color using a 26-neighborhood structure, and saving the resulting voxel arrays.s

    Parameters :
    - images (list[np.ndarray]): List of RGB images representing consecutive 2D slices of a 3D volume.
    - colors (list[str]): List of hexadecimal color strings corresponding to the colors used to identify voxel objects.
    - background_index (int, optional): Index of the background color in the colors list. This color is excluded from object detection. Default is 0.
    - path (str, optional): Directory path used to save the generated facecolor array and voxel object arrays as .npy files. Default is ''.

    Returns :
    - None: This function does not return any value. The generated 3D facecolor array and connected voxel objects are saved as .npy files in the specified path.    
    '''
    facecolor = np.stack([rgb_to_facecolor(img) for img in images], axis=0)
    np.save(path+'facecolor', facecolor)

    colors.pop(background_index)

    # 26-neighborhood
    neighbor = np.ones((3, 3, 3), dtype=int)

    for color in colors:

        col_mask = (facecolor == color)

        # replace HK_algorithm
        labels, nbr_objects = scipy.ndimage.label(col_mask, structure=neighbor)


        for l in range(1, nbr_objects + 1):
            obj = (labels == l)
            np.save(path+color+'_'+str(l), obj)

############## Metrics ##############

def pixel_count(images : list[np.ndarray]) -> dict :
    '''
    Counts the occurrence of each color in a collection of RGB images.

    Parameters :
    - images (list[np.ndarray]): List of RGB images for which pixel color frequencies are computed.

    Returns :
    - counts (dict): Dictionary containing color occurrence information:
    - colors (np.ndarray): Array containing the unique hexadecimal color strings found across all images.
    - total_counts (np.ndarray): Array containing the total number of pixels associated with each color across the entire image set.
    - per_image_counts (list[np.ndarray]): List containing the pixel counts for each color in each individual image. Each element corresponds to one image and follows the same color ordering as colors.    
    '''
    facecolor = np.stack([rgb_to_facecolor(img) for img in images], axis=0)
    colors, total_counts = np.unique(facecolor, return_counts = True)
    counts = {'colors' : colors, 'total_counts' : total_counts, 'per_image_counts' : []}
    for i in range(facecolor.shape[0]) :
        col, t = np.unique(facecolor[i, :, :], return_counts = True)
        t_ext = np.zeros(len(colors), dtype=int)
        indices = np.searchsorted(colors, col)
        t_ext[indices] = t
        counts['per_image_counts'].append(t_ext)
    
    return counts

def color_distribution(counts : dict) -> dict :
    '''
    Computes the color distribution from the pixel counts previously calculated by pixel_count().

    Parameters :
    - counts (dict): Dictionary containing the pixel counts returned by pixel_count(). It must contain:
    - colors (np.ndarray): Array of unique colors found in the images.
    - total_counts (np.ndarray): Array containing the total number of pixels for each color across all images.
    - per_image_counts (list[np.ndarray]): List containing the number of pixels of each color for every individual image.

    Returns :
    - dist (dict): Dictionary containing the color distributions:
    - colors (np.ndarray): Array of unique colors considered in the distributions.
    - global_distribution (dict): Dictionary mapping each color to its proportion over all images combined.
    - per_image_distribution (list[dict]): List of dictionaries, where each dictionary maps colors to their proportion within one individual image.    
    '''
    colors = counts['colors']
    total_counts = counts['total_counts']
    per_image_counts = counts['per_image_counts']

    total_pixels = np.sum(total_counts)

    global_distribution = {color: count / total_pixels for color, count in zip(colors, total_counts)}

    per_image_distribution = []

    for image_counts in per_image_counts:
        image_total = np.sum(image_counts)

        image_distribution = {color: count / image_total for color, count in zip(colors, image_counts) if count > 0}

        per_image_distribution.append(image_distribution)

    dist = {'colors': colors, 'global_distribution': global_distribution, 'per_image_distribution': per_image_distribution}

    return dist

############## Analysis ##############

def volume(voxelobject : np.ndarray, voxel_dim : list[int, int, int] = [1, 1, 1]) -> int :
    '''
    Computes the volume of a voxel object taking into account the volume of a voxel.

    Parameters :
    - voxelobject (np.ndarray): Boolean voxel array representing the object. Voxels with value True are considered part of the object.
    - voxel_dim (list[int, int, int], optional): Physical dimensions of a voxel along the three axes, expressed as [dx, dy, dz]. Default is [1, 1, 1].

    Returns :
    - vol (int): Volume of the voxel object, expressed in cubic units defined by voxel_dim.    
    '''
    vol = (voxelobject == True).sum()
    vol = vol*voxel_dim[0]*voxel_dim[1]*voxel_dim[2]
    return vol

def surface(voxelobject: np.ndarray, voxel_dim : list[int]=(1, 1, 1)) -> float:
    '''
    Computes the surface area of a voxel object taking into account the dimensions of a voxel.

    Parameters :
    - voxelobject (np.ndarray): Boolean voxel array representing the object. Voxels with value True are considered part of the object.
    - voxel_dim (list[int], optional): Physical dimensions of a voxel along the three axes, expressed as (dx, dy, dz). These dimensions are used to compute the area of each exposed face. Default is (1, 1, 1).

    Returns :
        - surface (float): Surface area of the voxel object, expressed in square units defined by voxel_dim.  
    '''
    surface = 0

    for i in range(voxelobject.shape[0]):
        for j in range(voxelobject.shape[1]):
            for k in range(voxelobject.shape[2]):
                if voxelobject[i, j, k]:

                    # Faces perpendicular to X
                    if i+1 >= voxelobject.shape[0] or not voxelobject[i+1, j, k]:
                        surface += voxel_dim[1] * voxel_dim[2]
                    if i-1 < 0 or not voxelobject[i-1, j, k]:
                        surface += voxel_dim[1] * voxel_dim[2]

                    # Faces perpendicular to Y
                    if j+1 >= voxelobject.shape[1] or not voxelobject[i, j+1, k]:
                        surface += voxel_dim[0] * voxel_dim[2]
                    if j-1 < 0 or not voxelobject[i, j-1, k]:
                        surface += voxel_dim[0] * voxel_dim[2]

                    # Faces perpendicular to Z
                    if k+1 >= voxelobject.shape[2] or not voxelobject[i, j, k+1]:
                        surface += voxel_dim[0] * voxel_dim[1]
                    if k-1 < 0 or not voxelobject[i, j, k-1]:
                        surface += voxel_dim[0] * voxel_dim[1]

    return surface

def bounding_box(voxelobject: np.ndarray, voxel_dim : list[int]=[1, 1, 1]):
    '''
    Computes the axis-aligned bounding box of a voxel object.

    Parameters :
    - voxelobject (np.ndarray): Boolean or binary voxel array representing the object. Voxels with a non-zero or True value are considered occupied.
    - voxel_dim (list[int], optional): Physical dimensions of a voxel along the three axes, expressed as [dx, dy, dz]. These values are used to convert voxel indices into physical coordinates. Default is [1, 1, 1].

    Returns :
    - min_corner (np.ndarray): Physical coordinates of the minimum corner of the bounding box, corresponding to the minimum occupied voxel indices.
    - max_corner (np.ndarray): Physical coordinates of the maximum corner of the bounding box, corresponding to the boundary immediately after the maximum occupied voxel.
    - dimensions (np.ndarray): Physical dimensions of the bounding box along the three axes, calculated as max_corner - min_corner.    
    '''
    occupied = np.argwhere(voxelobject)

    min_index = occupied.min(axis=0)
    max_index = occupied.max(axis=0)

    min_corner = min_index * voxel_dim
    max_corner = (max_index + 1) * voxel_dim

    dimensions = max_corner - min_corner

    return min_corner, max_corner, dimensions

############## Plots and images ##############

def plot_voxels(voxelarray : np.ndarray, facecolor : np.ndarray, title : str = '') -> None :  # TODO update doc
    '''
    Displays a 3D voxel object using Matplotlib's voxel visualization. The function renders all occupied voxels with the specified face colors and displays the result in a three-dimensional plot.

    Parameters :
    - voxelarray (np.ndarray): Boolean voxel array representing the object. Voxels with value True are displayed, while False voxels are ignored.
    - facecolor (np.ndarray): Array of hexadecimal color strings specifying the color assigned to each voxel. It must have the same shape as voxelarray.
    - title (str, optional): Title displayed above the figure. Default is ''.

    Returns :
    - None: This function does not return any value. It displays a 3D voxel visualization.
    '''
    fig, ax = plt.subplots(subplot_kw = {"projection" : "3d"})
    ax.voxels(voxelarray, facecolors = facecolor)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    ax.set_aspect('equal')
    plt.show()

def plot_images(images : list[np.ndarray], labels : list[str], rows : int, cols : int, title : str = '', axis1 : str = '', axis2 : str = '') -> None : 
    '''
    Displays a collection of images arranged in a grid of subplots.

    Parameters :
    - images (list[np.ndarray]): List of images or plotting data to display. Images are displayed using imshow(), while plotting data are displayed as bar charts.
    - labels (list[str]): List of titles associated with each subplot.
    - rows (int): Number of rows in the subplot grid.
    - cols (int): Number of columns in the subplot grid.
    - title (str, optional): Title displayed above the figure. Default is ''.
    - axis1 (str, optional): Label for the horizontal axis of each subplot. Default is ''.
    - axis2 (str, optional): Label for the vertical axis of each subplot. Default is ''.

    Returns :
    - None: This function does not return any value. It displays the figure containing the image grid.
    '''
    fig = plt.figure()

    for i in range(rows*cols) :
        ax = fig.add_subplot(rows, cols, i+1)

        if i >= len(images) :
            plt.bar(images[i][1], images[i][0])

        else:
            plt.imshow(images[i])

        plt.title(labels[i])
        ax.set_xlabel(axis1)
        ax.set_ylabel(axis2)
    fig.suptitle(title)
    fig.tight_layout()
    plt.show()

def save_slices(images : list[np.ndarray], path : str, name : str) -> None :
    '''
    Saves a collection of images as PNG files in a specified directory.

    Parameters :
    - images (list[np.ndarray]): List of images to save.
    - path (str): Directory path where the image files will be saved.
    - name (str): Base name used to generate the output filenames. Images are saved using the format name_index.png.

    Returns :
    - None: This function does not return any value. It saves the images as PNG files in the specified directory.    
    '''
    for i in range(len(images)) :
        imsave(path+name+'_'+str(i)+'.png', images[i])

def load_slices(filename : str, n : int, start : int = 0, format : str = 'png') -> list[np.ndarray] :
    '''
    Loads a sequence of image slices from disk and returns them as RGB images.

    Parameters :
    - filename (str): Base filename of the image sequence. Images are expected to follow the naming format filename_index.format.
    - n (int): Number of images to load.
    - start (int, optional): Starting index of the image sequence. Default is 0.
    - format (str, optional): File format extension of the images to load. Default is 'png'.

    Returns :
    - images (list[np.ndarray]): List of loaded RGB images.    
    '''
    images = []

    for i in range(start, n+start) :
        img = cv2.imread(filename+'_'+str(i)+'.'+format)
        b, g, r = cv2.split(img)
        rgb_img = cv2.merge([r, g, b])
        images.append(rgb_img)

    return images

def plot_clusters(data, labels, centroids, title : str = '') -> None :
    '''
    Displays the result of a clustering algorithm as a 2D scatter plot.

    Parameters :
    - data (np.ndarray): Two-dimensional array containing the coordinates of the data points to display. Each row corresponds to one observation, and the two columns represent its coordinates.
    - labels (np.ndarray | list[int]): Cluster label assigned to each data point. The number of labels must match the number of rows in data.
     - centroids (np.ndarray): Two-dimensional array containing the coordinates of the cluster centroids. Each row corresponds to the centroid of one cluster.
    - title (str, optional): Title displayed above the figure. Default is ''.

    Returns :
    - None: This function does not return any value. It displays a scatter plot of the clustered data and their corresponding centroids.    
    '''
    fig = plt.figure()
    u_labels = np.unique(labels)

    for i in u_labels:
        plt.scatter(data[labels == i , 0] , data[labels == i , 1] , label = i)

    plt.scatter(centroids[:,0] , centroids[:,1] , s = 80, color = 'k')
    plt.legend()
    fig.suptitle(title)
    fig.tight_layout()
    plt.show()   

def save_voxel_to_vtk(voxels: np.ndarray, filename: str, voxel_dim : list[float, float, float] = [1.0, 1.0, 1.0]) -> None:
    '''
    Saves a 3D voxel array as a VTK image data file (.vtk) that can be visualized and processed using software such as ParaView.

    Parameters :
    - voxels (np.ndarray): 3D boolean or binary voxel array representing the object. Occupied voxels should have a value of True or 1, while empty voxels should have a value of False or 0.
    - filename (str): Path and filename of the output VTK file.
    - voxel_dim (list[float, float, float], optional): Physical dimensions of each voxel along the three axes, expressed as [dx, dy, dz]. These values define the spacing between voxels in the generated VTK file. Default is [1.0, 1.0, 1.0].

    Returns :
    - None: This function does not return any value. It creates a VTK file containing the voxel data at the specified location.
        
    '''
    image = vtk.vtkImageData()
    image.SetDimensions(voxels.shape[0] + 1, voxels.shape[1] + 1, voxels.shape[2] + 1)
    image.SetSpacing(voxel_dim[0], voxel_dim[1], voxel_dim[2])
    image.SetOrigin(0.0, 0.0, 0.0)

    flat_data = voxels.astype(np.uint8).ravel(order='F')
    vtk_array = numpy_support.numpy_to_vtk(flat_data, deep=True,array_type=vtk.VTK_UNSIGNED_CHAR)
    vtk_array.SetName('mask')

    image.GetCellData().SetScalars(vtk_array)

    writer = vtk.vtkStructuredPointsWriter()
    writer.SetFileName(filename)
    writer.SetInputData(image)
    writer.Write()