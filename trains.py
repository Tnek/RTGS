#!/bin/python

class Sector(object):
    def __init__(self, name):
        self.name = name
        self.left = []
        self.right = []
        self.reset_astar()

    def reset_astar(self):
        self.weight = 0

        self._parent = None
        # Temp value used by astar
        self._distance = 0


    def can_reach(self, other):
        return True
    def __repr__(self):
        if self._parent != None:
            return self.name + "->" + str(self._parent)
        else:
            return self.name

class Blocker(Sector):
    def __init__(self, name):
        super().__init__(name)
        self.enabled = False

connections = {
    "L1":("S1",),
    "L2":("S1",),
    "L3":("bA",),

    "S1":("S3","bB"),
    "S2":("bC", "bH"),
    "S3":("bD", "bE"),
    "S4":("bF", "bG"),
    "S5":("bI",),
    "S6":("bJ",),
    "S7":("bK", "bL"),
    "S8":("R2", "R3"),

    "bA":("S2",), "bB":("S4",), "bC":("S4",), "bD":("S5",),
    "bE":("S5",), "bF":("S7",), "bG":("S6",), "bH":("S6",),
    "bI":("S7",), "bJ":("S8",), "bL":("S8",), "bK":("R1",)
}

def reverse_running_mode():
    gen = lambda leadchr, rnge:{leadchr+str(i):Sector(leadchr+str(i)) for i in rnge}
    sectors = gen("S", range(1, 9))
    rstations = gen("R", range(1, 4))
    lstations = gen("L", range(1 ,4))
    blockers = {"b"+chr(i):Blocker("b"+chr(i)) for i in range(65, 77)}
    objects = {**sectors, **rstations, **lstations, **blockers}

    #: Populate graph given table of connections
    for connect in connections:
        workingobj = objects[connect]
        children = connections[connect]
        for i in children:
            workingobj.right.append(objects[i])
            objects[i].left.append(workingobj)
#    for i in rstations:
#        print(astar(rstations[i], lstations["L1"]))
    for i in lstations:
        print(astar(lstations[i], rstations["R1"]))
    for i in objects:
        objects[i].reset_astar()
    for i in rstations:
        print(astar(rstations[i], lstations["L1"]))

def astar(start, end):
    """ Actually a lie, this is actually just dijkstra's because I don't have a heuristic to use yet """
    openset = {start}
    while len(openset) > 0:
        for i in openset:
            min_weight = None
            if min_weight == None or i.weight < min_weight:
                current_node = i
                min_weight = i.weight

        # We made it!
        if current_node.name[0] == end.name[0]:
            return current_node

        openset.remove(current_node)

        possible_moves = []
        # Which direction?
        if start.name[0] == "L":  # We want to go right
            possible_moves = [i for i in current_node.right if current_node.can_reach(i)] 
        elif start.name[0] == "R":  # We want to go left
            possible_moves = [i for i in current_node.left if current_node.can_reach(i)]

        for move in possible_moves:
            move._distance = current_node._distance + 1

            if not move in openset:
                openset.add(move)
            else:
                continue

            move._parent = current_node
            #: TODO: Actually write a heuristic
            move.weight = move._distance # + any other heuristics

reverse_running_mode()
