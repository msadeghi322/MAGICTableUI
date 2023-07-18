import argparse

####################################################
###               arguments                     ####
####################################################
#@Gooey
def get_arguments():
    # construct the argument parse and parse the arguments
    # connect arguments that relate to each other
    # 1st trial: snapshot 
    # 1) feedback mode (not recording) -> display, thread, clock, trace, linetrace, marker, tasktype, timed
    # 2) record mode (save raw video)
    #    A) record only  -> No-display, thread, clock, fps(?). No-trace, No-linetrace, No-marker. No-tasktype, timed
    #    B) visual fb + record orginal frame only.  -> display, thread, clock, fps(?). timed, trace, linetrace... (but "write" only original frame)
    # 3) postprocessing mode (run raw video)-> No-display,  No-thread, video, No-snapshot, condition, fps(?), trace, linetrace, tasktype. No-timed.

    # 1) Play mode: python main.py -d 1 -vir 1 -th 1 -clk 1 -tr 1 -ltr 1 -s 1 -m "el_object" -gt "p2p" -dir "ow" -t 16 (old)
    # 2) record mode (A)- FIG8:python main.py -d 0 -vir 0 -th 1 -clk 1 -tr 0 -ltr 0  -m "el_object" -gt "fig8" -c fig8 -s 0 -t 10 -dir "cw"
    #                     P2P: python main.py -d 0 -vir 0 -th 1 -clk 1 -tr 0 -ltr 0  -m "el_object" -gt "p2p" -c ID3 -s 0 -t 10 -dir "ow"
 
    #    record mode (B): python main.py -d 1 -vir 1 -th 1 -clk 1 -tr 0 -ltr 0  -s 1 -m "el_object" -gt "p2p" -dir "ow" -c cond -t 16 (if "fig8" no time limit?)
    # 3) Postprocesing mode (A): python main.py -d 0 -th 0 -clk 0 -s 0 -tr 1 -ltr 1 -m "el_object" -gt "p2p" -v Output/NoRed_output.avi_12s_20fps_20170923_133525.mp4  (if "fig8" no time limit?)


    # Abbreviated
    # 1) Play mode:  python main.py -mod "play" -tt "p2p" -sid "NT0" -hn "r" -t 30
    # 2) Pygame mode:  python main.py -mod "pygame" -c pygame -t 10
    # 3) record mode: python main.py -mod "record" -c fig8 -gt "p2p"  -dir "ow"  -t 10
    # 4) postprocessing: python main.py -mod "pp" -v videoOutput 20181210_121307_condition_iw_M11_NT0_Tracking_60s_60fps_raw.mp4 (UPDATE 2018.12.10)
    # timed for postprocessing.
    ## TODO: Log the timing if hitting the target in p2p. What is the hitting criteria?

    #ap = GooeyParser(description='Process some integers.')
    ap = argparse.ArgumentParser(prog="PROG", description="program")
    # groupa = ap.add_mutually_exclusive_group(required=True)
    ap.add_argument("-rest", "--RestBreak",type=int, default=10,           help = "the number of trials after which a rest break is given")
    ap.add_argument("-calibN", "--CalibPhotoNum",type=int, default=10,     help = "The number of pictures taken for calibration")
    ap.add_argument("-mtrnm", "--MetrnmInt",type=str, default="fixed",     help = "the metronome interval: it could be random (random delay each trial) or fixed")
    ap.add_argument("-mod", "--mode", type=str,  default="play",           help = "mode: play/pp/pygame. ")
    ap.add_argument("-trls", "--trials", type=int,  default=1,             help = "numbr of trials ")
    ap.add_argument("-cnd", "--Condition", type=int,  default=0,           help = "The condition of the experiment (when there are multiple conditions). The meaning of this index is up to the experimenter")
    ap.add_argument("-fam", "--Familiar", type=int,  default=0,           help = "Familiarization session")
    
    ap.add_argument('--version', action='version', version='%(prog)s 3.0')
    ap.add_argument("-d", "--display", type=int, default=-1,               help="Whether or not frames should be displayed")
    ap.add_argument("-rv", "--rawvideo", type=int, default=-1,             help="Whether you want to record raw video")
    ap.add_argument("-v", "--video", nargs=2,                              help = "1) subjectTag (e.g. 1003_JW), 2) video file to postprocess")
    ap.add_argument("-s", "--snapshot",type=int, default=0,                help = "take a new snapshot")
    ap.add_argument("-tr", "--trace", type=int, default=-1,                help="Whether or not traces should be displayed")
    ap.add_argument("-ltr", "--linetrace", type=int, default=-1,           help="Whether or not line traces should be displayed")
    ap.add_argument("-th", "--thread", type=int, default=-1,               help="Whether or not to use thread in reading frames")
    ap.add_argument("-b", "--buffer", type=int, default=64,                help="max buffer size")
    ap.add_argument("-f", "--fps", type=int, default=100,                  help="FPS of output video")
    ap.add_argument("-cod", "--codec", type=str, default="XVID",           help="codec of output video")
    ap.add_argument("-c", "--condition",  default ="condition",            help="condition of trial")
    ap.add_argument("-ts", "--targetsound", default=1,                     help="sound on at target")
    ap.add_argument("-tv", "--targetvisual", default=1,                    help="highlight if cursor on the target")
    ap.add_argument("-t", "--timed", type=int,  default=0,                 help="timed loop (s)")
    ap.add_argument("-m", "--marker", type=str,  default="object",         help="marker: Specify the tracking algorithm. (e.g. el_object, cl_object) ")
    ap.add_argument("-tt", "--tasktype", type=str,  default="p2p",         help="game types: p2p (point-to-point), fig8.")
    ap.add_argument("-clk", "--clock", type=int,  default="0",             help="display clock and frame number.")
    ap.add_argument("-vir", "--virtual", type=int,  default="0",           help="Virtual display instead of webcam display .")
    ap.add_argument("-pth", "--path", type=str,  default="diag",           help="Path of movement. Diagonal:diag, horizontal:hori, curve:cur")
    ap.add_argument("-pt", "--practice", type=int, default="0",            help="Practice stage (in pygame)")
    ap.add_argument("-pb", "--practice_boardtask", type=int, default="0",  help="Practice before the p2p or fig8 task.")
    ap.add_argument("-dc", "--discrete_control", type=int, default="0",    help="Discrete control of pygame")
    ap.add_argument("-kc", "--keyboard_control", type=int, default="0",    help="Keyboard control of pygame")
    ap.add_argument("-sid", "--subject", type=str, default="subj0",        help="subject ID")
    ap.add_argument("-nt", "--note",  type=int, default="0",               help="Leave note if necessary")
    ap.add_argument("-gnt", "--gamenote", type=int, default="0",           help="Leave game note if necessary")
    ap.add_argument("-gt", "--gametest", type=int, default="0",            help="Game Test mode: 1 if using mouse / keyboard")
    ap.add_argument("-br", "--bulkrecording", type=int, default="-1",      help="If recording many trials at once (bulk recording)")
    ap.add_argument("-hn", "--handedness", type=str, default="r",          help="Righthander:r, lefthander:l")
    ap.add_argument("-idx", "--idlevel", type=str, default="IDX",          help="Index of Difficulty (ID) 1 to 4.")
    ap.add_argument("-obs", "--obstacles", type=int, default="0",          help="Existence of polygon obstacles")
    args = vars(ap.parse_args())
    #args = ap.parse_args()
    print("video,:::", args["video"])
    print(args)

    if args["mode"] == "pp":  # PP: post processing
        #del args["mode"] #remove it
        args["snapshot"] = 0  #  must
        args["rawvideo"] = 0  # do not record raw video since we are working with it.
        args["thread"] = 0   #  must
        args["trace"] = 1           # option
        args["linetrace"] = 1      # option
        args["marker"] = "el_object_dual"  # option
        args["tasktype"] = "p2p"  # option
    
    elif args["mode"] == "play":  #
        #del args["mode"] #remove it
        args["note"] =0 # leave note on.
        args["clock"] = 1
        args["rawvideo"]=1 # record raw video as well for safety.
        args["targetsound"] = 1  # sound on at targets
        args["targetvisual"] = 1
        args["display"] = 1
        args["virtual"] = 0
        args["snapshot"] = 1
        args["thread"] = 1    # must
        args["trace"] = 1
        args["linetrace"] = 1
        args["marker"] = "el_object"  # option  "cl_object", "el_object", "cs_object", "cl_object+kalman", "el_object_dual", "el_object+kalman"
    
    elif args["mode"] == "dual":  #
        # del args["mode"] #remove it
        args["bulkrecording"] = 0
        args["clock"] =1
        args["note"] = 0
        args["rawvideo"]=1 # record raw video as well for safety.
        args["targetsound"] = 0  # sound on at targets0
        args["display"] = 1
        args["virtual"] = 0
        args["snapshot"] = 1
        args["thread"] = 1  # must
        args["trace"] = 0
        args["linetrace"] = 0
        args["marker"] = "el_object_dual"  # option  "cl_object", "el_object", "cs_object", "cl_object+kalman", "el_object_dual", "el_object+kalman"
    
    elif args["mode"] == "ms_dual":  #
        # del args["mode"] #remove it
        args["bulkrecording"] = 0
        args["clock"] =1
        args["note"] = 0
        args["rawvideo"]=1 # record raw video as well for safety.
        args["targetsound"] = 0  # sound on at targets0
        args["display"] = 1
        args["virtual"] = 0
        args["snapshot"] = 1
        args["thread"] = 1  # must
        args["trace"] = 1
        args["linetrace"] = 0
        args["marker"] = "el_object_dual"  # option  "cl_object", "el_object", "cs_object", "cl_object+kalman", "el_object_dual", "el_object+kalman"
    
    elif args["mode"] == "realtime_plot":  #
        # del args["mode"] #remove it
        args["rawvideo"] = 0
        args["targetsound"] = 0  # sound on at targets
        args["display"] = 1
        args["virtual"] = 0
        args["snapshot"] = 1
        args["thread"] = 1  # must
        args["trace"] = 1
        args["linetrace"] = 1
        args["marker"] = "el_object_dual"  # option  "cl_object", "el_object", "cs_object", "cl_object+kalman", "el_object_dual", "el_object+kalman"
    
    elif args["mode"] == "kalman_demo":  #
        #del args["mode"] #remove it
        args["display"] = 1
        args["virtual"] = 0
        args["snapshot"] = 1
        args["thread"] = 1    # must
        args["trace"] = 1
        args["linetrace"] = 1
        args["marker"] = "el_object+kalman"  # option  "cl_object", "el_object", "cs_object", "cl_object+kalman", "el_object_dual", "el_object+kalman"
    
    elif args["mode"] == "pygame":  # real time playing (no post-processing, otherwise thread should be set to 0)
        #del args["mode"] #remove it
        args["display"] = 0   # do not display openCV graphics.
        args["snapshot"] = 1
        args["thread"] = 1  # must
        args["trace"] = 0     # because display =0
        args["linetrace"] = 0  # because display =0
        args["marker"] = "el_object"  # option
        args["tasktype"] = "pygame"  # option?????????????????????
        args["gametest"]=0  # mouse or keyboard control test
        args["discrete_control"] = 0
        if args["gametest"]:
            args["discrete_control"] = 0
            args["keyboard_control"] = 1   # 0:mouse control, 1: keyboard control
        args["gamenote"]=1
    
    else:
        #del args["mode"] #remove it
        args["display"] = 0  # must
        args["thread"] = 1  # must
        args["trace"] = 0
        args["linetrace"] = 0
        args["marker"] = "el_object"  # option
    return args


