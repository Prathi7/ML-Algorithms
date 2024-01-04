from ast import keyword
import math
import bisect
from typing import Any, List, Optional, Tuple, Union, Dict, Generic, TypeVar, cast, NewType
from py_btrees.disk import DISK, Address
from py_btrees.btree_node import BTreeNode, KT, VT, get_node

"""
----------------------- Starter code for your B-Tree -----------------------

Helpful Tips (You will need these):
1. Your tree should be composed of BTreeNode objects, where each node has:
    - the disk block address of its parent node
    - the disk block addresses of its children nodes (if non-leaf)
    - the data items inside (if leaf)
    - a flag indicating whether it is a leaf

------------- THE ONLY DATA STORED IN THE `BTree` OBJECT SHOULD BE THE `M` & `L` VALUES AND THE ADDRESS OF THE ROOT NODE -------------
-------------              THIS IS BECAUSE THE POINT IS TO STORE THE ENTIRE TREE ON DISK AT ALL TIMES                    -------------

2. Create helper methods:
    - get a node's parent with DISK.read(parent_address)
    - get a node's children with DISK.read(child_address)
    - write a node back to disk with DISK.write(self)
    - check the health of your tree (makes debugging a piece of cake)
        - go through the entire tree recursively and check that children point to their parents, etc.
        - now call this method after every insertion in your testing and you will find out where things are going wrong
3. Don't fall for these common bugs:
    - Forgetting to update a node's parent address when its parent splits
        - Remember that when a node splits, some of its children no longer have the same parent
    - Forgetting that the leaf and the root are edge cases
    - FORGETTING TO WRITE BACK TO THE DISK AFTER MODIFYING / CREATING A NODE
    - Forgetting to test odd / even M values
    - Forgetting to update the KEYS of a node who just gained a child
    - Forgetting to redistribute keys or children of a node who just split
    - Nesting nodes inside of each other instead of using disk addresses to reference them
        - This may seem to work but will fail our grader's stress tests
4. USE THE DEBUGGER
5. USE ASSERT STATEMENTS AS MUCH AS POSSIBLE
    - e.g. `assert node.parent != None or node == self.root` <- if this fails, something is very wrong

--------------------------- BEST OF LUCK ---------------------------
"""

