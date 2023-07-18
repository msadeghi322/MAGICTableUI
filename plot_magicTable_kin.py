#import necessary modules
#if you encounter an 'import error' run the following commands (for linux only)
#in terminal: sudo apt-get install python-pandas
#in terminal: sudo apt-get install python-matplotlib
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import cv2
import pickle
import numpy as np
from scipy.signal import butter, lfilter, freqz
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import pdb
from save import save_output_at

def ID_calc():
    #####################################################
    ##################### definitions ###################
    #####################################################
    marble_d = 16 # in mm
    cup_depthID1 = 50 # arbitrary depth with no-marble situation
    cup_depthID2 = 20 # arbitrary depth with safety rim in the margin of the cup
    cup_depthID3 = 12
    cup_depthID4 = 5

    ## index of difficulty calculation
    ID1 = float(marble_d)/float(cup_depthID1) # 0.32 . baseline.  # index of difficulty = ratio of the marble size to the depth of the cup. 
    ID2 = float(marble_d)/float(cup_depthID2) # 0.8
    ID3 = float(marble_d)/float(cup_depthID3) # 1.33
    ID4 = float(marble_d)/float(cup_depthID4) # 3.2

    return ID1, ID2, ID3, ID4
    


def ID_fileList(baseDir, date):
    folder1 = "/dataframeOutput"
    FIG8_files = glob.glob(baseDir+ "/"+date+ folder1 + '/*fig8*success1*') # * means all if need specific format then *.csv
    FIG8_files = [FIG8_files]
    IF4_files = glob.glob(baseDir+ "/"+date+folder1 + '/*ID4*success1*') # * means all if need specific format then *.csv
    IF3_files = glob.glob(baseDir+ "/"+date+folder1 + '/*ID3*success1*') # * means all if need specific format then *.csv
    IF2_files = glob.glob(baseDir+ "/"+date+folder1 + '/*ID2*success1*') # * means all if need specific format then *.csv
    IF1_files = glob.glob(baseDir+ "/"+date+folder1 + '/*ID1*success1*') # * means all if need specific format then *.csv

    IF4_files_iw = glob.glob(baseDir+ "/"+date+folder1 + '/*ID4*iw*success1*') # * means all if need specific format then *.csv
    IF3_files_iw = glob.glob(baseDir+ "/"+date+folder1 + '/*ID3*iw*success1*') # * means all if need specific format then *.csv
    IF2_files_iw = glob.glob(baseDir+ "/"+date+folder1 + '/*ID2*iw*success1*') # * means all if need specific format then *.csv
    IF1_files_iw = glob.glob(baseDir+ "/"+date+folder1 + '/*ID1*iw*success1*') # * means all if need specific format then *.csv
    IF4_files_ow = glob.glob(baseDir+ "/"+date+folder1 + '/*ID4*ow*success1*') # * means all if need specific format then *.csv
    IF3_files_ow = glob.glob(baseDir+ "/"+date+folder1 + '/*ID3*ow*success1*') # * means all if need specific format then *.csv
    IF2_files_ow = glob.glob(baseDir+ "/"+date+folder1 + '/*ID2*ow*success1*') # * means all if need specific format then *.csv
    IF1_files_ow = glob.glob(baseDir+ "/"+date+folder1 + '/*ID1*ow*success1*') # * means all if need specific format then *.csv

    IDX_files = [IF1_files_iw+IF1_files_ow, IF2_files_iw+IF2_files_ow, IF3_files_iw+IF3_files_ow, IF4_files_iw+IF4_files_ow]

    IDX_files_iw = [IF1_files_iw, IF2_files_iw,IF3_files_iw, IF4_files_iw]
    IDX_files_ow = [IF1_files_ow, IF2_files_ow,IF3_files_ow, IF4_files_ow]
    

    #list_of_files = IF4_files
    return FIG8_files, IDX_files, IDX_files_iw, IDX_files_ow


def circle_property(baseDir, timeTag, date):
    timetag_circles = timeTag+ "_circles.dump"  #1006_morning: 20171006_112249  # 1003: 20171003_170016
    circles = pickle.load(open(baseDir+ "/"+date +'/pickles/'+ timetag_circles, 'rb'))
    x1=circles[0][0] # x
    x2=circles[1][0] # x
    y1=circles[0][1] # y
    y2=circles[1][1] # y
    r1=circles[0][2] # r
    r2=circles[1][2] # r

    return x1, y1, r1, x2, y2, r2
#width = 640
#height = 360






## LPF

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


