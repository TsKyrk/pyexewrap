Initial bug:
a python script using the __file__ variable to get its filesystem location would fail in pyexewrap since __file__ will be initialized to the wrapper's location.

Solution:
Python code is injected right after the shebang line to overwrite __file__ back to the expected default value.
I am guessing that there are other variables that could need the same trick to "simulate" a normal environment. Time will tell.