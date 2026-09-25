import functions as func
import numpy as np
import random 

### Script to generate the images in 'slices/' ###

## CLOT COLORS ##
# ['#c78637', '#ba6e2e', '#e3bb37', '#e65a49', '#f08a8c', '#e88d76']

###### 1 Cuboid #################
def cuboid_slices() :
    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc cube")
    cube_aligned = func.rectangular_cuboid_vox([100, 100, 100], [200, 175, 90], x, y, z)
    axis = np.array([random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)])
    #cube_rand_axis = func.rectangular_cuboid_vox([100, 100, 100], [70, 95, 90], x, y, z, axis = axis)
    print("cube OK\n")

    print("calc facecol")
    colors = ['#e65a49']
    facecolor_aligned = func.color_objects(cube_aligned, [], colors)
    #facecolor_rand_axis = func.color_objects(cube_rand_axis, [], colors)
    print("facecol OK\n")

    print("creating images")
    images_z = func.slice(facecolor_aligned, axis='z')
    func.save_slices(images_z, 'slices/1_cuboid/cube_z/', '0_img_init')
    print("images z OK")
    #images_rand_axis = func.slice(facecolor_rand_axis, axis='z')
    #func.save_slices(images_rand_axis, 'slices/1_cuboid/cube_rand_axis/', '0_img_init')
    print("images rand axis OK")

###### 2 Filled Cuboid ###########
def filled_cuboid_slices() :
    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc cube")
    cube = func.rectangular_cuboid_vox([100, 100, 100], [198, 195, 195], x, y, z)
    print("cube OK\n")

    print("calc inside")
    c1 = func.rectangular_cuboid_vox([100, 75, 80], [60, 60, 60], x, y ,z)
    print("cube 1 OK")
    c2 = func.rectangular_cuboid_vox([80, 75, 50], [30, 40, 20], x, y ,z)
    print("cube 2 OK")
    t = func.torus_vox([120, 160, 100], 25, 10, x, y, z, axis =[1, 0, 0])
    print("torus OK")
    print("calc inside OK\n")

    print("calc facecol")
    objects = [c1, c2, t]
    colors = ['#e3bb37', '#e65a49',  '#f08a8c', '#f08a8c']
    facecolor_1 = func.color_objects(cube, objects, colors)
    #facecolor_2 = func.color_objects(cube, objects, colors, with_intersections=True)
    print("facecol OK\n")

    print("creating images")
    images_1 = func.slice(facecolor_1, axis='z')
    #images_2 = func.slice(facecolor_2, axis='z')
    func.save_slices(images_1, 'slices/2_filled_cuboid/f_cub_z/', '0_img_init')
    #func.save_slices(images_2, 'slices/2_filled_cuboid/f_cub_intersect_z/', '0_img_init')
    print("images z OK")
    images_1 = func.slice(facecolor_1, axis='x')
    #images_2 = func.slice(facecolor_2, axis='x')
    func.save_slices(images_1, 'slices/2_filled_cuboid/f_cub_x/', '0_img_init')
    #func.save_slices(images_2, 'slices/2_filled_cuboid/f_cub_intersect_x/', '0_img_init')
    print("images x OK")

###### 3 Cylinder ################
def cylinder_slices() :
    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc cyl")
    cyl_aligned = func.cylinder_vox([90, 90, 100], 80, 200, x, y, z)
    axis = np.array([random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)])
    cyl_rand_axis = func.cylinder_vox([90, 90, 100], 60, 100, x, y, z, axis=axis)
    print("cyl OK\n")

    print("calc facecol")
    colors = ['#e65a49']
    facecolor_aligned = func.color_objects(cyl_aligned, [], colors)
    facecolor_rand_axis = func.color_objects(cyl_rand_axis, [], colors)
    print("facecol OK\n")

    print("creating images")
    images_z = func.slice(facecolor_aligned, axis='z')
    func.save_slices(images_z, 'slices/3_cylinder/cyl_z/', '0_img_init')
    print("images z OK")
    images_x = func.slice(facecolor_aligned, axis='x')
    func.save_slices(images_x, 'slices/3_cylinder/cyl_x/', '0_img_init')
    print("images x OK")
    images_rand_axis = func.slice(facecolor_rand_axis, axis='z')
    func.save_slices(images_rand_axis, 'slices/3_cylinder/cyl_rand_axis/', '0_img_init')
    print("images rand_axis OK")