#Filter test
# Plot the frequency response.
# Get the filter coefficients so we can check its frequency response.
def LPFdemo(cutoff, fs, order, data, t):
    b, a = butter_lowpass(cutoff, fs, order)
    w, h = freqz(b, a, worN=8000)
    plt.subplot(2, 1, 1)
    plt.plot(0.5*fs*w/np.pi, np.abs(h), 'b')
    plt.plot(cutoff, 0.5*np.sqrt(2), 'ko')
    plt.axvline(cutoff, color='k')
    plt.xlim(0, 0.5*fs)
    plt.title("Lowpass Filter Frequency Response")
    plt.xlabel('Frequency [Hz]')
    plt.grid()

    # Demonstrate the use of the filter.
    # First make some data to be filtered.
    plt.subplot(2, 1, 2)
    plt.plot(t, data, 'b-', label='data')
    plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
    plt.xlabel('Time [sec]')
    plt.grid()
    plt.legend()
    plt.subplots_adjust(hspace=0.35)



####################################################################
################      FIG8  ALL ##       ###########################
####################################################################

def plot_fig8(FIG8_files, date, data_columnx, data_columny, xlim, ylim, x1, x2, y1, y2, r1, r2):   
    #read data from csv file into data frame
    #fig = plt.gcf()
    nrows = 1
    fig, axes = plt.subplots(nrows, 1)
    fig.subplots_adjust(hspace = .5, wspace=.2)
    #axes = axes.ravel()
    window_title = date + ' Continuous'+' xy'
    fig.canvas.set_window_title(window_title)

    for i, ID_file in enumerate(FIG8_files): # 
        for thisfile in ID_file: # interate all files in that category
            #print thisfile
            df= pd.read_csv(thisfile)
            axes.plot(df[data_columnx], df[data_columny])
    ##        axes[1].plot(df['elapsedTime'], df['xObject'])
    ##        axes[2].plot(df['elapsedTime'], df['yObject'])

        circle1 = plt.Circle((x1, y1), r1, linewidth = 4, color='b', fill=False)
        circle2 = plt.Circle((x2, y2), r2, linewidth = 4, color='b', fill=False)
        axes.add_patch(circle1)
        axes.add_patch(circle2)
        axes.set_aspect(1)
        axes.set_title("Continuous"+str(i+1)+"_"+date, fontsize='large')
        axes.set_xlim(xlim)
        axes.set_ylim(ylim)

  
    # save figure in pdf 
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.pdf')


    ## add x-time panel, 20180130
    nrows = 2
    fig, axes = plt.subplots(nrows, 1)
    fig.subplots_adjust(hspace = .5, wspace=.2)
    #axes = axes.ravel()
    window_title = date + ' Fig8'+' xt'
    fig.canvas.set_window_title(window_title)

    df= pd.read_csv(FIG8_files[0][0])
    axes[0].plot(df['elapsedTime'], df[data_columnx])
    
    axes[0].set_title("Fig8_"+date, fontsize='large')
    axes[0].set_xlim([0, 20000])
    
    axes[1].plot(df['elapsedTime'], df[data_columny])
    axes[1].set_title("Fig8_"+date, fontsize='large')
    axes[1].set_xlim([0, 20000])
    #axes.set_ylim( [50, 350])
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.eps', format='eps')


    

####################################################################
##############      P2P X-Y plane        ###########################
####################################################################        

def plot_xy(IDX_files, nrows, ncols, date, data_columnx, data_columny, xlim, ylim, x1, x2, y1, y2, r1, r2):
    fig, axes = plt.subplots(nrows, ncols)
    fig.subplots_adjust(hspace = .5, wspace=.2)
    axes = axes.ravel()
    window_title = date + ' Discrete'+' xy'
    fig.canvas.set_window_title(window_title)


    for i, ID_file in enumerate(IDX_files): # interate over ID1 to ID4
        for thisfile in ID_file: # interate all files in that category
            #print thisfile
            df= pd.read_csv(thisfile)
            axes[i].plot(df[data_columnx], df[data_columny])

        circle1 = plt.Circle((x1, y1), r1, linewidth = 4, color='b', fill=False)
        circle2 = plt.Circle((x2, y2), r2, linewidth = 4, color='b', fill=False)
        axes[i].add_patch(circle1)
        axes[i].add_patch(circle2)
        axes[i].set_aspect(1)
        axes[i].set_title("Discrete-ID"+str(i+1)+"_"+date, fontsize='large')
        axes[i].set_xlim(xlim)
        axes[i].set_ylim(ylim)
    # save figure in pdf    
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.pdf')


