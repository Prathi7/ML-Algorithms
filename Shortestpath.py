from py_wikiracer.internet import Internet
from typing import List
from heapq import *
from collections import defaultdict
from difflib import SequenceMatcher,get_close_matches

class Parser:

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:

        links = []
        disallowed = Internet.DISALLOWED
        pos = 0
        while True:
            pos=html.find('a href="/wiki/',pos) # makes sure its internal but not external 
            if pos < 0:
                break
            end = html.find('"',pos+8)

            if all([ch not in html[pos+14:end] for ch in disallowed]): #avoids disallowed characters
                if html[pos+8:end] not in links: # avoids duplicates
                    links.append(html[pos+8:end]) 
            pos += 1

        return links

class BFSProblem:
    def __init__(self):
        self.internet = Internet()
        
    def bfs(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia"):
        path = [source]
        queue =[]
        visited = set()
        queue =[(source,path)]

        while queue:
            node, path = queue.pop(0)
            if node is visited:
                continue
            visited.add(node)

            for i in Parser.get_links_in_page(self.internet.get_page(node)):
                if i == goal:
                    return (path + [goal])
                else:
                    if i not in visited:
                        queue.append((i,path+[i]))
        
        if path == None or len(path) <= 1:
            return None


class DFSProblem:
    def __init__(self):
        self.internet = Internet()
    # Links should be inserted into a stack as they are located in the page. Do not add things to the visited list until they are taken out of the stack.
    def dfs(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia"):
        path = [source]
        queue =[]
        visited = set()
        queue =[(source,path)]

        while queue:
            node, path = queue.pop()
            if node is visited:
                continue
            visited.add(node)
            for i in Parser.get_links_in_page(self.internet.get_page(node)):
                if i == goal:
                    return (path + [goal])
                else:
                    if i not in visited:
                        queue.append((i,path+[i]))
        
        if path == None or len(path) <= 1:
            return None

class DijkstrasProblem:
    def __init__(self):
        self.internet = Internet()

    def dijkstras(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia", costFn = lambda x, y: len(y)):
        
        path = [source]
        visited =  set()
        que = [(0,source,path)] # tuple with cost (initial cost 0), node, path         
    
        while que:
            (cost, node, path) = heappop(que)
            if node in visited:
                continue
            visited.add(node)    
            for i in Parser.get_links_in_page(self.internet.get_page(node)):
                if i == goal:
                    return (path + [goal])
                else:
                    if i not in visited:
                        heappush(que,(cost+costFn(node,i),i,path+[i]))
                            
        if path == None or len(path) <= 1:
            return None


class WikiracerProblem:
    def __init__(self):
        self.internet = Internet()

    def mycostfn(self,node,goal,goallinks): #instead of sending noes, pass downloaded pages as already fetched
        costval = 1
        a,b = 1,1

        goalword=goal[6:len(goal)]
        nodeword=node[6:len(node)]
        goall=[]
        for i in goallinks:
            goall.append(i[6:len(i)])

        seqmat_strings = SequenceMatcher(None,goal,node)
        matches = get_close_matches(nodeword,goall,n=500,cutoff=0.75)
    
        if seqmat_strings.ratio() > 0:
            a = seqmat_strings.ratio()

        if len(matches) > 0:
            b=(len(matches)/500)
    
        costval = a*b
        return costval

    def wikiracer(self, source = "/wiki/Calvin_Li", goal = "/wiki/Wikipedia"):
        
        path=[source]
        if source == goal:
            return (path.append(goal))

        goallinks =  Parser.get_links_in_page(self.internet.get_page(goal))

        visited =  set()
        que = [(0,source,path)] # tuple with cost (initial cost 0), node, path         

        while que:
            (cost, node, path) = heappop(que)
            if node in visited:
                continue
            visited.add(node)   
        
            nodelinks = Parser.get_links_in_page(self.internet.get_page(node))
            for i in nodelinks:
                if i == goal:
                    return (path + [goal])
                else:
                    if i not in visited:
                        heappush(que,(cost+self.mycostfn(i,goal,goallinks),i,path+[i]))
                            
        if path == None or len(path) <= 1:
            return None

