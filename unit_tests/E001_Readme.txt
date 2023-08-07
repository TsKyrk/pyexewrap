Initial bug:
import statements made within exec() wouldn't be visible from within a function called by exec.

Solution:
Using exec(mycode, globals(), globals()) solved the issue by binding the module level globals to the local level of exec
I don't know yet if this has some unwanted side effects.