####################################################################
##############      P2P plot 1 column   ############################
#################################################################### 
def plot_1axis(IDX_files, nrows, ncols, date, data_column, xlim, ylim):
    fig, axes = plt.subplots(nrows, ncols)
    fig.subplots_adjust(hspace = .5, wspace=.2)
    axes = axes.ravel()
    window_title = date + ' Discrete '+data_column
    fig.canvas.set_window_title(window_title)

    for i, ID_file in enumerate(IDX_files): # interate over ID1 to ID4
        print ID_file
        for thisfile in ID_file: # interate all files in that category
            df= pd.read_csv(thisfile)

            
            # LPF the digitally sampled signal
            T = 5.0         # seconds
            n = int(len(df[data_column])) # total number of samples
            t = np.linspace(0, T, n, endpoint=False)
            # "Noisy" data.  We want to recover the 1.2 Hz signal from this.
            datax = df[data_column]
     

            # Filter the data, and plot both the original and filtered signals.
            filteredx = butter_lowpass_filter(datax, cutoff, fs, order)
            #filteredy = butter_lowpass_filter(datay, cutoff, fs, order)
            
            axes[i].plot(df['elapsedTime'], filteredx)

            #axes[i].set_aspect(1)
            axes[i].set_title("Discrete-ID"+str(i+1)+"_"+date, fontsize='large')
            axes[i].set_xlim(xlim)
            axes[i].set_ylim(ylim)
    # save figure in pdf    
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.pdf')
    
####################################################
###                    main                     ####
####################################################
def run_main():
    plt.close('all')

    ID1, ID2, ID3, ID4 = ID_calc()  # calculate ID
    # get the latest file in a folder
    #list_of_files = glob.glob('/Users/wonjoonsohn/Dropbox/ActionLab/MagicBoard/ObjectTracking/ObjectTrackingDrone/Output/1002/dataframeOutput/*') # * means all if need specific format then *.csv
    baseDir = '/Users/wonjoonsohn/Documents/workspace_python/MAGicTableGame/Output'

 #  date, timeTag_p2p, timeTag_fig8 ='1003_JW', "20171003_160852", "20171003_160852"
    #date, timeTag_p2p, timeTag_fig8 ='1004_HM_EMU', "20171004_135501", "20171004_113334"
    #date, timeTag_p2p, timeTag_fig8 ='1006_morning', "20171006_112249", "20171006_110232"
    date, timeTag_p2p, timeTag_fig8 ='1006_afternoon', "20171006_153626", "20171006_152654"
    
    ## 1002_CN: 20171002_154348  (no fig 8)
    ## 1004_HM_EMU p2p: 20171004_135501 (many snapshots)
    ## 1004_HM_EMU fig8: 20171004_113334

    FIG8_files, IDX_files, IDX_files_iw, IDX_files_ow = ID_fileList(baseDir, date)
    x1, y1, r1, x2, y2, r2= circle_property(baseDir, timeTag_p2p, date)

    x1f, y1f, r1f, x2f, y2f, r2f= circle_property(baseDir, timeTag_fig8, date)


    ### Filter requirements.
    global order
    order= 6
    global fs
    fs= 50.0       # sample rate, Hz
    global cutoff
    cutoff= 15.00  # desired cutoff frequency of the filter, Hz


    ### plot parameters
    
    plot_fig8(FIG8_files, date, 'xObject', 'yObject', [100, 550], [50, 350], x1f, x2f, y1f, y2f, r1f, r2f)
    plot_xy(IDX_files, 2, 2, date, 'xObject', 'yObject', [100, 550], [50, 350], x1, x2, y1, y2, r1, r2 )
    plot_1axis(IDX_files, 2, 2, date, 'xObject', [1000, 10000], [150, 500] )
    plot_1axis(IDX_files, 2, 2, date, 'yObject',[1000, 10000], [100, 300] )

    plt.show()

    ####################################################################
    ################      P2P time to reach  ###########################
    ####################################################################


    # bar graph
    meanList_iw=[]
    stdList_iw=[]
    meanList_ow=[]
    stdList_ow=[]

    ##### inward
    reachtimeList_iw = []

    ID_level = [ID1, ID2, ID3, ID4]

    for i, ID_file in enumerate(IDX_files_iw): # interate over ID1 to ID4
        print ID_file
        reachtimeListID_iw = []
        for thisfile in ID_file: # interate all files in that category
            df= pd.read_csv(thisfile)

            startindex =  next((i for i, x in enumerate(df['startCue']) if x), None)
            starttime= df['elapsedTime'][startindex]
            endtime = df['elapsedTime'][len(df['elapsedTime'])-1] # last element
            reachtime= endtime- starttime 
            
            #print reachtime
            reachtimeListID_iw.append((ID_level[i], reachtime))

        reachtimeList_iw = reachtimeList_iw + reachtimeListID_iw           
        meanList_iw.append(np.mean(zip(*reachtimeListID_iw)[1])) # second elements of list
        stdList_iw.append(np.std(zip(*reachtimeListID_iw)[1])) # second elements of list


    #### outward
    reachtimeList_ow = []

    for i, ID_file in enumerate(IDX_files_ow): # interate over ID1 to ID4
        print ID_file
        reachtimeListID_ow = []
        for thisfile in ID_file: # interate all files in that category
            df= pd.read_csv(thisfile)

            startindex =  next((i for i, x in enumerate(df['startCue']) if x), None)
            starttime= df['elapsedTime'][startindex]
            endtime = df['elapsedTime'][len(df['elapsedTime'])-1] # last element
            reachtime = endtime- starttime 
            #print reachtime
            reachtimeListID_ow.append((ID_level[i], reachtime))

        reachtimeList_ow = reachtimeList_ow + reachtimeListID_ow
        meanList_ow.append(np.mean(zip(*reachtimeListID_ow)[1]))
        stdList_ow.append(np.std(zip(*reachtimeListID_ow)[1]))
