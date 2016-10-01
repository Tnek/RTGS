#!/bin/python

class Sector(object):
    def __init__(self, name):
        self.name = name
        self.left = []
        self.right = []
        self.canReach = True
    def __repr__(self):
        return self.name

class Blocker(Sector):
    def __init__(self, name):
        super().__init__(name)
    def __repr__(self):
        return self.name

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


