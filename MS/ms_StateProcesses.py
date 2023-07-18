# All the state-related processes are here

from MS.ms_Timer import ms_Timer
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class ms_StateProcesses:
    
    # build a class to resemble the structure data type in matlab
    
    def __init__(STATE,HW,*args):
        
        
        # State design 
        STATE.INITIALIZE    = 1
        STATE.SETUP         = 2
        STATE.START         = 3
        STATE.GO            = 4
        STATE.METRONOME     = 5
        STATE.REACTTIME     = 6
        STATE.MOVING        = 7
        STATE.INTARGET      = 8   
        STATE.RECOVER       = 9  
        STATE.FINISH        = 10
        STATE.NEXT          = 11   
        STATE.INTERTRIAL    = 12
        STATE.EXIT          = 13
        STATE.BALLESCAPED   = 14
        STATE.OBSTACLE      = 15
        STATE.REST          = 16
        STATE.TOOSOON       = 17
        STATE.TOOSLOW       = 18
        
        
        STATE.Names = ['INITIALIZE' , 'SETUP'      , 'START'    , 'GO'         , 'METRONOME' , 
                       'REACTTIME'  , 'MOVING'     , 'INTARGET' , 'RECOVER'    , 'FINISH' , 
                       'NEXT'       , 'INTERTRIAL' , 'EXIT'     , 'BALLESCAPED' , 'OBSTACLE',
                       'REST', 'TOOSOON' , 'FAMILIARIZE']
        
        
        
        
         
        STATE.From          = 0   # will be reset externally in each loop
        STATE.To            = 0
        STATE.Last          = 1
        STATE.Current       = 1
        STATE.LoopCnt       = 0         
        STATE.LoopFlag      = False         
        STATE.LoopList      = []
        STATE.TrialCnt      = 1
        STATE.TrialsAll     = HW.NumberOfTrials       # this will be reset externally 
        
        
        # Timing
        STATE.StateTimer            = ms_Timer()    # measures the time from beginning of each state
        STATE.ExperimentTimer       = ms_Timer()    # Measures the duration of the whole experiment
        STATE.MovementTimer         = ms_Timer()    # Measures time from the begining of the movement within each trial
        STATE.TrialTimer            = ms_Timer()    # measures time during a trial
        STATE.TrialTimeList         = []
        STATE.SetupDelay            = .2    # Delay time s after the start
        STATE.StartDelay            = 0    # Delay time s after the start
        STATE.GoDelay               = .1    # Delay before sending the go signal
        STATE.RotationDuration      = 1    # how long should rotation go before we get to metronome
        STATE.InTargetDelay         = 0   # time to stay in target to register as hitting the target
        STATE.RecoveryTime          = 3
        STATE.ReactionMaxDelay      = 2
        STATE.ErrorWait             = 1
        STATE.FinishDelay           = .2
        STATE.IntertrialDelay       = 2
        STATE.SubStateTime          = 0 # to control time within a state
        STATE.MaxMoveTime           = 1.5
        STATE.RotReactionTimeOut    = 3
        STATE.MetronomeReactionTime = 0
        STATE.MetronomeOnset        = 0  # Time from the trial onset when the metronome sounds
        STATE.MetronomeDelay        = 2    # The fixed metronome delay from an exponential diestribution
        STATE.ReachDuration         = 0
        STATE.ExitFlag              = False
        STATE.RestFlag              = False
        STATE.BallEscapedFlag       = 0
        STATE.BallEscapedCnt        = 0 #  how many time ball escaped?
        STATE.RestBreakTime         = 30 # sec
        STATE.ExperimentDuration    = 0;
        STATE.BallEscapedDelay      = .1    # wait after ball escape (needed)
        STATE.BallEscapeTime        = 0  # when during the trial the ball escaped
        STATE.FamiliarizeTime       = 20
        STATE.TooSlowFlag           = False

#        STATE.RecoveryTime          = 2    # this is for simple p2p balistic movement
#        STATE.MetronomeDelay        = .1
        

