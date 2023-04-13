TODO: send to ricky


# to debug python - do this: (like javascript debugger;)
#        import pdb
#        pdb.set_trace()

# term pronounciations:
# ---------------------
# too-puhl - tuple
# sigh-thon - cython (c python thing)

# standards:
# PEAK = Python Enterprise App Kit (http://peak.telecommunity.com/DevCenter/FrontPage)
# PEP = https://www.python.org/dev/peps/ - #s = standards, pep8 = source style

# packaging:
easy_install    -> egg
    # about egg:
    easy_install /my_downloads/OtherPackage-3.2.1-py2.3.egg # (like package mgr)
    # ^^^^^^^^^^ - legacy old, etc.
disttools       -> wheels (compressed, binary)
setuptools      -> pip (contains wheels)

# ---

# installs library as a developer in my own code base
python3 setup.py develop # (setup.py is a PEP standard file name)
                           (PEP standard would look for setup.py in PIP)

# installs library into site packages (system global):
python3 setup.py install

# to use installed module:
python3 -m x_browse
#        ^ module argument, x_browse = module
# can use pip as module for example

# setuptools stuff: https://packaging.python.org/tutorials/packaging-projects/


# scaffolding:
repository folder (this is like root in git)
    - module (this is what makes python treat as module)
             (once it has an __init__.py)

             __init__.py (can be empty)
             setup.py (PEP standard filename)
                setuptools
                setup(
                    name="x_browse", # (has to match module dir name)
                    packages=find_packages() # makes wheels and eggs on disk
                                             # affords us to not sweat relative pathing
                )
        # does nothing until python3 setup.py is called (develop|[install])

        __main__.py # allows you to use -m for python3 arg
        # - if using -m arg will run headless, and assume __name__=__main__ 
        # __name__ = what file you are in

# from .controller import BrowseController
#      ^ == pwd() 
# if in /foo/bar/baz --- . = /foo/bar/baz 

# from {module_name}.controller import BrowseController
#      ^ == pwd() 
# if in /foo/bar/baz --- . = /foo/bar/baz          

# order of import resolution
# 1 - local folder
# 2 - local library module
# 3 - site library module
# read://https_chrisyeh96.github.io/?url=https%3A%2F%2Fchrisyeh96.github.io%2F2017%2F08%2F08%2Fdefinitive-guide-python-imports.html


# if moving need to reinstall with python3 setup.py develop - because it needs to

# monkey patch = you can do whatever the hell you want :) 
# e.g. importing a module_a inside another module_b - if module_b changes module_a, 
# anything that also imports module_b now module_a's version of that, is module_b version
# this override is called monkeypatching
# no protection of any code at all - you can do what you want
# to override _ you can in monkeypatch approach

# to protect you simply use convention of _ prefix.
# we should not use __ for our own stuff - that's sacred shit for python

# package = outer module 
# module = inner module of outer module 

# basic definitions from (order import resolution):

module: any *.py file. Its name is the file name.
built-in module: a “module” (written in C) that is compiled into the Python interpreter, and therefore does not have a *.py file.
package: any folder containing a file named __init__.py in it. Its name is the name of the folder.
in Python 3.3 and above, any folder (even without a __init__.py file) is considered a package
object: in Python, almost everything is an object - functions, classes, variables, etc.

automobiles
    _brand: chevy
    .car
        .chevy_equinox 
            __main__.py <-- 
            automobiles._brand = 'ford' <- fail - protected

automobiles.car.chevy_equinox 

import automobiles
# grabs car, chevy_equinox also 

chevy_equinox = automobiles.car.chevy_equinox 
# only my chevy chevy_equinox

# to hide egg info - go to settings | workspace | files.exclude - add pattern:
# **/*.egg-info 
# also consider removing **/__pycache__

# requirements.txt in main dir will let you define dependencies
# google pip {package} - will find relevant packages
# https://pypi.org/ - search here for packages
# e.g. 
# PyYAML==5.4.1 
# == - pin to version   ~=5 == 5.4.1 (latest v5)  >=5 (5.>) <= ^=

# then to get the stuff from requirements:
# pip3 install -r requirements.txt

# if you add things to requirements.txt after you initially run it,
# you need to run it again.. pip3 install -r requirements.txt

# absolute path from current:
import os
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "2091/data.txt"
abs_file_path = os.path.join(script_dir, rel_path)

# if at first you try to pip install something, with just a name without
# py starting it, try again pip install py(the thing)

# pip3 uninstall (package):
PS B:\Dropbox\P\git\x_browse\x_browse> pip3 uninstall x_browse
Found existing installation: x-browse 0.0.0
Uninstalling x-browse-0.0.0:
  Would remove:
    c:\python39\lib\site-packages\x-browse.egg-link
Proceed (y/n)?

-- site packages is there!

# if you remove a thing, and it can't resolve, make sure you:
# python3 setup.py develop # again!


# enum-like:
import collections

Person = collections.namedtuple('Person', 'name age gender')

print 'Type of Person:', type(Person)

bob = Person(name='Bob', age=30, gender='male')
print '\nRepresentation:', bob

See https://docs.python.org/3/library/exceptions.html for exception types

# note - if you make changes to code, after you do the setup.py stuff
# you do NOT have to rerun setup.py - as long as the directories in filesys
# are the same

# to look inside anything, you can use dir(the_thing) - it will show you all 
# the attributes and methods (aka functions)

# to find out what type a thing is, use type(the_thing)

# @ = decorator - they go above the methods 
# @staticmethod
# The staticmethod decorator modifies a method function so that it does not use the self variable. The method function will not have access to a specific instance of the class.
# For an example of a static method, see the section called “Static Methods and Class Method”.
# 
# @classmethod
# The classmethod decorator modifies a method function so that it receives the class object as the first parameter instead of an instance of the class. This method function wil have access to the class object itself.
#
# a decorator is any function that returns a function
# https://www.saltycrane.com/blog/2010/03/simple-python-decorator-examples/

def automobile(func, y, z):

    def chevy(func):
        my_func = func(y, z)
        return my_func
   
    return chevy

@automobile

from functools import wraps

def mydecorator(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        print "Before decorated function"
        r = f(*args, **kwargs)
        print "After decorated function"
        return r
    return wrapped

@mydecorator
def myfunc(myarg):
    print "my function", myarg
    return "return value"

r = myfunc('asdf')
print r
Before decorated function
my function asdf
After decorated function
return value

# array = list = array (interchangable)

# if you are attempting to access something with dot (.) and it doesn't to seem 
# to work but you think it should, try the thing with ['thing']. so:
# os.environ.path = None/fail 
# os.environ.PATH = None/fail
# HOWEVER! *dramatic finger waving* 
# os.environ['PATH'] = Winner