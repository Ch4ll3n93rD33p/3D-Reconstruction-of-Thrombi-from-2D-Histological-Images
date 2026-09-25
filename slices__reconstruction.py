import numpy as np
import functions as func
import cv2
import time
import openpyxl

### Script to reconstruct objects from the images in 'slices' ###

directories = ['1_cuboid/cube_rand_axis/', '1_cuboid/cube_z/', '2_filled_cuboid/f_cub_x/', '2_filled_cuboid/f_cub_z/', '3_cylinder/cyl_rand_axis/', '3_cylinder/cyl_x/', '3_cylinder/cyl_z/', '4_filled_cylinder/f_cyl_axis_unal/', '4_filled_cylinder/f_cyl_x/', '4_filled_cylinder/f_cyl_z/', '5_torus/torus_rand_axis/', '5_torus/torus_x/', '5_torus/torus_z/', '6_clot_1/', '7_clot_2/', '7_clot_2_pt1/', '7_clot_2_pt2/', '7_clot_2_pt3/', '8_clot_glob/', '9_mini_clot/']
nbr_images = [141, 200, 195, 198, 157, 161, 200, 183, 197, 200, 95, 149, 39, 33, 33, 33, 33, 33, 33, 33]
masks_paths = ['slices/6_clot_1/masks/', 'slices/7_clot_2/masks/', 'slices/7_clot_2_pt1/masks/', 'slices/7_clot_2_pt2/masks/', 'slices/7_clot_2_pt3/masks/', 'slices/8_clot_glob/masks/', 'slices/9_mini_clot/masks/']
masks_names = ['Crop_1', 'Crop_2', 'Crop_2', 'Crop_2', 'Crop_2', '2019_5 MSB', '0_miniclot']
ref_colors = [['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e3bb37', '#e65a49',  '#f08a8c', '#ffffff'], ['#e3bb37', '#e65a49',  '#f08a8c', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#e88d76', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#e88d76', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'],  ['#e65a49', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff'], ['#d76c3a', '#f58b83', '#f6b354', '#fabeb3', '#ffffff']]
nbr_cluster = [2, 2, 4, 4, 2, 2, 2, 5, 6, 6, 2, 2, 2, 5, 5, 5, 5, 5, 5, 5]
i = 4 # index of the targeted dir in directories (between 0 and 19)
# 0-1 : cuboid
# 2-3 : filled cuboid
# 4-6 : cylinder
# 7-9 : filled cylinder
# 10-12 : torus
# 13-19 : clots

#color_mode = 'clust' # color clustering
color_mode = 'class' # color classification


#color_mode = 'd_clust' # double color clustering

merging_col = False # only for classif

#directories[i]= directories[i][:-1]+'_2/'

'''## Loading images
print("loading images")

if 0 <= i < 13 :
    name = '0_3_img_crop'
    images = func.load_slices('slices/'+directories[i]+name, nbr_images[i])

elif 13<= i < 18:
    names = ['Crop_1', 'Crop_2', 'Crop_2', 'Crop_2', 'Crop_2', '2019_5 MSB'] 
    name = names[i-13]
    images = func.load_slices('slices/'+directories[i]+name, nbr_images[i], start = 1, format = 'tif')

else :
    print(directories[i])
    name = '0_miniclot'
    images = func.load_slices('slices/'+directories[i]+name, nbr_images[i], start = 1)

print("loading images OK\n")

## 1 Resizing images (+ restoration for clots )
print("resizing and restoration")

if i >= 13 : # image restoration
    #images = func.image_restoration(images, masks_paths[i-14], masks_names[i-14], start = 1)
    images = func.image_restoration(images, masks_paths[i-13], masks_names[i-13], start = 1)
    func.save_slices(images, 'slices/'+directories[i], '1_img_restored')
    print("restoration OK")

background_color = '#ffffff'
if i >= 13 : # pads the clot images to avoid to cut the clot during realignement
    images = func.resize_images(images, background_color = background_color, add_padding=[20,20])
else : 
    images = func.resize_images(images, background_color = background_color)

func.save_slices(images, 'slices/'+directories[i], '1_img_resize')
print("resizing OK\n")

# down_size for 7_clot_2_pt1 and 7_clot_2_pt3
if i == 15 or i == 17 :
    print('downsizing')
    new_size = (images[0].shape[1]//2,images[0].shape[0]//2) # invert the two parameters for the right shape in the end
    images = [cv2.resize(images[j], new_size, interpolation=cv2.INTER_AREA) for j in range(len(images))]
    func.save_slices(images, 'slices/'+directories[i], '1_img_downsize')

    print('downsizing OK\n')

## 2 Color clustering / classification
if color_mode == 'clust' :
    print("color clust")

    img_shape = images[0].shape
    glob_img = func.merg_images(images)
    labels, centroids = func.color_clustering(glob_img, nbr_cluster[i])
    new_glob_img = centroids[labels]
    images = func.unmerg_images(new_glob_img, nbr_images[i], img_shape)

    directories[i] = directories[i]+'Col_clust/'
    func.save_slices(images, 'slices/'+directories[i], '2_img_col_clust')
    
    print("color clust OK\n")

elif color_mode == 'class' :
    print('color classif')

    img_shape = images[0].shape
    glob_img = func.merg_images(images)
    ref = np.array([func.hexa_to_rgb(c) for c in ref_colors[i]])
    labels = func.color_classif(glob_img, ref)

    if merging_col :
        labels_remap = [0, 3, 2, 3, 4]
        col = ref[labels_remap].astype(np.uint8)
        new_glob_img = col[labels]
    else :
        new_glob_img = ref[labels].astype(np.uint8)
    images = func.unmerg_images(new_glob_img, nbr_images[i], img_shape)

    directories[i] = directories[i]+'Col_class/'
    func.save_slices(images, 'slices/'+directories[i], '2_img_col_class')

    print('color classif OK\n')'''

'''
elif color_mode == 'd_clust' :
    print("double color clust")

    img_shape = images[0].shape
    new_images = []
    for im in images :
        g_im = func.merg_images([im])
        l, c = func.color_clustering(g_im, nbr_cluster[i])
        n_g_im = c[l]
        n_im = func.unmerg_images(n_g_im, 1, img_shape)
        new_images = new_images+n_im

    glob_img = func.merg_images(new_images)
    labels, centroids = func.color_clustering(glob_img, nbr_cluster[i])
    new_glob_img = centroids[labels]
    images = func.unmerg_images(new_glob_img, nbr_images[i], img_shape)

    func.save_slices(images, 'slices/'+directories[i], '2_img_d_col_clust')
    directories[i] = directories[i]+'D_col_clust/'
    print("double color clust OK\n")
'''

'''## 3 Alignement
print("alignement")

images, _ = func.aligned(images)


func.save_slices(images, 'slices/'+directories[i], '3_img_aligned')
print("alignement OK\n")'''


'''## 4 Color correction
print("color correct")

if color_mode == 'clust' : #or color_mode == 'd_clust':
    colors = [func.rgb_to_hexa(c[0], c[1], c[2]) for c in centroids]

elif color_mode == 'class' :
    if merging_col :
        colors = [func.rgb_to_hexa(c[0], c[1], c[2]) for c in col]
    else : 
        colors = ref_colors[i]
        
images = func.correct_colors(images, colors)


func.save_slices(images, 'slices/'+directories[i], '4_img_col_correct')
print("color correct OK\n")
'''

'''## 4 Color classification
print("color classif")
if color_mode == 'clust' : #or color_mode == 'd_clust':
    colors = ref = np.array(centroids)

elif color_mode == 'class' :
    if merging_col :
        ref = np.array(col)
    else : 
        ref = np.array([func.hexa_to_rgb(c) for c in ref_colors[i]])


#name = '3_img_aligned'
#images = func.load_slices('slices/'+directories[i]+name, nbr_images[i])

img_shape = images[0].shape
glob_img = func.merg_images(images)
labels = func.color_classif(glob_img, ref)
new_glob_img = ref[labels].astype(np.uint8)
images = func.unmerg_images(new_glob_img, nbr_images[i], img_shape)

func.save_slices(images, 'slices/'+directories[i], '4_img_col_classif')
print("color classif OK\n")'''


print("loading images")
if color_mode == 'clust' :
    directories[i] = directories[i]+'Col_clust/'

elif color_mode == 'class' :
    directories[i] = directories[i]+'Col_class/'

name = '4_img_col_classif'
images = func.load_slices('slices/'+directories[i]+name, nbr_images[i])

print("loading images OK\n")
if merging_col : 
    labels_remap = [0, 3, 2, 3, 4]
    r = np.array([func.hexa_to_rgb(c) for c in ref_colors[i]])
    ref_ = r[labels_remap].astype(np.uint8)
    ref = [func.rgb_to_hexa(c[0], c[1], c[2]) for c in ref_]
    ref.pop(3)

else :
    ref = ref_colors[i]

print(ref)

#ref.pop(0)
#ref.pop(0)

## Voxelize 
print("voxelize")

start = time.time()
func.voxelize_images_fast(images, ref, background_index = -1, path = 'slices/'+directories[i])
end = time.time()
print("durée : ", end-start)

print("voxelize OK\n")
