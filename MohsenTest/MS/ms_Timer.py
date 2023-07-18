
import time
import numpy as np
import math


class ms_Timer:


    def __init__(This,*args):
        
        This.N=10000;
        
        if len(args) > 0:
            N=args;
        
        This.StartTime  = time.time() 
        This.Loops      = np.zeros((This.N,1), np.uint8)
        This.LastToc    = 0
        This.tic_time   = -1
        This.loop_count = 0
        This.toc_count  = 0
        #This.TimeLapse  = 0
        
    
    def GetTime(This):
        R = time.time() - This.StartTime
        return R
    
    
    def Reset(This):
        
        This.loop_count = 0
        This.toc_count  = 0
        This.tic_time   = -1
        This.StartTime  = time.time()
        This.TimeLapse  = 0
        
        
        
    def Loop(This):
        This.loop_count = This.loop_count+1
        w = circ_buffer(This.loop_count,This.N)
        This.Loops[w-1] = This.GetTime()
    
    
    def Tic(This):
        This.tic_time = This.GetTime()    
        
        
        
        
    def Toc(This):
        if This.tic_time>0:
            This.toc_count = This.toc_count+1
            This.LastToc   = This.GetTime()
            iti = This.LastToc-This.tic_time
            This.tic_time = -1
            
        elif This.toc_count > 0:   # if Tic wasn't called, use previous Toc as new Tic
            iti = This.GetTime()-This.LastToc
            This.LastToc = This.GetTime()
    
        else:
            iti = This.GetTime();
    
        return iti    
            
        
def circ_buffer(count,N):
  k= 1 + ((count-1) % N) 
  return k








        
