import re
import sys
import copy
from collections import deque

class TreeNode:
    def __init__(self,f,id):
        self.id = id
        self.name = re.sub(r'[(|)]',r'',f)
        self.prop = None
        self.label = None
        self.origname = f
        self.role = None
        self.head = None #define head
        new = re.sub(r'=',r'-',self.name)
        if re.search('-',new) is not None and re.search('^-',new) is None:
            self.label = new.split('-')[0]
            self.prop = "-".join(new.split('-')[1:])
        else:
            self.label = self.name
        if self.label.startswith("V"):
            self.role = "MAIN"

    def copyProp(self,node):
        if self.name == "": self.name = node.name
        if self.prop == None: self.prop = node.prop
        if self.label == "": self.label = node.label
        if self.head == None: self.head = node.head
        if self.role == None: self.role = node.role
        self.id = node.id

class Tree:
    def __init__(self,parse):
        self.chart = {}
        self.tree = {} #transformed in process
        self.origTree = {} #untransformed
        self.nodes = {}
        self.parentOf = {}
        self.treeRulesMap = {}
        self.updatedChart = {}
        self.helpkeys = {"was":1,"is":1,"had":1, "are":1, "were":1, "has":1, "be":1,"have":1,"do":1,"get":1} #headword
        self.read(parse)
        self.updatedChart = copy.deepcopy(self.chart)

    def read(self,parse):
        stack = []
        help = []
        id = 0
        parse = re.sub(r'\s+',r' ',parse)
        print parse
        for f in parse.split(' '):
            if re.search('^\(',f) is not None:
                n = TreeNode(f,id)
                id += 1
                if len(stack) > 0:
                    h = stack[-1]
                    if self.chart.has_key(h.id):
                        self.chart[h.id][0].append(n.id)
                    else:
                        self.chart[h.id] = [] # stack for every cell in chart
                        self.chart[h.id].append([n.id]) # 0th element in stack
                    self.parentOf[n.id] = h.id
                stack.append(n)
                self.nodes[n.id] = n
            elif re.search('\)$',f) is not None:
                if re.search('^\)',f) is not None:
                    for cIndex in range(0,len(f)):
                        h = stack.pop()
                else:
                    n = TreeNode(f,id)
                    id += 1
                    h = stack[-1]
                    if self.chart.has_key(h.id):
                        self.chart[h.id][0].append(n.id)
                    else:
                        self.chart[h.id] = []
                        self.chart[h.id].append([n.id])
                    h.head = n.name
                    if self.helpkeys.has_key(n.name): h.head = "be"
                    if self.helpkeys.has_key(n.name):
                        help.append((h.id,n.id))
                    self.nodes[n.id] = n
                    self.parentOf[n.id] = h.id
                    for cIndex in range(f.index(')'),len(f)):
                        h = stack.pop()
        for h in help:
            if self.parentOf.has_key(h[0]):
                p = self.parentOf[h[0]]
                for cID in self.chart[p][0]:
                    c = self.nodes[cID]
                    if not c.id == h[0] and c.label == "VP":
                        self.nodes[h[1]].role = "HELP"
                        self.nodes[h[0]].role = "HELP"

    def updateChart(self,rulesUsed):
        #self.newParse()
        if self.hasCycle(): 
            print "Yes"
            return
        cQ = deque([0])
        while len(cQ) > 0:
            h = cQ.popleft()
            if re.search('^VB',self.nodes[h].name) is not None:
                string = self.nodes[h].head
                count = 1
                gp = h
                while self.parentOf.has_key(gp):
                    string = self.nodes[self.parentOf[gp]].name +"->"+ string
                    gp = self.parentOf[gp]
                    count += 1
                if count == 4:
                    #fPtr.write(self.nodes[h].head)
                    if self.treeRulesMap.has_key((self.nodes[h].head,self.nodes[h].id)):
                        for rID in rulesUsed:
                            if rID not in self.treeRulesMap[(self.nodes[h].head,self.nodes[h].id)]:
                                self.treeRulesMap[(self.nodes[h].head,self.nodes[h].id)].append(rID)
                    else:
                        self.treeRulesMap[(self.nodes[h].head,self.nodes[h].id)] = copy.deepcopy(rulesUsed)
                        #fPtr.write("\t"+ str(self.nodes[h].id) + "\t"+str(rulesUsed)[1:-1] +"\n")
            if self.tree.has_key(h):
                newC = copy.deepcopy(self.tree[h])
                try:
                    self.updatedChart[h].index(newC)
                except:
                    if self.updatedChart.has_key(h):
                        self.updatedChart[h].append(newC)
                    else:
                        self.updatedChart[h] = [newC]
                for c in newC:
                    cQ.append(c)

    def compare(self,newC,h):
        if not self.updatedChart.has_key(h):
            return newC
        for item in self.updatedChart[h]:
            for iID,iI in enumerate(item):
                for nID,nI in enumerate(newC):
                    if nI == iI: continue
                    if self.propCompare(self.nodes[iI],self.nodes[nI]): #category compare
                        if not self.updatedChart.has_key(iI) or not self.tree.has_key(nI):
                            newC[nID] = iI
                        else:
                            if self.compareChildren(self.tree[nI],self.updatedChart[iI]):
                                newC[nID] = iI
        return newC

    def compareChildren(self,tList,cList):
        for cItems in cList:
            count = 0
            for cItemID,cItem in enumerate(cItems):
                for tItemID,tItem in enumerate(tList):
                    if tItem == cItem:
                        count += 1
                    if self.propCompare(self.nodes[cItem],self.nodes[tItem]):
                        count +=1
            if count >= min(len(cItems),len(tList)):
                return True
        #print self.chart

    def hasCycle(self):
        vis = {}
        cQ = deque([0])
        while len(cQ) > 0:
            h = cQ.popleft()
            if vis.has_key(h): return True
            vis[h] = 1
            if self.tree.has_key(h):
                for c in self.tree[h]:
                    cQ.append(c)
        return False

    def newParse(self):
        s1 = [] #node stack
        s2 = [({},-1,0,{})] #parse forest stack
        parses = []
        parents = []
        while len(s2) > 0:
            p,c,h,pH = copy.deepcopy(s2.pop())
            if not c == -1:
                p[h] = c
                for cc in c:
                    s1.append(cc)
                    pH[cc] = h
            else:
                s1 = [h]
            while len(s1) > 0:
                h = s1.pop()
                if self.chart.has_key(h):
                    if len(self.chart[h]) == 1:
                        p[h] = self.chart[h][0]
                        for c in self.chart[h][0]:
                            s1.append(c)
                            pH[c] = h
                    else:
                        for c in self.chart[h]:
                            s2.append((p,c,h,pH))
                        p,c,h,pH = copy.deepcopy(s2.pop())
                        p[h] = c
                        for cc in c :
                            s1.append(cc)
                            pH[cc] = h
            same = {}
            self.treeCompare(p,self.tree,0,0,same)
            print same
                
    def treeCompare(self,p,t,phead,thead,same):
        if not p.has_key(phead) or not t.has_key(thead):
            if phead == thead or self.propCompare(self.nodes[phead],self.nodes[thead]):
                same[thead] = phead
                print thead,phead,"same"
                return True
            else:
                return False
        if len(p[phead]) == len(t[thead]):    
            sameCount = 0
            for cID,pc in enumerate(p[phead]):
                tc = t[thead][cID]
                print "comparing child",phead,thead,pc,tc
                if pc == tc:
                    sameCount += 1
                elif self.treeCompare(p,t,pc,tc,same):
                    print "same",pc,tc
                    same[tc] = pc
                    sameCount += 1
            if sameCount == len(p[phead]):
                if phead == thead:
                    return True
                if self.propCompare(self.nodes[phead],self.nodes[thead]):
                    same[thead] = phead
                    return True
        else:
            for cID,pc in enumerate(p[phead]):
                for tID,tc in enumerate(t[thead]):
                    if pc == tc:
                        same[pc] = tc
                    elif self.treeCompare(p,t,pc,tc,same):
                        print "same",pc,tc
                        same[tc] = pc

    def propCompare(self,n1,n2):
        flag = True
        if not n1.name == n2.name: flag = False
        if not n1.prop == n2.prop: flag = False
        if not n1.label == n2.label: flag = False
        if not n1.head == n2.head: flag = False
        if not n1.role == n2.role: flag = False
        return flag
