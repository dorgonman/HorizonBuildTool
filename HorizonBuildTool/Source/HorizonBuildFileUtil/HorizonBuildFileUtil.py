from collections import defaultdict
import codecs
import os
import warnings
from itertools import count
import hashlib
import csv
import shutil
import sys

from contextlib import contextmanager


class HorizonBuildFileUtil(object):
    """description of class"""
    def __init__(self):
        print('HorizonBuildFileUtil.__init__')

    @staticmethod
    def EnsureDir(f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    @staticmethod
    def CreateDir(d):
        if not os.path.exists(d):
            os.makedirs(d)
    @staticmethod
    def ToBool(value):
        """
           Converts 'something' to boolean. Raises exception for invalid formats
               Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
               Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
        """
        if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
        if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
        raise Exception('Invalid value for boolean conversion: ' + str(value))
    @staticmethod
    def LogInfo(reportFile, info):
        reportFile.write(info)
        try:
          print(info)
        except: # catch *all* exceptions
          e = sys.exc_info()[0]
          print(e)


    @contextmanager
    def pushd(newDir):
        previousDir = os.getcwd()
        os.chdir(newDir)
        yield
        os.chdir(previousDir)