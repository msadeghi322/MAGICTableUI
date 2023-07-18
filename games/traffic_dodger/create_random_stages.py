
import random
import xlwt
import numpy as np

workbook = xlwt.Workbook() 
sheet = workbook.add_sheet("Sheet Name") 


nrows = 120
ncols = 8 #40
num_cars_excess = 120 #250  # 200 is the goal
num_cars_goal = 80

num_rocks_excess = 100#200
num_rocks_goal = 40 # 100


car_row_list = []
rock_row_list = []
xy_pairs = [] # a set of pairs for (x, y) 

##### CAR #######
current_cars = 0
##while current_cars < num_cars_excess:
##    x = random.randint(0,nrows-1)
##    y = random.randint(0,ncols-1)
##    xy_pairs.append((x, y))

##    current_cars = current_cars + 1
while current_cars < num_cars_goal:
    x = random.randint(0,nrows-1)
    y = random.randint(0,ncols-1)
    if (x, y) not in xy_pairs:
        xy_pairs.append((x, y))
        current_cars = current_cars + 1


print len(xy_pairs)
##
##_, idx = np.unique(xy_pairs, axis=0, return_index=True)
##xy_pairs_re = [xy_pairs[x] for x in np.sort(idx)]
##reduced_xy_pairs = xy_pairs_re[:num_cars_goal]


##### ROCK #######
current_rocks = 0
xy_rock_pairs = []
while current_rocks < num_rocks_goal:
    x = random.randint(0,nrows-1)
    y = random.randint(0,ncols-1)
    if (x, y) not in (xy_pairs or xy_rock_pairs):
        xy_rock_pairs.append((x, y))
        current_rocks = current_rocks + 1
        
print len(xy_rock_pairs)

## writing to spread sheet
for num in range(num_cars_goal):
    sheet.write(xy_pairs[num][0], xy_pairs[num][1], 1)

for num in range(num_rocks_goal):
    sheet.write(xy_rock_pairs[num][0], xy_rock_pairs[num][1], 2)


## spreat sheet column width control
for col in range(ncols):
    sheet.col(col).width = 256*3 # 256: width of '0' character


##
##for row in range(nrows):
##    for col in range(ncols):
##        value = 1
##        sheet.write(row, col, value)
##        sheet.col(col).width = 256*3 # 256: width of '0' character

workbook.save("random_stage.xls")