###### 4 Filled Cylinder ###########
def filled_cylinder_slices() :
    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc cyl")
    c1_vox = func.cylinder_vox([100, 100, 100], 98, 200, x, y, z)
    print("cyl OK\n")

    print("calc inside")
    c2_vox = func.cylinder_vox([60, 120, 60], 40, 20, x, y, z, axis = [1, 0, 0])
    print("cyl1 OK")
    s_vox = func.sphere_vox([120, 100, 100], 40, x, y, z)
    print("s OK")
    t1_vox = func.torus_vox([140, 120, 120], 20, 10, x, y, z)
    print("tor1 OK")
    t2_vox = func.torus_vox([80, 40, 120], 30, 20, x, y, z, axis = [0, 1, 0])
    print("tor2 OK")
    print("inside OK\n")

    print("calc facecol")
    objects = [c2_vox, s_vox, t1_vox, t2_vox]
    colors = ['#e3bb37', '#e65a49', '#c78637', '#f08a8c', '#e88d76']
    facecolor_1 = func.color_objects(c1_vox, objects, colors)
    #facecolor_2 = func.color_objects(c1_vox, objects, colors, with_intersections=True)
    print("facecol OK\n")

    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc cyl")
    axis = [10, 16, 3]
    c1_vox = func.cylinder_vox([100, 100, 100], 85, 100, x, y, z, axis = axis)
    print("cyl OK\n")

    print("calc inside")
    c2_vox = func.cylinder_vox([60, 120, 80], 40, 20, x, y, z, axis = [1, 0, 0])
    print("cyl1 OK")
    s_vox = func.sphere_vox([120, 95, 100], 40, x, y, z)
    print("s OK")
    t1_vox = func.torus_vox([110, 80, 120], 20, 10, x, y, z)
    print("tor1 OK")

    print("inside OK\n")

    print("calc facecol")
    objects = [c2_vox, s_vox, t1_vox ]
    colors = ['#e3bb37', '#e65a49', '#c78637', '#f08a8c']
    facecolor_axis_unal = func.color_objects(c1_vox, objects, colors)

    print("creating images")
    images_1 = func.slice(facecolor_1, axis='z')
    #images_2 = func.slice(facecolor_2, axis='z')
    func.save_slices(images_1, 'slices/4_filled_cylinder/f_cyl_z/', '0_img_init')
    #func.save_slices(images_2, 'slices/4_filled_cylinder/f_cyl_intersect_z/', '0_img_init')
    print("images z OK")
    images_1 = func.slice(facecolor_1, axis='x')
    #images_2 = func.slice(facecolor_2, axis='x')
    func.save_slices(images_1, 'slices/4_filled_cylinder/f_cyl_x/', '0_img_init')
    #func.save_slices(images_2, 'slices/4_filled_cylinder/f_cyl_intersect_x/', '0_img_init')
    print("images x OK")
    images_axis_unal = func.slice(facecolor_axis_unal, axis='z')
    func.save_slices(images_axis_unal, 'slices/4_filled_cylinder/f_cyl_axis_unal/', '0_img_init')
    print("images x OK")

###### 5 Torus ################
def torus_slices() :
    print("calc x y z")
    x, y, z = np.indices((200, 200, 200))
    print("x y z OK\n")

    print("calc torus")
    torus_aligned = func.torus_vox([100, 100, 100], 55, 20, x, y, z)
    axis = np.array([random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)])
    torus_rand_axis = func.torus_vox([100, 100, 100], 40, 15, x, y, z, axis=axis)
    print("torus OK\n")

    print("calc facecol")
    colors = ['#e65a49']
    facecolor_aligned = func.color_objects(torus_aligned, [], colors)
    facecolor_rand_axis = func.color_objects(torus_rand_axis, [], colors)
    print("facecol OK\n")

    print("creating images")
    images_z = func.slice(facecolor_aligned, axis='z')
    func.save_slices(images_z, 'slices/5_torus/torus_z/', '0_img_init')
    print("images z OK")
    images_x = func.slice(facecolor_aligned, axis='x')
    func.save_slices(images_x, 'slices/5_torus/torus_x/', '0_img_init')
    print("images x OK")
    images_rand_axis = func.slice(facecolor_rand_axis, axis='z')
    #func.save_slices(images_rand_axis, 'slices/5_torus/torus_rand_axis/', '0_img_init')
    print("images rand axis OK")

###### MAIN ###################

#cuboid_slices()
#filled_cuboid_slices()
#cylinder_slices()
#filled_cylinder_slices()
#torus_slices()
