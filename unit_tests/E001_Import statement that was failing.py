#! /usr/bin/env python -m pyexewrap
from os import system

system("echo hello world")

def myfunction():
    system("echo hello again")
    
myfunction()