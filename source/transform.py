import re
import sys
from collections import deque
import copy
from parse import *
class Transform:
	def __init__(self,rules):
		self.commands = [] #command name and args as tuple
		self.newNode = {}
		self.newlyAdded = {}
		self.handleDuplicates = {}
		self.transformedNodes = {}
		self.emtpyNodes = {}
		self.func = {
			'add_child_end': self.addC2End,
			'add_child_before': self.addCBefore,
			'add_child_begin': self.addC2Begin,
			'remove_child': self.removeC,
			'set_category': self.setCategory,
			'concatenate': self.concatenate,
			'set_root': self.setRoot,
			'replace_child': self.replaceChild,
			'add_child_after': self.addCAfter,
			'copy_original_from': self.copyOriginal,
			'set_head_word': self.setHeadWord,
			'replace_child_with_contents': self.replaceCwC,
			'copy_head_word_from': self.copyHead,
			'make_helper': self.makehelper,
			'transfer_children_after': self.transfer,
		}

		self.process(rules)
	def process(self,rules):
		for rule in rules:
			r,arg = rule.split('(')
			args = arg[:-1].split(',')
			self.commands.append((r,args))

	def transform(self,map,tr,currRuleId):
		#print self.transformedNodes
		global t
		t = tr
		self.newNode = {}
		self.newlyAdded = {}
		self.currRuleId = currRuleId
		for c in self.commands:
			#print t.tree , "Original"
			self.func[c[0]](map,c[1],t)
			#print t.tree , "transformed"
	def addC2End(self,map,args,t):
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = oldtcnode = self.getMapNode(map,int(args[1])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]

		if t.tree.has_key(tpnode): 
			t.tree[tpnode].append(tcnode)
		else: #newly added node has children
			t.tree[tpnode] = [tcnode]
		oldParent = None
		if t.parentOf.has_key(tcnode): #handling new added node
			oldParent = t.parentOf[tcnode]
			t.tree[oldParent].remove(tcnode)
			t.parentOf[tcnode] = tpnode
		else:
			t.parentOf[tcnode] = tpnode
	def addC2Begin(self,map,args,t):
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = oldtcnode = self.getMapNode(map,int(args[1])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]

		if t.tree.has_key(tpnode): 
			t.tree[tpnode].insert(0,tcnode)
		else: #newly added node has children
			t.tree[tpnode] = [tcnode]
		oldParent = None
		if t.parentOf.has_key(tcnode): #handling new added node
			oldParent = t.parentOf[tcnode]
			t.tree[oldParent].remove(tcnode)
			t.parentOf[tcnode] = tpnode
		else:
			t.parentOf[tcnode] = tpnode
	def addCBefore(self,map,args,t): 
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		tbnode = oldtbnode = self.getMapNode(map,int(args[1])) #node to replace
		tcnode = oldtcnode = self.getMapNode(map,int(args[2])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tbnode):
			tbnode = self.newNode[tbnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		pos = t.tree[tpnode].index(tbnode)
		t.tree[tpnode].insert(pos,tcnode)
		oldParent = None
		if t.parentOf.has_key(tcnode): #handling new added node
			oldParent = t.parentOf[tcnode]
			t.tree[oldParent].remove(tcnode)
			t.parentOf[tcnode] = tpnode
		else:
			t.parentOf[tcnode] = tpnode

	def addCAfter(self,map,args,t): 
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		tbnode = oldtbnode = self.getMapNode(map,int(args[1])) #node to replace
		tcnode = oldtcnode = self.getMapNode(map,int(args[2])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tbnode):
			tbnode = self.newNode[tbnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		pos = t.tree[tpnode].index(tbnode)+1
		t.tree[tpnode].insert(pos,tcnode)

		if t.parentOf.has_key(tcnode): #handling new added node
			oldParent = t.parentOf[tcnode]
			t.tree[oldParent].remove(tcnode)
			t.parentOf[tcnode] = tpnode
	def removeC(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = self.getMapNode(map,int(args[1])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		t.tree[tpnode].remove(tcnode)
		del t.parentOf[tcnode]
	def setCategory(self,map,args,t):
		p = int(args[0])
		cat = args[1]
		if map.has_key(p):
			tpnode = map[p]
			if not self.newNode.has_key(tpnode):
				newID = len(t.nodes)
				newID = self.replace(t,tpnode,newID)
				t.nodes[newID].name = t.nodes[newID].label = cat
				#print newID,t.nodes[newID].label
			else:
				tpnode = self.newNode[tpnode] 
				t.nodes[tpnode].name = t.nodes[tpnode].label = cat
		else:
			if not self.emptyNodes.has_key((p,self.currRuleId)):
				newID = len(t.nodes)
				t.nodes[newID] = TreeNode("ANY",newID)
				self.emptyNodes[(p,self.currRuleId)] = newID
			else:
				newID = self.emptyNodes[(p,self.currRuleId)]

			map[p] = newID
			self.newNode[newID] = newID
			self.newlyAdded[newID] = 1
			#print >> sys.stderr, "Adding a new node"
			t.nodes[newID].name = t.nodes[newID].label = cat

	def setHeadWord(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		if not self.newNode.has_key(tpnode):
			newID = len(t.nodes)
			newID = self.replace(t,tpnode,newID)
			t.nodes[newID].head = args[1]
		else:
			tpnode = self.newNode[tpnode]
			t.nodes[tpnode].head = args[1]
	def concatenate(self,map,args,t):
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = oldtcnode = self.getMapNode(map,int(args[1])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode): #this wouldnt happen
			tcnode = self.newNode[tcnode]
		for cID,c in enumerate(t.tree[tcnode]):
			t.tree[tpnode].append(c)
			t.parentOf[c] = tpnode
	def setRoot(self,map,args,t):
		tpnode = oldtpnode = self.getMapNode(map,int(args[0])) #parent
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if t.parentOf.has_key(tpnode):  #handling case where root is created
			par = t.parentOf[tpnode]
			if par == 0: return
			t.tree[par].remove(tpnode)  #remove link to parent
		else:	
			t.tree[tpnode] = [] #children = null for newly created node
		if len(t.tree[0]) >0:
			if t.parentOf.has_key(t.tree[0][0]):
				del t.parentOf[t.tree[0][0]]
		t.tree[0] = [tpnode] #make it the root
		t.parentOf[tpnode] = 0
	def getMapNode(self,map,node):
		if map.has_key(node):
			return map[node]
		else:
			if not self.emptyNodes.has_key((node,self.currRuleId)):
				newID = len(t.nodes)
				t.nodes[newID] = TreeNode("ANY",newID)
				self.emptyNodes[(node,self.currRuleId)] = newID
			else:
				newID = self.emptyNodes[(node,self.currRuleId)]
			map[node] = newID
			self.newNode[newID] = newID
			self.newlyAdded[newID] = 1
			return newID
	def replaceChild(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		tanode = self.getMapNode(map,int(args[1])) #node to replace
		tbnode = self.getMapNode(map,int(args[2])) #node replacement
		#print tpnode,tanode,tbnode
		if self.newNode.has_key(tpnode): tpnode =self.newNode[tpnode]
		if self.newNode.has_key(tanode): tanode =self.newNode[tanode]
		if self.newNode.has_key(tbnode): tbnode =self.newNode[tbnode]
		
		bpar = None
		if t.parentOf.has_key(tbnode): #handling newly added node
			bpar = t.parentOf[tbnode] #unlink b
			t.tree[bpar].remove(tbnode)
		pos = t.tree[tpnode].index(tanode) #unlink 
		t.tree[tpnode][pos] = tbnode 
		t.parentOf[tbnode] = tpnode
		del t.parentOf[tanode]
	def copyOriginal(self,map,args,t):
		do_nothing = 1
	def copyHead(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = self.getMapNode(map,int(args[1])) #node to replace
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		t.nodes[tpnode].head = t.nodes[tcnode].head
		if not self.newlyAdded.has_key(tpnode):
			self.replace(t,tpnode,len(t.nodes))
	def makehelper(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		t.nodes[tpnode].role = "HELP"
		if not self.newlyAdded.has_key(tpnode):
			self.replace(t,tpnode,len(t.nodes))
	def replaceCwC(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = self.getMapNode(map,int(args[1])) #node to replace
		trnode = self.getMapNode(map,int(args[2])) #node replacement
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		if self.newNode.has_key(trnode):
			trnode = self.newNode[trnode]
		tcPos = t.tree[tpnode].index(tcnode)
		newContent = copy.deepcopy(t.tree[tpnode][0:tcPos])
		for ID,content in enumerate(t.tree[trnode]):
			newContent.append(content)
			t.parentOf[content] = tpnode
		for ID,content in enumerate(t.tree[tpnode][tcPos+1:]):
			newContent.append(content)
		t.tree[tpnode] = copy.deepcopy(newContent)
		del t.parentOf[tcnode]
	def transfer(self,map,args,t):
		tpnode = self.getMapNode(map,int(args[0])) #parent
		tcnode = self.getMapNode(map,int(args[1])) #node to replace
		trnode = self.getMapNode(map,int(args[2])) #node replacement
		if self.newNode.has_key(tpnode):
			tpnode = self.newNode[tpnode]
		if self.newNode.has_key(tcnode):
			tcnode = self.newNode[tcnode]
		if self.newNode.has_key(trnode):
			trnode = self.newNode[trnode]
		tcPos = t.tree[tpnode].index(tcnode)
		rPar = None
		if t.parentOf.has_key(trnode):
			rPar = t.parentOf[trnode]
			t.tree[rPar].remove(trnode)			
		t.tree[tpnode].insert(tcPos+1,trnode)
		t.parentOf[trnode] = tpnode
		
	def replace(self,t,node,id,cat=""):
		if self.transformedNodes.has_key((node,self.currRuleId)):
			id = self.transformedNodes[(node,self.currRuleId)]
			self.newNode[node] = id
			self.newlyAdded[id] = 1
		else:
			self.newNode[node] = id
			self.newlyAdded[id] = 1
			t.nodes[id] = TreeNode(cat,id)
			t.nodes[id].copyProp(t.nodes[node])

		self.transformedNodes[(node,self.currRuleId)] = id
		p = None
		
		if t.parentOf.has_key(node):
			p = t.parentOf[node]
			nI = t.tree[p].index(node)
			t.tree[p][nI] = id
		#print id,t.nodes[id].name

		#print t.tree,node,p
		if t.tree.has_key(node):
			for c in t.tree[node]:
				t.parentOf[c] = id
			t.tree[id] = copy.deepcopy(t.tree[node])
			del t.tree[node]
		if not p == None:
			t.parentOf[id] = p
		return id
