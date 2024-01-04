from py_wikiracer.internet import Internet
from typing import List
from heapq import *
from collections import defaultdict
from difflib import SequenceMatcher,get_close_matches

class Parser:

    # def __init__(self):
    #     self.internet = Internet()

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        """
        In this method, we should parse a page's HTML and return a list of links in the page.
        Be sure not to return any link with a DISALLOWED character.
        All links should be of the form "/wiki/<page name>", as to not follow external links
        """
        # print("hi")
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

        
        # print("yeel",links)

        # YOUR CODE HERE
        # You can look into using regex, or just use Python's find methods to find the <a> tags or any other identifiable features
        # A good starting place is to print out `html` and look for patterns before/after the links that you can string.find().
        # Make sure your list doesn't have duplicates. Return the list in the same order as they appear in the HTML.
        # This function will be stress tested so make it efficient!

        return links

# In these methods, we are given a source page and a goal page, and we should return
#  the shortest path between the two pages. Be careful! Wikipedia is very large.

# These are all very similar algorithms, so it is advisable to make a global helper function that does all of the work, and have
#  each of these call the helper with a different data type (stack, queue, priority queue, etc.)

class BFSProblem:
    def __init__(self):
        self.internet = Internet()
    # Example in/outputs:
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computer_science") == ["/wiki/Computer_science", "/wiki/Computer_science"]
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computation") == ["/wiki/Computer_science", "/wiki/Computation"]
    # Find more in the test case file.

    # Do not try to make fancy optimizations here. The autograder depends on you following standard BFS and will check all of the pages you download.
    # Links should be inserted into the queue as they are located in the page, and should be obtained using Parser's get_links_in_page.
    # Be very careful not to add things to the "visited" set of pages too early. You must wait for them to come out of the queue first. See if you can figure out why.
    #  This applies for bfs, dfs, and dijkstra's.
    # Download a page with self.internet.get_page().
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
    # Links should be inserted into the heap as they are located in the page.
    # By default, the cost of going to a link is the length of a particular destination link's name. For instance,
    #  if we consider /wiki/a -> /wiki/ab, then the default cost function will have a value of 8.
    # This cost function is overridable and your implementation will be tested on different cost functions. Use costFn(node1, node2)
    #  to get the cost of a particular edge.
    # You should return the path from source to goal that minimizes the total cost. Assume cost > 0 for all edges.
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

    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

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
# KARMA
class FindInPageProblem:
    def __init__(self):
        self.internet = Internet()
    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source = "/wiki/Calvin_Li", query = ["ham", "cheese"]):

        raise NotImplementedError("Karma method find_in_page")

        path = [source]

        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path # if no path exists, return None