# Complete both the find and insert methods to earn full credit
class BTree:
    def __init__(self, M: int, L: int):
        """
        Initialize a new BTree.
        You do not need to edit this method, nor should you.
        """
        self.root_addr: Address = DISK.new() # Remember, this is the ADDRESS of the root node
        # DO NOT RENAME THE ROOT MEMBER -- LEAVE IT AS self.root_addr
        DISK.write(self.root_addr, BTreeNode(self.root_addr, None, None, True))
        self.M = M # M will fall in the range 2 to 99999
        self.L = L # L will fall in the range 1 to 99999

    def insert(self, key: KT, value: VT) -> None:
        """
        Insert the key-value pair into your tree.
        It will probably be useful to have an internal
        _find_node() method that searches for the node
        that should be our parent (or finds the leaf
        if the key is already present).

        Overwrite old values if the key exists in the BTree.

        Make sure to write back all changes to the disk!
        """
        node = get_node(self.root_addr)
        node = self.find_node(key,node)

       

        if self.find(key) != None: # Key exists - overwrite   
            assert node.is_leaf
            idx = node.find_idx(key)
            node.data[idx] = value
            node.write_back()
        else: # key does not exist - insert
            assert node.is_leaf
            node.insert_data(key,value) 
            if len(node.keys) <= self.L: # if leaf is not full, ok
                node.write_back()
                return
            else:
                self.split(node)
        return

    def split(self, node):     
        half=len(node.keys)//2
        new_key=node.keys[half]

        if node.parent_addr == None: # if leaf has no parent, means leaf itself is root 
            
            new_root =  BTreeNode(DISK.new(),None , None, is_leaf= False)
            new_root.keys = [new_key]
            new_leaf = BTreeNode(DISK.new(),new_root.my_addr,index_in_parent = 1, is_leaf=True)
            
            node.parent_addr = new_root.my_addr
            node.index_in_parent = 0
            new_root.children_addrs = [node.my_addr,new_leaf.my_addr]

            self.root_addr = new_root.my_addr #important

            new_leaf.keys = node.keys[half:]
            new_leaf.data = node.data[half:]
            node.keys=node.keys[:half]
            node.data =node.data[:half]

            new_leaf.write_back()
            node.write_back()
            new_root.write_back()

            return 

 
        if node.parent_addr != None: # if leaf has an internal node as parent
            

            parentnode = node.get_parent()
            bisect.insort(parentnode.keys,new_key)
            idx = parentnode.find_idx(new_key)
            new_leaf = BTreeNode(DISK.new(),parentnode.my_addr,idx+1, is_leaf=True)

            parentnode.children_addrs.insert(idx+1,new_leaf.my_addr)
            # node.index_in_parent = idx

            new_leaf.keys = node.keys[half:]
            new_leaf.data = node.data[half:]
            node.keys=node.keys[:half]
            node.data =node.data[:half]

            new_leaf.write_back()
            node.write_back()            
            parentnode.write_back()

            if len(parentnode.keys) <= self.M - 1 :
                return
            else:
                current = parentnode

                while len(current.keys) > self.M - 1:                    
                    if current.parent_addr != None:

                        c_half=len(current.keys)//2
                        c_new_key = current.keys[c_half]

                        c_parentnode = current.get_parent()
                        bisect.insort(c_parentnode.keys,c_new_key)
                        idx = c_parentnode.find_idx(c_new_key)
                        new_intnode = BTreeNode(DISK.new(),c_parentnode.my_addr,idx+1, is_leaf=False)
                        
                        c_parentnode.children_addrs.insert(idx+1,new_intnode.my_addr)

                        new_intnode.keys = current.keys[c_half+1:]

                        current.keys=current.keys[:c_half]
                        
                        new_intnode.children_addrs = current.children_addrs[(c_half+1):]
                        current.children_addrs = current.children_addrs[:(c_half+1)]
                        
                        tempi=0
                        for i in new_intnode.children_addrs:
                            child = get_node(i)
                            child.parent_addr = new_intnode.my_addr
                            child.index_in_parent=tempi
                            tempi= tempi+1 
                            child.write_back()
                            
                        c_parentnode.write_back()
                        new_intnode.write_back()
                        current.write_back()
                        
                    if current.parent_addr == None:
  
                        c_half=(len(current.keys))//2
                        c_new_key = current.keys[c_half]     

                        new_introot =  BTreeNode(DISK.new(),None , None, is_leaf= False)
                        new_introot.keys = [c_new_key]
                        new_intnode = BTreeNode(DISK.new(),new_introot.my_addr,index_in_parent = 1, is_leaf=False)
                        

                        new_introot.children_addrs = [current.my_addr,new_intnode.my_addr]
                        self.root_addr = new_introot.my_addr #important


                        new_intnode.keys = current.keys[c_half+1:]


                        current.keys=current.keys[:c_half]
                        current.parent_addr = new_introot.my_addr
                        current.index_in_parent = 0


                        new_intnode.children_addrs = current.children_addrs[(c_half+1):]
                        current.children_addrs = current.children_addrs[:(c_half+1)]


    
                        for i,j in enumerate(new_intnode.children_addrs):
                            child = get_node(j)
                            child.parent_addr = new_intnode.my_addr
                            child.index_in_parent=i
                            child.write_back()

                        new_introot.write_back()
                        new_intnode.write_back()
                        current.write_back()

                    current = current.get_parent()
                
        return
       
    def find(self, key: KT) -> Optional[VT]:
        """
        Find a key and return the value associated with it. If it is not in the BTree, return None.
        This should be implemented with a logarithmic search in the node.keys array, not a linear search. Look at the BTreeNode.find_idx() method for an example of using the builtin bisect library to search for a number in a sorted array in logarithmic time.
        """

        node = self.find_node(key, get_node(self.root_addr))

        if node.is_leaf:
            idx = node.find_idx(key)
            if idx < len(node.keys) and node.keys[idx] == key:
                return node.data[idx]
        return None

    def find_node(self, key, node):
        if node.is_leaf:
            return node
        else:
            if len(node.keys)==0:
                return self.find_node(key,node.get_child(0))
            else:
                for i in range(len(node.keys)):
                    if key < node.keys[i]:
                        return self.find_node(key,node.get_child(i))
                        
                return self.find_node(key, node.get_child(len(node.keys)))

            
    def delete(self, key: KT) -> None:
        raise NotImplementedError("Karma method delete()")



    def printTree(self,printLeaves=True):
        print('hi')
        q=[(get_node(self.root_addr),0)]
        i=0
        while len(q)!=0:
            n=q.pop()
            if n[1]!=i:
                print('--------------------------------')
            i=n[1]
            n=n[0]
            if printLeaves or not n.is_leaf:
                n.printNode()
            if n.children_addrs:
                for childAddr in n.children_addrs:
                    q.insert(0,(get_node(childAddr),i+1))

