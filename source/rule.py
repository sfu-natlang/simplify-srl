import re
#import sys
#from collections import deque
from transform import *

class Node:
    """An abstract treenode in the LHS of a rule"""
    def __init__(self,id,cat):
        """
        Creates a node with blank starting enforcements/restrictions
        Arguments:
            id  - Reference number in Rule tree
            cat - Category/POS
        """
        self.cat = cat          # Enforces category/POS
        self.id = id            # Number that corresponds to Rule.tree
        self.verbType = None    # "HELP" or "MAIN" via addProperty
        self.notPos = None      # Restricts category/POS via setNotCategory
        self.childOrder = []    # Enforces order of children via fixChildOrder
        self.childPos = []      # Enforces POS of children via fixChildPos
        self.head = None        # Enforces head word via fixHead
        self.numChildren = None # Enforces number of children via setNumChildren

class Rule:
    """Holds the LHS of one rule"""
    def __init__(self,rules):
        """
        Creates a tree by applying a list of operations
        Arguments:
            rules - list of operations to build tree
                    Not to be confused with Rules which is a list of Rule objects
        """
        self.tree = {}         # Chart of tree IDs
        self.nodes = {}        # Maps each ID to a Node
        self.parentOf = {}     # parentOf[x] == x's parent in tree
        self.func = None
        self.definefunc()
        self.head = None       # Root of tree
        self.nodesvisited = {} # Maps all nodes to 1?
        # Apply all of the operations in "rules"
        for rule in rules:
            r,arg = rule.split('(')
            args = arg[:-1].split(',')
            self.func[r](args,r)
        # Creates wildcard Node for any missing referenced nodes in tree
        for h in self.nodesvisited:
            if not self.nodes.has_key(h):
                self.nodes[h] = Node(h,"ANY")
        # Define the tree's root
        for n in self.nodes:
            if not self.parentOf.has_key(n):
                self.head = n

    def definefunc(self):
        """Maps Vickrey's operations to Ravi's functions"""
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
        """Vickrey's category"""
        self.nodes[int(args[0])] = Node(args[0],args[1])
        self.nodesvisited[int(args[0])] = 1

    def add2tree(self,args,r):
        """Vickrey's child"""
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
        """Vickrey's is_main_verb and is_helper_verb"""
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
        """Vickrey's child_order"""
        p = int(args[0])
        self.nodesvisited[p] = 1
        o = []
        for a in args[1:]:
            o.append(int(a))
        self.nodes[p].childOrder.append(o)

    def fixChildPos(self,args,r):
        """Vickrey's child_num"""
        p = int(args[0])
        c = int(args[1])
        self.nodesvisited[p] = 1
        self.nodesvisited[c] = 1
        self.nodes[p].childPos.append((c,args[2]))

    def fixHead(self,args,r):
        """Vickrey's head_word"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].head = args[1]

    def sibDist(self,args,r):
        """Vickrey's sibling_dist"""
        pass

    def setNotCategory(self,args,r):
        """Vickrey's not_category"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"ANY")
        self.nodes[n].notPos = args[1]

    def setVerb(self,args,r):
        """Vickrey's is_verb"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"VERB")

    def setVerbCategory(self,args,r):
        """Vickrey's basic_verb_category"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].cat = args[1]

    def setHeadChild(self,args,r):
        """Vickrey's is_head_child"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        p = self.parentOf[n]
        if not self.nodes.has_key(n):
            self.nodes[n] = Node(n,"ANY")
        self.nodes[p].headChild = n

    def setNumChildren(self,args,r):
        """Vickrey's num_children"""
        n = int(args[0])
        self.nodesvisited[n] = 1
        self.nodes[n].numChildren = int(args[1])

    def typedSentence(self,args,r):
        """Vickrey's is_typed_sentence"""
        pass #set category to S

class Rules:
    """Holds a list of all the rules from transformrules.txt"""
    def __init__(self,rulefile):
        """
        Reads in rules as a list of (Rule, Transform, string) tuples
        Arguments:
            rulefile - string with filename of rulefile
        """
        self.rules = [] # List of (LHS, RHS, rawtext)
        for line in open(rulefile,"r"):
            if re.search('^\/\/',line[:-1]) is None and not line[:-1] == "":
                l,r,c = line[:-1].split(':')
                lhs = Rule(l.split(';'))
                rhs = Transform(r.split(';'))
                self.rules.append((lhs,rhs,c))
