# plots for r01grant AIM3
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import glob
import os
import numpy as np
import pandas as pd
from ast import literal_eval


baseDir = '/Users/wonjoonsohn/Documents/workspace_python/MAGicTableGame/games/traffic_dodger/Output/AIM3_DATA' # FIX:CROSS PLATFORM


SUBJ1_S= glob.glob(baseDir+  '/*CM_s*')
SUBJ1_D = glob.glob(baseDir+  '/*CM_d*')

SUBJ2_S = glob.glob(baseDir+  '/*IZ_s*')
SUBJ2_D = glob.glob(baseDir+  '/*IZ_d*')

SUBJ3_S = glob.glob(baseDir+  '/*KC_s*')
SUBJ3_D = glob.glob(baseDir+  '/*KC_d*')

SUBJ4_S = glob.glob(baseDir+  '/*SP_s*')
SUBJ4_D = glob.glob(baseDir+  '/*SP_d*')

SUBJ5_S = glob.glob(baseDir+  '/*SB_s*')
SUBJ5_D = glob.glob(baseDir+  '/*SB_d*')

SUBJ6_S = glob.glob(baseDir+  '/*WJ_s*')
SUBJ6_D = glob.glob(baseDir+  '/*WJ_d*')

game_result_files_s= [SUBJ1_S, SUBJ2_S, SUBJ3_S, SUBJ4_S, SUBJ5_S, SUBJ6_S]
game_result_files_d = [SUBJ1_D, SUBJ2_D, SUBJ3_D, SUBJ4_D, SUBJ5_D, SUBJ6_D]

#### plot basic
nrows = 1
fig, axes = plt.subplots(nrows, 1)
fig.subplots_adjust(hspace = .5, wspace=.2)
window_title ='Barplot'
fig.canvas.set_window_title(window_title)


## loading csv
#print "file name:", game_result_files_s
#print "file name:", game_result_files_s[0]
#df= pd.read_csv(game_result_files[0])
### literal eval:  df.carX_at_bottom_list.apply(literal_eval)[0][0]
#nrows= len(df.carX_in_row_list)-1


###################################
## 1. Scores vs trials (s1-s4, d1-d4)
###################################

meanList_s = []
stdList_s =[]
meanList_d = []
stdList_d =[]
scoreList_s = []
scoreList_d =[]
trial = [1, 2, 3, 4, 5]

for i, game_result_files in enumerate(game_result_files_s): #iterate over s game files
    scoreList_s = []
    for n, game_result_file in enumerate(game_result_files): #iterate over files in a subject
        df= pd.read_csv(game_result_file)
        nrows= len(df.score)-1
        print df.score[nrows] # end of list
        scoreList_s.append((trial[n], df.score[nrows]))

    meanList_s.append(np.mean(zip(*scoreList_s)[1]))
    stdList_s.append(np.std(zip(*scoreList_s)[1]))



for j, game_result_files in enumerate(game_result_files_d): #iterate over s game files
    scoreList_d = []
    for n, game_result_file in enumerate(game_result_files): #iterate over files in a subject
        df= pd.read_csv(game_result_file)
        nrows= len(df.score)-1
        print df.score[nrows] # end of list
        scoreList_d.append((trial[n], df.score[nrows]))

    meanList_d.append(np.mean(zip(*scoreList_d)[1]))
    stdList_d.append(np.std(zip(*scoreList_d)[1]))

    
n_groups = 6
bar_width = 0.35
opacity = 0.4
index = np.arange(n_groups)
error_config = {'ecolor': '0.3'}
print meanList_s

rects1 = plt.bar(index, meanList_s, bar_width,
                     alpha=opacity,
                     color='b',
                     yerr=stdList_s,
                     error_kw=error_config,
                     label='Score (random)')
rects2 = plt.bar(index+bar_width, meanList_d, bar_width,
                     alpha=opacity,
                     color='g',
                     yerr=stdList_d,
                     error_kw=error_config,
                     label='Score (deterministic)')

plt.xlabel('Subject',  fontname="Arial", fontsize=15)
plt.ylabel('Score (4 trials)',  fontname="Arial", fontsize=15)
plt.title('Mean score(random_vs_deterministic)',  fontname="Arial", fontsize=15)
plt.xticks(index + bar_width / 2, ('CM', 'IZ', 'KC', 'SP', 'SB', 'WJ'),  fontname="Arial",  fontsize=10)
plt.legend()
plt.tight_layout()


plt.show(block=False)

# save figure in pdf    

plt.savefig(os.path.join(baseDir,window_title+'.pdf'))
    

###################################
## 2. Strategy vs trials  (s1-s4, d1-d4)
###################################




###################################
## 3. Path analysis
###################################
