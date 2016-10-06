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
        if isinstance(other, Blocker):
            return not other.enabled
        return True

    def backpropagate(self):
        path = [self]
        i = self._parent
        while i._parent != None:
            path.append(i)
            i = i._parent
        path.append(i)
        return path[::-1]

    def __repr__(self):
        return self.name

class Blocker(Sector):
    def __init__(self, name):
        super().__init__(name)
        self.enabled = False

def gen_entry(start):
    """
    I'm sorry, this function is ugly code

    Returns:
        S1 - S8 - 0, 1, "X"

    """

    sectors = {"S"+str(i):"X" for i in range(1, 9)}
    if start != None:
        used_sectors = [i for i in start if i.name[0] == "S"]
        for s in used_sectors:
            sectors[s.name] = 1
        print(sectors)
        return []
    return 

#    print("->".join(str(i) for i in [j for j in start if start]))

#    if start:
#        if start[0].name[0] == "L":
#            for i in range(1, len(start) - 1):
#                if len(lconnections[start[i].name]) >= 2:
#                    pass

lconnections = {
    "L1":("S3", "bA"),
    "L2":("S3", "bA"),
    "L3":("bA",),

    "S2":("bC", "bH"),
    "S3":("bD", "bE"),
    "S5":("bI",),
    "S6":("bJ",),

    "bA":("S2",), "bB":("bF", "bG",), "bC":("bF", "bG",), "bD":("S5",),
    "bE":("S5",), "bF":("bK", "bL",), "bG":("S6",), "bH":("S6",),
    "bI":("bK", "bL",), "bJ":("R2", "R3",), "bL":("R2", "R3",), "bK":("R1",)
}

def astar(start, end):
    openset = {start}
    while len(openset) > 0:
        for i in openset:
            min_weight = None
            if min_weight == None or i.weight < min_weight:
                current_node = i
                min_weight = i.weight

        # Reached goal
        if current_node.name[0] == end.name[0]:
            return current_node.backpropagate()

        openset.remove(current_node)

        possible_moves = []
        # Which direction?
        if start.name[0] == "L":  # Go right
            possible_moves = [i for i in current_node.right if current_node.can_reach(i)] 
        elif start.name[0] == "R":  # Go left
            possible_moves = [i for i in current_node.left if current_node.can_reach(i)]

        for move in possible_moves:
            move._distance = current_node._distance + 1

            if not move in openset:
                openset.add(move)
            else:
                continue

            move._parent = current_node
            move.weight = move._distance # + any other heuristics
 
def reverse_running_mode():
    global objects
    gen = lambda leadchr, rnge:{leadchr+str(i):Sector(leadchr+str(i)) for i in rnge}
    sectors = gen("S", range(1, 9))
    rstations = gen("R", range(1, 4))
    lstations = gen("L", range(1 ,4))
    blockers = {"b"+chr(i):Blocker("b"+chr(i)) for i in range(65, 77)}
    blocker_list = list(blockers.values())
    objects = {**sectors, **rstations, **lstations, **blockers}

    #: Populate graph given table of connections
    for connect in lconnections:
        workingobj = objects[connect]
        children = lconnections[connect]
        for i in children:
            workingobj.right.append(objects[i])
            objects[i].left.append(workingobj)

    lboolvals = {"L" + str(i):[] for i in range(1, len(lstations) + 1)}
    rboolvals = {"R" + str(i):[] for i in range(1, len(rstations) + 1)}
    boolvals = {**lboolvals, **rboolvals}

    blocker_size = len(blockers)
    for x in range(2**blocker_size):
        arr = [(x>>i) & 1 for i in range(blocker_size-1,-1,-1)]
        for blocker in range(blocker_size):
            blocker_list[blocker].enabled = (arr[blocker] == 1)

        #: Generate all left to right
        for i in lstations:
            bool_vals = gen_entry(astar(lstations[i], rstations["R1"]))
            boolvals[lstations[i].name].append(bool_vals)
            for i in objects:
                objects[i].reset_astar()

        #: Now lets do right to left
        for i in rstations:
            gen_entry(astar(rstations[i], lstations["L1"]))
            boolvals[rstations[i].name].append(bool_vals)
            for i in objects:
                objects[i].reset_astar()

reverse_running_mode()
