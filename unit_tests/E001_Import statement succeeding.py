
import pprint as pp
from os import system

pp.pprint(globals())

system("echo hello world")

def myfunction():
    system("echo hello again")
    
myfunction()

input("Press ENTER to continue")