##        axes[i].plot(reachtimeList, 'go')
##        axes[i].set_title("Discrete-ID"+str(i+1)+"_"+date, fontsize='large')
##        #axes[i].set_xlim([1000, 10000])
##        axes[i].set_ylim([1000, 9000])

    ####################################################           
    ### plotting barplot movement time    
    ####################################################
    
    fig, axes = plt.subplots()
    window_title = date + ' Discrete time Barplot'
    fig.canvas.set_window_title(window_title)

    n_groups = 4
    bar_width = 0.35
    opacity = 0.4
    index = np.arange(n_groups)
    error_config = {'ecolor': '0.3'}

    rects1 = plt.bar(index, meanList_iw, bar_width,
                     alpha=opacity,
                     color='b',
                     yerr=stdList_iw,
                     error_kw=error_config,
                     label='Inward movement time(ms)')
    rects2 = plt.bar(index+bar_width, meanList_ow, bar_width,
                     alpha=opacity,
                     color='g',
                     yerr=stdList_ow,
                     error_kw=error_config,
                     label='Outward movement time(ms)')

    plt.ylim([500, 5000])
    plt.xlabel('ID group')
    plt.ylabel('reach time')
    plt.title('Discrete Reach time '+date)
    plt.xticks(index + bar_width / 2, ('ID1', 'ID2', 'ID3', 'ID4'))
    plt.legend()
    plt.tight_layout()

    # save figure in pdf    
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.pdf')



    

    ####################################################
    ## plotting linear regression of ID vs movement time
    ####################################################
    fig, axes = plt.subplots()

    window_title = date+ ' Discrete LR'+' time scatter'
    fig.canvas.set_window_title(window_title)
            
    # Create linear regression object


    # Train the model using the training sets

    ID = [i[0] for i in reachtimeList_iw]
    Y = [i[1] for i in reachtimeList_iw]

    X=np.array(ID)
    Y=np.array(Y)
    #X2=np.reshape(X, (1, len(ID)))
    #Y2=np.reshape(Y, (1, len(ID)))

    #print"X is: ", X[:10]
    #print "Y is:  ", Y[:10]

    Xreshape=X.reshape(len(ID),1)
    regr = linear_model.LinearRegression()
    regr.fit(Xreshape, Y)
    # The coefficients
    print('Coefficients: \n', regr.coef_)
    # The mean squared error


    # Make predictions using the testing set
    y_pred = regr.predict(Xreshape)
    # The coefficients
    print('Coefficients: \n', regr.coef_)
    # The mean squared error
    print("Mean squared error: %.2f"
          % mean_squared_error(Y, y_pred))


    # Plot outputs
    plt.scatter(Xreshape, Y,  color='black')
    plt.plot(Xreshape, y_pred, color='blue', linewidth=3)

    ##
    ##m = regr.coef_[0]
    ##b = regr.intercept_
    ##
    ##print(' y = {0} * x + {1}'.format(m, b))
    ##
    ##plt.scatter(X2, Y2,  color='black')
    ###plt.plot(X2, Y2, color='blue', linewidth=3)
    ##plt.plot([b, m*X2 + b], 'r')
    ###plt.plot(X2,Y_pred, color='blue', linewidth=3)


    plt.xticks(ID)
    plt.xlabel('movement time (ms)') 
    plt.yticks = np.arange(0, 10000, 1000)
    plt.ylabel('ID') 
    plt.legend()
    plt.tight_layout()

    # save figure in pdf    
    dataOutput_path= save_output_at("pdf_figures")
    plt.savefig(dataOutput_path+'/'+window_title+'.pdf')

    plt.show()



if __name__ == "__main__":
    run_main()


