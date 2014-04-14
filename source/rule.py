import re
import sys
from collections import deque
from transform import *

class Node:
    def __init__(self,id,cat):    
        self.cat = cat
        self.id = id
        self.verbType = None
        self.notPos = None
        self.childOrder = []
        self.childPos = []
        self.head = None
        self.numChildren = None

class Rule:
    def __init__(self,rules):
        self.tree = {}
        self.nodes = {}
        self.parentOf = {}
        self.func = None
        self.definefunc()
        self.head = None
        self.nodesvisited = {}
        for rule in rules:
            r,arg = rule.split('(')
            args = arg[:-1].split(',')
            self.func[r](args,r)
        for h in self.nodesvisited.keys():
            if not self.nodes.has_key(h):
                self.nodes[h] = Node(h,"ANY")
        for n in self.nodes.keys():
            if not self.parentOf.has_key(n):
                self.head = n

    def definefunc(self):
        self.func = {
            'category' : self.addNode,
            'child': self.add2tree,
            'is_main_verb': self.addProperty,
            'is_helper_verb': self.addProperty,
            'child_order': self.fixChildOrder,
            'child_num': self.fixChildPos,
            'head_word': self.fixHead,
            'sibling_dist': self.sibDist,
            'not_category': self.setNotCategory,
            'is_verb': self.setVerb,
            'basic_verb_category': self.setVerbCategory,
            'is_head_child': self.setHeadChild,
            'num_children': self.setNumChildren,
            'is_typed_sentence': self.typedSentence,
        }

    def addNode(self,args,r):
        self.nodes[int(args[0])] = Node(args[0],args[1])
        self.nodesvisited[int(args[0])] = 1
    
    def add2tree(self,args,r):
        p = int(args[0])
        c = int(args[1])
        self.nodesvisited[p] = 1
        self.nodesvisited[c] = 1
        self.parentOf[c] = p 
        if self.tree.has_key(p):
            self.tree[p].append(c)
        else:
            self.tree[p] = [c]

    def addProperty(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        type = "HELP"
        if re.search('main',r) is not None:
            type = "MAIN"
        v = Node(n,type)
        if not self.nodes.has_key(n):
            self.nodes[n] = v
        self.nodes[n].verbType = type
        
    def fixChildOrder(self,args,r):
        p = int(args[0])
        self.nodesvisited[p] = 1
        o = []
        for a in args[1:]:
            o.append(int(a))
        self.nodes[p].childOrder.append(o)
    def fixChildPos(self,args,r):
        p = int(args[0])
        c = int(args[1])
        self.nodesvisited[p] = 1
        self.nodesvisited[c] = 1
        self.nodes[p].childPos.append((c,args[2]))

    def fixHead(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].head = args[1]

    def sibDist(self,args,r):
        do_nothing = 1 

    def setNotCategory(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"ANY")
        self.nodes[n].notPos = args[1]

    def setVerb(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"VERB")

    def setVerbCategory(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].cat = args[1]

    def setHeadChild(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        p = self.parentOf[n]
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"ANY")
        self.nodes[p].headChild = n

    def setNumChildren(self,args,r):
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].numChildren = int(args[1])

    def typedSentence(self,args,r):
        do_nothing = 1 #set category to S

class Rules:
    def __init__(self,rulefile):
        self.rPtr = open(rulefile,"r")
        self.rules = []
        #count = 0
        for line in self.rPtr:
            if re.search('^\/\/',line[:-1]) is None and not line[:-1] == "":
                #print line[:-1]
                l,r,c = line[:-1].split(':')
                lhs = Rule(l.split(';'))
                rhs = Transform(r.split(';'))
                self.rules.append((lhs,rhs,line[:-1]))
                #count += 1
                #if count == 24: break
