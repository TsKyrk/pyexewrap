=============Initial bug===========
According to the Python documentation, it should be possible to intercept a system exit ( exit(1) statement for instance ) since this raises a SystemExit exception that can be handled and not raised (exit canceled).
It appeared that the exit mechanism can indeed be interrupted and canceled as described but it seems that this leaves the environment in a wrong state since any following input("your text") statement will result in the following exception : ValueError: I/O operation on closed file.
In my opinion this is a bug in Python itself. I could confirm that the "bug" was introduced at Python v3.10.0b1

=============Python Docs==========
Extracted from : https://docs.python.org/3/library/sys.html?highlight=exit#sys.exit
"Since exit() ultimately “only” raises an exception, it will only exit the process when called from the main thread, and the exception is not intercepted. Cleanup actions specified by finally clauses of try statements are honored, and it is possible to intercept the exit attempt at an outer level."

=============Investigations==========
####Dichotomy in Python versions using Pyenv-win####
Python v3.10.0a7 behaves as expected (Apr 5, 2021)
Python v3.10.0b1 introduces the bug (May 3, 2021)
There are about 500 commits in between and at least one of them has SystemExit in its description :
https://github.com/python/cpython/pull/25441/commits/1861add7384a8d709f83c491c595630b5b38e801

There is also this in managers.py :
https://github.com/python/cpython/blob/7c29ae1f0585378dba4d220a2c0fb5dd49fdab3e/Lib/multiprocessing/managers.py#L163C1-L183C24
    def serve_forever(self):
        '''
        Run the server forever
        '''
        self.stop_event = threading.Event()
        process.current_process()._manager_server = self
        try:
            accepter = threading.Thread(target=self.accepter)
            accepter.daemon = True
            accepter.start()
            try:
                while not self.stop_event.is_set():
                    self.stop_event.wait(1)
            except (KeyboardInterrupt, SystemExit):
                pass
        finally:
            if sys.stdout != sys.__stdout__: # what about stderr?
                util.debug('resetting stdout, stderr')
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
            sys.exit(0)

#### Changelog of Python 3.10 ####
https://docs.python.org/3.10/whatsnew/changelog.html
Only one reference to SystemExit. It the same evolution as above:
LIBRARY
    bpo-43867: The multiprocessing Server class now explicitly catches SystemExit and closes the client connection in this case. It happens when the Server.serve_client() method reaches the end of file (EOF).

#### Wandering in Github ####
builtins.exit is an objet bind to _sitebuiltins.Quitter here : https://github.com/python/cpython/blob/d6892c2b9263b39ea1c7905667942914b6a24b2c/Lib/site.py#L401
and calling this Quitter does indeed close stdin: https://github.com/python/cpython/blob/d6892c2b9263b39ea1c7905667942914b6a24b2c/Lib/_sitebuiltins.py#L13
class Quitter(object):
    def __init__(self, name, eof):
        self.name = name
        self.eof = eof
    def __repr__(self):
        return 'Use %s() or %s to exit' % (self.name, self.eof)
    def __call__(self, code=None):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper is closed.
        try:
            sys.stdin.close()        # <== here stdin is closed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! to prevent a CTRL+C interruption?
        except:
            pass
        raise SystemExit(code)


https://github.com/python/cpython/blob/d6892c2b9263b39ea1c7905667942914b6a24b2c/Lib/_sitebuiltins.py
import sys

class Quitter(object):
    def __init__(self, name, eof):
        self.name = name
        self.eof = eof
    def __repr__(self):
        return 'Use %s() or %s to exit' % (self.name, self.eof)
    def __call__(self, code=None):
        # Shells like IDLE catch the SystemExit, but listen when their
        # stdin wrapper is closed.
        try:
            sys.stdin.close()
        except:
            pass
        raise SystemExit(code)

https://github.com/python/cpython/blob/add16f1a5e4013f97d33cc677dc008e8199f5b11/Lib/site.py#L401
    builtins.quit = _sitebuiltins.Quitter('quit', eof)
    builtins.exit = _sitebuiltins.Quitter('exit', eof)

For the moment I can't figure out if the "bug" is something intentional for the python devs or an unwanted side effect that requires a bug report.

=============Solution==========
At the moment we will monkey-path exit() and quit() or maybe only the Quitter() class that closes stdin for an unknown reason.