# Transition to the next state ------------------------------------------------
    
    def ms_NextState(STATE, TargetState):
        if STATE.Current==TargetState:
            return
        
        STATE.StateTimer.Reset()
        STATE.Last    = STATE.Current;
        STATE.From    = STATE.Last;
        STATE.Current = TargetState;
        STATE.To      = TargetState;
            
    
    
    
    
    def IsNextTrial(STATE):
        ok = False
        if STATE.TrialCnt< STATE.TrialsAll:
            ok = True
            STATE.TrialCnt += 1
        return ok    
    
    
    
    def StartLoopCount(STATE):
        STATE.LoopList = []
        STATE.LoopCnt  = 0
        STATE.TrialTimeList = []
        STATE.TrialTimer.Reset()
        STATE.LoopFlag = True
        
    
    
    def StopLoopCount(STATE):
        STATE.LoopFlag = False
        STATE.TrialTimer.Reset()
        
    
    
    
    
    def ms_StateProcess(STATE,HW):  # pass in the hardware information
        
        
        # check for ball escape
        if STATE.BallEscapedFlag==0 and STATE.Current < STATE.FINISH: # if next, don't bother
            if HW.BallEscaped():
                STATE.ms_NextState(STATE.BALLESCAPED)
        
        
        # record loop count and time
        if STATE.LoopFlag:
            STATE.LoopCnt += 1
            STATE.LoopList.append( STATE.LoopCnt )
            STATE.TrialTimeList.append( STATE.TrialTimer.GetTime() )
            
          
        
        # check for rest-break
        if STATE.TrialCnt % HW.args["RestBreak"] ==0:
            STATE.RestFlag=True
            
            
            
        # Go through the states
        if STATE.Current == STATE.INITIALIZE:
            print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
            STATE.ExperimentTimer.Reset()
            STATE.ms_NextState(STATE.SETUP)
            print("Swiched to state:",STATE.Names[STATE.Current-1])
            
            # might need to go for the calibration here as well
        
        
        
        elif STATE.Current == STATE.SETUP:
            
            if not HW.BallEscaped():
                STATE.BallEscapedFlag = 0
                STATE.BallEscapeTime = 0
                
                if HW.InHome():
                    if STATE.StateTimer.GetTime() - STATE.SubStateTime > STATE.SetupDelay:
                        print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                        print('..............  Cup home ................')
                        STATE.SubStateTime = 0
                        STATE.ms_NextState(STATE.START)
                        print("Swiched to state:",STATE.Names[STATE.Current-1])
                        
                else:
                    STATE.SubStateTime = STATE.StateTimer.GetTime()   # we lose the total time in this state
                
            
        
        elif STATE.Current == STATE.START:    # We should ideally collect data from here
            if STATE.StateTimer.GetTime() > STATE.StartDelay:    # remember the state timer is reset when moving to next state
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.MovementTimer.Reset()
                
                if  HW.args["Familiar"] ==1:
                    STATE.ms_NextState(STATE.FAMILIARIZE)
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
                else:
                    STATE.ms_NextState(STATE.GO)                   # This delay is to start recording a few ms before the movement starts
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
                
        
        
        elif STATE.Current == STATE.GO:
            if HW.InHome() and HW.BallRotating():
            #if HW.InHome():  # simple p2p movement
                if STATE.StateTimer.GetTime() - STATE.SubStateTime > STATE.RotationDuration: 
                    print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                    STATE.ms_NextState(STATE.METRONOME)
                    STATE.SubStateTime = 0
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
            elif not HW.InHome():
                print("Moved too soon!")
                STATE.ms_NextState(STATE.TOOSOON)
                STATE.SubStateTime = 0
            else:
                STATE.SubStateTime = STATE.StateTimer.GetTime()   # we lose the total time in this state
            
            
        
        
        elif STATE.Current == STATE.METRONOME:
            
            if HW.InHome() and HW.BallRotating():  # also check for early move
            #if HW.InHome():  # simple p2p movement
                if STATE.StateTimer.GetTime() - STATE.SubStateTime > STATE.MetronomeDelay:
                    print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                    STATE.ms_NextState(STATE.REACTTIME)
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
                    STATE.MetronomeOnset = STATE.TrialTimer.GetTime() 
                    STATE.SubStateTime = 0
            elif not HW.InHome():
                print("Moved too soon!")
                STATE.ms_NextState(STATE.TOOSOON)
                STATE.SubStateTime = 0
            else:
                STATE.SubStateTime = STATE.StateTimer.GetTime()
                    
                    
                    
                    
            
        elif STATE.Current == STATE.REACTTIME:
            if not HW.InHome():
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.MetronomeReactionTime = STATE.StateTimer.GetTime()
                STATE.ms_NextState(STATE.MOVING)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
                
            #elif STATE.StateTimer.GetTime() > STATE.ReactionMaxDelay:
             #   print(' .......... Move It .........')
                
        
        
        elif STATE.Current == STATE.MOVING:
            
            if HW.InTarget():
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.ReachDuration = STATE.StateTimer.GetTime()
                STATE.ms_NextState(STATE.INTARGET)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
                
                
            elif STATE.StateTimer.GetTime() > STATE.MaxMoveTime:
                #print(' .......... Too slow .........')
                STATE.TooSlowFlag = True
                
                
        
        elif STATE.Current == STATE.INTARGET:
            
            if HW.InTarget():
                if STATE.StateTimer.GetTime() - STATE.SubStateTime > STATE.InTargetDelay: 
                    print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                    print('..............  Cup in Target ................')
                    STATE.SubStateTime = 0
                    STATE.ms_NextState(STATE.RECOVER)
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
                    
            else:
                STATE.SubStateTime = STATE.StateTimer.GetTime()   # we lose the total time in this state
            
            
            
        
        elif STATE.Current == STATE.RECOVER:
            if STATE.StateTimer.GetTime() > STATE.RecoveryTime:
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.ms_NextState(STATE.FINISH)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
                
        
        
        
        
        elif STATE.Current == STATE.FINISH:
            if STATE.StateTimer.GetTime() > STATE.FinishDelay:
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.MovementDuration = STATE.MovementTimer.GetTime()
                if STATE.BallEscapedFlag: 
                    STATE.ms_NextState(STATE.SETUP)
                else:
                    STATE.ms_NextState(STATE.NEXT)
                    print("Swiched to state:",STATE.Names[STATE.Current-1])
            
                    
                # Finish this trial and do all the saving and get ready for the next trial. Target and home positions might be swapped at this point
        
        
        
        
        elif STATE.Current == STATE.NEXT:
            if not STATE.IsNextTrial():
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.ms_NextState(STATE.EXIT)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
            
            elif STATE.RestFlag:
                STATE.ms_NextState(STATE.REST)
                STATE.RestFlag = False
            else:
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.ms_NextState(STATE.INTERTRIAL)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
            
            
            
            
        elif STATE.Current == STATE.INTERTRIAL:    # We could decide whether we want to make the ball stationary before next trial, or just continue with the ball movement from previous trial
            if STATE.StateTimer.GetTime() > STATE.IntertrialDelay:
                HW.SwapTargets()
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                STATE.ms_NextState(STATE.SETUP)
                print("Swiched to state:",STATE.Names[STATE.Current-1])
                
        
        
        
        elif STATE.Current == STATE.EXIT:
            STATE.ExperimentDuration = STATE.ExperimentTimer.GetTime()
            STATE.ExitFlag = True  
            
        
        
        
        # Check all the preivious states for ball scape- depending on the last state, do appropriately
        elif STATE.Current == STATE.BALLESCAPED:
            STATE.BallEscapedFlag = 1  # only is turned off in setup state
            
            if STATE.StateTimer.GetTime() > STATE.BallEscapedDelay: # this is necessary delay so idle function could affect, otherwise, as soon as state changes to escaped, immediately changes to setup, and the idle func never catches it
                print("STATE:",STATE.Names[STATE.Current-1], f'Time: {STATE.StateTimer.GetTime():.3f} ')
                if STATE.Last <STATE.INTARGET: # just in case ball drops before reach ends
                    STATE.ReachDuration = -1000
                
                if STATE.Last >= STATE.METRONOME:
                    STATE.BallEscapedCnt += STATE.BallEscapedFlag
                    print('Ball Escaped Flag',STATE.BallEscapedFlag)
                    STATE.ms_NextState(STATE.FINISH)
                    STATE.BallEscapeTime = STATE.TrialTimer.GetTime()
                else:
                    STATE.ms_NextState(STATE.SETUP)  # repeat the trial, but also record the trial in which ball scaped 
        
        
        
        elif STATE.Current == STATE.OBSTACLE:
            pass
            
        
        
        
        
        elif STATE.Current == STATE.REST:
            if STATE.StateTimer.GetTime() > STATE.RestBreakTime:
                STATE.ms_NextState(STATE.INTERTRIAL)
        
       
       
       
       
        elif STATE.Current ==STATE.TOOSOON:
            if STATE.StateTimer.GetTime() > .6:
                STATE.ms_NextState(STATE.SETUP)
       
       
       
       
        elif STATE.Current == STATE.FAMILIARIZE:
            if STATE.StateTimer.GetTime() > STATE.FamiliarizeTime:
                STATE.ms_NextState(STATE.FINISH)
       
       
       
       
       
       
       
       
       
