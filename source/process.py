import re
import sys
from main import *
from parse import *
from transform import *
from rule import *


if __name__ == "__main__":
    if len(sys.argv) > 3:
        rulefile = sys.argv[1]
        treein = sys.argv[2]
        treeout = sys.argv[3]
        rObj = Rules(rulefile)
        tObj = Main(treein,treeout,rObj)
        #tObj.convert(rObj)
    else:
        print >> sys.stderr , "usage:",sys.argv[0],"rulefile treein treeout"
