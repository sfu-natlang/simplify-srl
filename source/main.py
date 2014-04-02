import re
import sys
from collections import deque
import copy
from parse import *
from transform import *
from rule import *
import gc
import signal

def signal_handler(signum, frame):
    raise Exception("Timed out!")


class Main:
	def __init__(self,treein,treeout,rObj):
		self.iPtr = open(treein,"r")
		self.rObj = rObj
		self.out = open(treeout,"w")
		sentId = 0
		gc.enable()

		for parse in self.iPtr:
			sentId += 1
			t = Tree(parse[:-1])
			signal.signal(signal.SIGALRM, signal_handler)
			signal.alarm(1200)   # Ten seconds
			try:
				self.ruleMatch(t)
				self.out.write("sentence num:"+str(sentId)+"\n")
				self.out.write(str(t.treeRulesMap)+"\n")
				self.out.write("CHART\n"+str(t.updatedChart)+"\n")
				nodedict = {}
			        for node in t.nodes.keys():
                		        nodedict[node] = (t.nodes[node].id,t.nodes[node].name,
                        	        t.nodes[node].origname,t.nodes[node].label,
                                	t.nodes[node].role,t.nodes[node].head)
		                self.out.write("NODES\n"+str(nodedict)+"\n\n")
				#self.printSentences(t)
			except Exception, msg:
				self.out.write("sentence num:"+str(sentId)+"\nTimedOut\n\n")
				

		self.out.close
	def ruleMatch(self,t):
		#print t.chart
		for rID,fullrule in enumerate(self.rObj.rules):
			#if rID < 19 or rID > 20: continue
			#visited = {}  # visited nodes (treenodeId,rulenodeID,rID) = (flag,map)
			'''
			myChart = {
				0: [[1], [23]], 1: [[2, 10, 12, 15]], 2: [[3, 5]], 
				3: [[4]], 5: [[6, 8]], 6: [[7]], 8: [[9]], 10: [[11]], 
				12: [[13]], 13: [[14]], 15: [[16, 18]], 16: [[17]], 18: [[19, 21]], 
				19: [[20]], 21: [[22]], 23: [[10, 12, 24]], 24: [[16, 18, 2]]
			}
			print myChart
			(currTrees,currParents) = self.generateTrees(0,myChart,[{}],[{}])
			for c in currTrees:
				print c
			sys.exit(0)
			'''
			fullrule[1].transformedNodes = {}
			fullrule[1].emptyNodes = {}
	        	Is1 = [] #node stack
		        Is2 = deque([({},-1,0,{},[],{})]) #parse forest stack parse,children,head,parentOf,visited
			parseNum = 0
			del t.chart
			t.chart = copy.deepcopy(t.updatedChart)
			#print t.chart

		        while len(Is2) > 0:
				cycleFlag = False
        		        Ip,Ic,Ih,IpH,Is1,Iv = copy.deepcopy(Is2.popleft())
		                if not Ic == -1:
        		                Ip[Ih] = copy.deepcopy(Ic)
                		        for Icc in Ic:
                        		        Is1.append(Icc)
						IpH[Icc] = Ih
		                else:
        		                Is1 = [Ih]
	        	        while len(Is1) > 0:
        	        	        Ih = Is1.pop()
					if Iv.has_key(Ih):
						cycleFlag = True
						break
					Iv[Ih] = 1
	                	        if t.chart.has_key(Ih):
        	                	        if len(t.chart[Ih]) == 1:
                	                	        Ip[Ih] = copy.deepcopy(t.chart[Ih][0])
                        	                	for Ic in t.chart[Ih][0]:
	                        	                        Is1.append(Ic)
								IpH[Ic] = Ih
	        	                        else:
        	        	                        for Ic in t.chart[Ih]:
                	        	                        Is2.append((Ip,Ic,Ih,IpH,Is1,Iv))
                        		       	        Ip,Ic,Ih,IpH,Is1,Iv = copy.deepcopy(Is2.popleft())
                                        		Ip[Ih] = copy.deepcopy(Ic)
		                                        for Icc in Ic :   
        		                                        Is1.append(Icc)
								IpH[Icc] = Ih
				#print "length",len(Is2)
				if cycleFlag: continue
				parseNum+=1
				if parseNum > 300: break
				#print "In Parse",parseNum, rID
				#print t.chart
			
				#print parseNum, len(t.nodes),rID
				del t.origTree
				t.origTree = copy.deepcopy(Ip)
				#print "\n\n*******original", t.origTree
				tQ = deque([0])
				lhs = fullrule[0] #match
				rhs = fullrule[1] #transform
				while len(tQ) > 0:
					n = tQ.popleft()
					q1 = deque([n])
					q2 = deque([lhs.head])
					nodeMap = {}
					while len(q1) > 0:
						h1 = q1.popleft() #Tree
						h2 = q2.popleft() #rule
						#if visited.has_key((h1,h2,rID)):
						#	(flag,map) = visited[(h1,h2,rID)]
						#else:
						(flag,map) = self.compare(h1,h2,lhs,t)  #matching with current tree
						#visited[(h1,h2,rID)] = (flag,map)
						if flag:
							transform = 1
							nodeMap[h2] = h1
							for k in map.keys():
								q2.append(k)
								q1.append(map[k][1])
						else:
							transform = 0
							break
					if transform == 1:
						#print >>sys.stderr, "=============MATCHED RULE #",rID,"===============", h1
						#print "=============MATCHED RULE #",rID,"===============", h1
						#print >> sys.stderr, fullrule[2]
						#print fullrule[2]
						del t.tree
						del t.parentOf
						t.tree = copy.deepcopy(Ip)
						t.parentOf = copy.deepcopy(IpH)
						try:
							rhs.transform(nodeMap,t,rID)
							t.updateChart([rID])
						except: continue
						#print "transformed", t.tree
					if t.origTree.has_key(n):
						for c in t.origTree[n]:
							tQ.append(c)
				del tQ
				del Is1
			del Is2
		#print t.chart
	def printSentences(self,t):
		(currTrees,currParents) = self.iterateTrees(0,t.chart)
		for cID,curr in enumerate(currTrees):
			print self.printTree(t,curr,0,"",currParents[cID])
		#print t.chart
	def printTree(self,t,curr,head,sent,parentOf):
		if not curr.has_key(head): 
			#sent += " "+t.nodes[head].name +" "+str(head)
			if t.nodes[head].head == None:
				sent += " "+t.nodes[head].name 
			else:
				sent += " "+t.nodes[head].head 
			return sent
		else:
			for c in curr[head]:
				if not re.search('^USED',t.nodes[head].name):
					if re.search('^VB',t.nodes[head].name) is not None:
						string = t.nodes[head].head
						gp = head
						while parentOf.has_key(gp):
							string = t.nodes[parentOf[gp]].name +"->"+ string
							gp = parentOf[gp]
						self.out.write(string+"\n")
					sent = self.printTree(t,curr,c,sent,parentOf)
		return sent
	def iterateTrees(self,head,chart):
	        s1 = [] #node stack
	        s2 = deque([({},-1,head,{},[],{})]) #parse forest stack
		parses = []
		parents = []
	        while len(s2) > 0:
			cycleFlag = False
        	        p,c,h,pH,s1,v = copy.deepcopy(s2.popleft())
	                if not c == -1:
        	                p[h] = copy.deepcopy(c)
                	        for cc in c:
                        	        s1.append(cc)
					pH[cc] = h
	                else:
        	                s1 = [h]
	                while len(s1) > 0:
        	                h = s1.pop()
				if v.has_key(h): 
					cycleFlag = True
					break
				v[h] = 1
                	        if chart.has_key(h):
                        	        if len(chart[h]) == 1:
                                	        p[h] = copy.deepcopy(chart[h][0])
                                        	for c in chart[h][0]:
	                                                s1.append(c)
							pH[c] = h
        	                        else:
                	                        for c in chart[h]:
                        	                        s2.append((p,c,h,pH,s1,v))
                                	        p,c,h,pH,s1,v = copy.deepcopy(s2.popleft())
                                        	p[h] = copy.deepcopy(c)
	                                        for cc in c :   
        	                                        s1.append(cc)
							pH[cc] = h
			if cycleFlag: continue
				
			parses.append(p)
			parents.append(pH)
			if len(parses) > 300: break
		return (parses,parents)
				
	def generateTrees(self,head,chart,parses,parents):
		if not chart.has_key(head):
			return (parses,parents)
		if len(chart[head]) == 1:
			for pID,p in enumerate(parses):
				if len(p) == 0 or parents[pID].has_key(head):
					parses[pID][head] = chart[head][0] # assign children to head
					for c in chart[head][0]:	
						parents[pID][c] = head
			for c in chart[head][0]:
				(parses,parents) = self.generateTrees(c,chart,parses,parents)
			return (parses,parents)
		if len(chart[head]) > 1:
			currParses = copy.deepcopy(parses)
			Ids = []
			#print len(currParses), "before adding or node"
			#print "hit an or node", chart[head]

			for pID,p in enumerate(currParses):
				if len(p) == 0 or parents[pID].has_key(head):
					for orNode in chart[head]:
						newP = copy.deepcopy(p)
						newP[head] = orNode
						parses.append(newP)  #every possible parse
						newQ = copy.deepcopy(parents[pID])
						for c in orNode:
							newQ[c] = head
						parents.append(newQ)
					Ids.append(pID)
			for pID in Ids:
				del parses[pID] #removing original parse which has been duplicated
				del parents[pID]
			#print "after adding or node", len(parses)
			for orNode in chart[head]:
				for c in orNode:
					(parses,parents) = self.generateTrees(c,chart,parses,parents)
			return (parses,parents)
	def compare(self,tnode,rnode,rule,tree):
		if self.compareCategory(tnode,rnode,rule,tree):
			#print "Matched: tnode",tnode,tree.nodes[tnode].label,\
			#	"rnode:",rnode,rule.nodes[rnode].cat
			if not rule.tree.has_key(rnode):
				return (True,{})
			if not tree.origTree.has_key(tnode):
				return (False,{})
			tC = tree.origTree[tnode]
			#print "\tChildren are:",tC
			rt = {}
			matched = {}
			for rId,rsnode in enumerate(rule.tree[rnode]):
				for tsId,tsnode in enumerate(tC):
					if matched.has_key(tsnode): continue
					#print "\t\t\tComparing Children: tnode",tsnode,tree.nodes[tsnode].label,\
						#"rnode:",rsnode,rule.nodes[rsnode].cat
					if self.compareCategory(tsnode,rsnode,rule,tree):
						rt[rsnode] = (tsId,tsnode)
						matched[tsnode] = 1
						#print "\t\t\tFound a match"
						break
				if not len(rt) ==  rId +1:
					return (False,{})
			cOrderFlag = self.compareFixChildren(rnode,rule,rt)
			cPosFlag = self.compareFixChildPos(rnode,rule,rt)
			if cPosFlag and cOrderFlag:
				#print "\t\t\t************HEAD MATCHED**************"
				return (True,rt)	
			else:
				return (False,{})
		else:
			#print "Dint Match: tnode",tnode,tree.nodes[tnode].label,\
				#"rnode:",rnode,rule.nodes[rnode].cat
			return (False,{})
	def compareFixChildren(self,rnode,rule,rt):
		rC = rule.nodes[rnode].childOrder
		if len(rC) == 0: 
			#print "\t\t\t\tNo Order"
			return True
		else:

			for oId,order in enumerate(rC):
				#print "\t\t\t\tOrder Fixed: node1:",order[0],\
				rt[order[0]][0],"node2:",order[1],rt[order[1]][0]
				if rt[order[0]][0] > rt[order[1]][0]:
					return False
		return True
	def compareFixChildPos(self,rnode,rule,rt):
			r = rule.nodes[rnode]
			cPosFlag = True
			if len(r.childPos) > 0:
				for c in r.childPos:
					#print "\t\t\t\tChild Pos in rule:",c[1],"Tree:",rt[c[0]][0]
					if c[1] == ">=2":
						if rt[c[0]][0] >= 2:  #hardcoded >=2
							cPosFlag = True	
						else: 
							cPosFlag = False
							break
						
					elif rt[c[0]][0] == int(c[1]):
						cPosFlag = True
					else:
						cPosFlag = False
						break
			return cPosFlag
	def compareCategory(self,tnode,rnode,rule,tree):
		a = tree.nodes[tnode].label
		aR = tree.nodes[tnode].role
		aH = tree.nodes[tnode].head
		aN = None
		if tree.origTree.has_key(tnode):
			aN = len(tree.origTree[tnode])
		b = rule.nodes[rnode].cat
		bH = rule.nodes[rnode].head
		bN = rule.nodes[rnode].numChildren
		bNP = rule.nodes[rnode].notPos
		#print "Comparing: treeNode: ",a,tnode, "ruleNode:",b
		#print "ruleNode",rnode,b,bH,bN,bNP
		#print "ruleNode",tnode,a,aR,aH,aN

		#category
		catFlag = False
		if a == b: catFlag = True
		if b == "ANY": catFlag = True
		if b == "VERB": 
			if a.startswith("V"): catFlag =  True
			else: catFlag = False
		if b == "MAIN" or b=="HELP":
			if a.startswith("V") and aR==b:	catFlag = True
			else: catFlag = False
		#if b =="USED_TO" and a == "TO": return True
		if not bNP == None:
			if not bNP == a: catFlag = True
			else: catFlag = False
		if not bH == None:
			catFlag = False
			if aH == None:
				if tree.origTree.has_key(tnode): 
				     tempQ = deque(tree.origTree[tnode])
				     while len(tempQ) > 0:
					c = tempQ.popleft()
					if tree.nodes[c].head == bH:
						catFlag = True	
						break
					if tree.origTree.has_key(c):
						for CID,C in enumerate(tree.origTree[c]):
							tempQ.append(C)
			else:
				if aH == bH:	catFlag = True
				else: catFlag = False
		if not bN == None:
			if bN == aN: catFlag = True
			else: catFlag = False

		return catFlag
	
