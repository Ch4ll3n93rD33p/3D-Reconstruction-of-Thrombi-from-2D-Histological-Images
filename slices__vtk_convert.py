import numpy as np
import functions as func
import openpyxl

### METRICS AND COMPARISON TO ORIGINAL
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

#directories[i] = directories[i][:-1]+'_2/'
#color_mode = 'clust' # color clustering
color_mode = 'class' # color classification

if color_mode == 'clust' :
    directories[i] = directories[i]+'Col_clust/'
elif color_mode == 'class' :
    directories[i] = directories[i]+'Col_class/'

in_dir = func.os.listdir('slices/'+directories[i])
filenames = list(filter(lambda f: ('.npy' in f) and ('#' in f), in_dir))


for f in filenames :
    print(f)
    object = np.load('slices/'+directories[i]+f, allow_pickle = True)
    func.save_voxel_to_vtk(object, 'slices/'+directories[i]+f[:-4]+'.vtk')