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
i = 7 # index of the targeted dir in directories (between 0 and 19)
# 0-1 : cuboid
# 2-3 : filled cuboid
# 4-6 : cylinder
# 7-9 : filled cylinder
# 10-12 : torus
# 13-19 : clots

#color_mode = 'clust' # color clustering
color_mode = 'class' # color classification

excel_file_exists = False

column_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

if i <= 12 :
    idx = [j for j in range(len(directories[i])) if directories[i].startswith('/', j)]
    excel_file = 'slices/'+directories[i][0]+'_'+directories[i][idx[-2]+1:idx[-1]]+'_metrics'
    voxel_dim = [1, 1, 1]
else :
    excel_file = 'slices/'+directories[i][:-1]+'_metrics'
    if i == 15 or i == 17 : # for down sized images
        voxel_dim = [3.546, 3.546, 5] # dim of each voxel in micrometers (for slice thickness of 5 micrometers)
    else :
        voxel_dim = [1.773, 1.773, 5] # dim of each voxel in micrometers (for slice thickness of 5 micrometers)

if excel_file_exists :
    excel_wb = openpyxl.load_workbook(filename=excel_file+'.xlsx')
    sheet = excel_wb.active
else :
    excel_wb =openpyxl.Workbook()
    sheet = excel_wb.active
    excel_wb.save(excel_file+'.xlsx')

if color_mode == 'clust' :
    directories[i] = directories[i]+'Col_clust/'
elif color_mode == 'class' :
    directories[i] = directories[i]+'Col_class/'


in_dir = func.os.listdir('slices/'+directories[i])
filenames = list(filter(lambda f: ('.npy' in f) and ('#' in f), in_dir))

colors = list(set([f[:7] for f in filenames]))

nbr_objects = [len(list(filter(lambda y: c in y, filenames))) for c in colors]

'''idx = colors.index('#f6b354')
colors.pop(idx)
nbr_objects.pop(idx)
idx = colors.index('#fabeb3')
colors.pop(idx)
nbr_objects.pop(idx)
print(colors)'''

start_r = 3
end_r = start_r+max(nbr_objects)-1
start_c = 3 

# filename
s = sheet.cell(row = start_r -1, column = 1)
s.value = directories[i][:-1]
sheet.merge_cells(start_row=start_r-1, start_column= 1, end_row=end_r+2, end_column=1)

# objects number
im = sheet.cell(row = 1, column = 2)
im.value = 'object'
sheet.merge_cells(start_row=1, start_column= 2, end_row=2, end_column=2)
for r in range(start_r, end_r+1) :
    c = sheet.cell(row = r, column = 2)
    c. value = r-start_r+1
c = sheet.cell(row = end_r+1, column = 2)
c.value = 'Total'
c = sheet.cell(row = end_r+2, column = 2)
c.value = 'Mean'

for j in range(len(colors)) :

    c = sheet.cell(row = 1, column = start_c)
    c.value = colors[j]
    sheet.merge_cells(start_row=1, start_column= start_c, end_row=1, end_column=start_c+7)
    code = colors[j][1:].upper()
    c.fill = openpyxl.styles.PatternFill(start_color = code, fill_type = "solid")

    c = sheet.cell(row = 2, column = start_c)
    c.value = 'Volume'
    c = sheet.cell(row = 2, column = start_c+1)
    c.value = 'Surface'
    c = sheet.cell(row = 2, column = start_c+2)
    c.value = 'SA/V'
    c = sheet.cell(row = 2, column = start_c+3)
    c.value = 'Bounding box dimensions'
    c = sheet.cell(row = 2, column = start_c+6)
    c.value = 'Bounding box volume'
    c = sheet.cell(row = 2, column = start_c+7)
    c.value = 'Vol. object/Vol. b. box'

    for k in range(nbr_objects[j]) :
        print('slices/'+directories[i]+colors[j]+'_'+str(k+1)+'.npy')
        object = np.load('slices/'+directories[i]+colors[j]+'_'+str(k+1)+'.npy', allow_pickle = True)
        v = func.volume(object, voxel_dim)
        s = func.surface(object, voxel_dim)
        _, _, bbox_dim = func.bounding_box(object, voxel_dim)
        bbox_v = bbox_dim[0]*bbox_dim[1]*bbox_dim[2]

        c = sheet.cell(row = start_r+k, column = start_c)
        c.value = v
        c = sheet.cell(row = start_r+k, column = start_c+1)
        c.value = s
        c = sheet.cell(row = start_r+k, column = start_c+2)
        c.value = s/v
        c = sheet.cell(row = 2, column = start_c+3)
        c.value = bbox_dim[0]
        c = sheet.cell(row = 2, column = start_c+4)
        c.value = bbox_dim[1]
        c = sheet.cell(row = 2, column = start_c+5)
        c.value = bbox_dim[2]
        c = sheet.cell(row = 2, column = start_c+6)
        c.value = bbox_v
        c = sheet.cell(row = 2, column = start_c+7)
        c.value = v/bbox_v
        excel_wb.save(excel_file+'.xlsx')

    for k in range(nbr_objects[j], end_r-start_r+1) :
        c = sheet.cell(row = start_r+k, column = start_c)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+1)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+2)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+3)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+4)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+5)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+6)
        c.value = 0
        c = sheet.cell(row = start_r+k, column = start_c+7)
        c.value = 0
        excel_wb.save(excel_file+'.xlsx')
    
    # total
    c = sheet.cell(row = end_r+1, column = start_c)
    c.value = '= SUM('+column_letters[start_c-1]+str(start_r)+':'+column_letters[start_c-1]+str(end_r)+')'
    c = sheet.cell(row = end_r+1, column = start_c+1)
    c.value = '= SUM('+column_letters[start_c]+str(start_r)+':'+column_letters[start_c]+str(end_r)+')'
    c = sheet.cell(row = end_r+1, column = start_c+2)
    c.value = '= '+column_letters[start_c-1]+str(end_r+1)+'-'+column_letters[start_c]+str(end_r+1)
    
    # mean
    c = sheet.cell(row = end_r+2, column = start_c)
    c.value = '= MEAN('+column_letters[start_c-1]+str(start_r)+':'+column_letters[start_c-1]+str(end_r)+')'
    c = sheet.cell(row = end_r+2, column = start_c+1)
    c.value = '= MEAN('+column_letters[start_c]+str(start_r)+':'+column_letters[start_c]+str(end_r)+')'
    c = sheet.cell(row = end_r+2, column = start_c+2)
    c.value = '= MEAN('+column_letters[start_c+1]+str(start_r)+':'+column_letters[start_c+1]+str(end_r)+')'
    

    excel_wb.save(excel_file+'.xlsx')
    start_c += 8
