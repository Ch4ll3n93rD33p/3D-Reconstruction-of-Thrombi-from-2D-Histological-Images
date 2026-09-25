import numpy as np
import functions as func

### Script to unaligne and crop the exemples in 'slices' ###

directories = ['1_cuboid/cube_rand_axis/', '1_cuboid/cube_z/', '2_filled_cuboid/f_cub_x/', '2_filled_cuboid/f_cub_z/', '3_cylinder/cyl_rand_axis/', '3_cylinder/cyl_x/', '3_cylinder/cyl_z/', '4_filled_cylinder/f_cyl_axis_unal/', '4_filled_cylinder/f_cyl_x/', '4_filled_cylinder/f_cyl_z/', '5_torus/torus_rand_axis/', '5_torus/torus_x/', '5_torus/torus_z/']
nbr_images = 200
new_nbr_images = [141, 200, 195, 198, 157, 161, 200, 183, 197, 200, 95, 149, 39]
ref_colors = [['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e3bb37', '#e65a49',  '#f08a8c', '#ffffff'], ['#e3bb37', '#e65a49',  '#f08a8c', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#e88d76', '#ffffff'], ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#e88d76', '#ffffff'], ['#e65a49', '#ffffff'], ['#e65a49', '#ffffff'],  ['#e65a49', '#ffffff']]
i = 4 # index of the targeted dir in directories (between 0 and 12)
# 0-1 : cuboid
# 2-3 : filled cuboid
# 4-6 : cylinder
# 7-9 : filled cylinder
# 10-12 : torus


#directories[i] = directories[i][:-1]+'_2/'
print(ref_colors[i])
name = '0_img_init'

col_corr = True # color correction step

images = func.load_slices('slices/'+directories[i]+name, nbr_images)

# removing empty images
empty_images = nbr_images-new_nbr_images[i]

if empty_images != 0 :
    
    if i == 5 : # cylinder not centered along x axis
        a = 10
        b = 29

    elif i == 11 :# torus not centered along x axis
        a = 21
        b = 30

    else :
        b = empty_images//2
        a = empty_images-b

    images = images[a:-b]

'''if col_corr :
    # get colors for the color correction step
    colors = []
    for img in images :
        f = func.rgb_to_facecolor(img)
        colors = colors + list(np.unique(f))

    colors = list(np.unique(colors))'''

## Unaligne images
print("unalignement")

max_r = np.pi/48
max_t = 10.0
#max_r = np.pi/96
#max_t = 3.0
first = images.pop(0)
[first] = func.padding([first])
images = func.unaligne_images(images, max_r, max_t)
images = [first]+images

func.save_slices(images, 'slices/'+directories[i], '0_1_img_unal')
print("unalignement OK\n")

## Color correction (opt)
if col_corr :
    print("color correction")

    img_shape = images[0].shape
    ref = np.array([func.hexa_to_rgb(c) for c in ref_colors[i]])
    glob_img = func.merg_images(images)
    labels = func.color_classif(glob_img, ref)
    new_glob_img = ref[labels].astype(np.uint8)
    images = func.unmerg_images(new_glob_img, new_nbr_images[i], img_shape)

    func.save_slices(images, 'slices/'+directories[i], '0_2_img_col_classif')
    print("color correction OK\n")

## Crop images 
print("croping")

max_c = [20,30]
images = func.crop_images(images, max_c, sym = False)

func.save_slices(images, 'slices/'+directories[i], '0_3_img_crop')
print("croping OK\n")