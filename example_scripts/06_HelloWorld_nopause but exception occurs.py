#!/usr/bin/env python -m pyexewrap

print("hello world")
print(1/0)

#Don't pause this script in console (unless there is an exception) :
globals()['pyexewrap_must_pause_in_console'] = False