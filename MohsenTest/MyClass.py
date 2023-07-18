#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 20:13:19 2019

@author: mohsensadeghi
"""

class MyClass:
    
    
    def __init__(This):
        
        This.a1 = 0
        This.a2 = 0
        This.a3 = 0
        
        
    def func_1(abc):
        abc.a1 = 1
        abc.a2 = 1
        abc.a3 = 1

    def func_2(abc):
        abc.a1 = abc.a1 + abc.a2 + abc.a3
        abc.a2 = abc.a1 * abc.a2 * abc.a3
        abc.a3 = abc.a1 - abc.a2 - abc.a3


    