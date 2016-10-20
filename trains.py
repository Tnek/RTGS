#/usr/bin/python
from PIL import Image, ImageTk
import tkinter as tk

class Sector(object):
    def __init__(self, name):
        self.name = name
        self.left = []
        self.right = []
        self.reset_astar()

    def set_coord(self, coord):
        self.coords = coord

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
        if path[0].name[0] == "R":
            path = path[::-1]
        return path

    def __repr__(self):
        return self.name

    def draw(self, canvas):
        canvas.create_rectangle(self.coords[0] - 5, self.coords[1] - 5, self.coords[0] + 105, self.coords[1] + 55, fill="gray", width=2)
        canvas.create_line(self.coords[0], self.coords[1] + 50, self.coords[0] + 100, self.coords[1] + 50, width=4)
        if len(self.left) >= 2:
            canvas.create_line(self.coords[0], self.coords[1], self.coords[0] + 100, self.coords[1] + 50, width=4)

        if len(self.right) >= 2:
            canvas.create_line(self.coords[0], self.coords[1] + 50, self.coords[0] + 100, self.coords[1], width=4)

        if len(self.right) >= 2 and len(self.left) >= 2:
            canvas.create_line(self.coords[0], self.coords[1], self.coords[0] + 100, self.coords[1], width=4)

        canvas.create_text(self.coords[0] + 20, self.coords[1] - 15,  text="Sector " + self.name[1])

class Station(Sector):
    def __init__(self, name):
        super().__init__(name)
        self.selected = False
    def draw(self, canvas):
        if self.name[0] == "R":
            canvas.create_rectangle(self.coords[0], self.coords[1] - 20, self.coords[0] - 20, self.coords[1],  width=2)
            if self.selected:
                canvas.create_rectangle(self.coords[0], self.coords[1], self.coords[0] - 20, self.coords[1] - 20, fill="gold", width=2)
            canvas.create_text(self.coords[0] - 10, self.coords[1] - 10,  text=self.name)
        else:
            canvas.create_rectangle(self.coords[0], self.coords[1] - 20, self.coords[0] + 20, self.coords[1], width=2)
            if self.selected:
                canvas.create_rectangle(self.coords[0], self.coords[1] - 20, self.coords[0] + 20, self.coords[1], fill="gold", width=2)
            canvas.create_text(self.coords[0] + 10, self.coords[1] - 10,  text=self.name)

class Blocker(Sector):
    def __init__(self, name):
        super().__init__(name)
        self.enabled = False
    def on_click(self):
        self.enabled = not self.enabled
    def draw(self, canvas):
        if self.enabled: 
            fillcolor = "red"
        else:
            fillcolor="white"
        canvas.create_oval(self.coords[0] - 5, self.coords[1] - 5, self.coords[0] + 5, self.coords[1] + 5, fill=fillcolor)
        canvas.create_text(self.coords[0], self.coords[1] - 15, text=self.name[1])

reverse_running_mode = {
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

normal_mode_right = {
     "L1":("S1",),
     "L2":("S1",),
     "L3":("bA",),
 
     "S1":("S3","bB"),
     "S2":(),
     "S3":("bD", "bE"),
     "S4":(),
     "S5":("bI",),
     "S6":(),
     "S7":("bK", "bL"),
     "S8":(),

     "bA":("S2",), "bB":("bF",), "bC":("S4",), "bD":("S5",),
     "bE":("S5",), "bF":("S7",), "bG":("S6",), "bH":("S6",),
     "bI":("S7",), "bJ":(), "bL":("R2",), "bK":("R1",)
}
normal_mode_left = {
     "L1":("S3",),
     "L2":("bB",),
     "L3":("bA",),
 
     "S2":("bC", "bH"),
     "S3":("bE",),
     "S4":("bF", "bG"),
     "S5":("bI",),
     "S6":("bJ",),
     "S8":("R2", "R3"),
 
     "bA":("S2",), "bB":("S4",), "bC":("S4",), "bD":("S5",),
     "bE":("S5",), "bF":("bL",), "bG":("S6",), "bH":("S6",),
     "bI":("bK",), "bJ":("S8",), "bL":("S8",), "bK":("R1",)
}

def populate_graph(connections_graph):
    """ 
        Generate objects given adjacency list
    """
    sectors = {"S"+str(i):Sector("S"+str(i)) for i in range(1, 9)}
    rstations ={"R"+str(i):Station("R"+str(i)) for i in range(1, 4)}
    lstations = {"L"+str(i):Station("L"+str(i)) for i in range(1, 4)}
    blockers = {"b"+chr(i):Blocker("b"+chr(i)) for i in range(65, 77)}
    objects = {**sectors, **rstations, **lstations, **blockers}
    for i in objects:
        objects[i].set_coord(node_coords[i])

    for connect in connections_graph:
        workingobj = objects[connect]
        children = connections_graph[connect]
        for i in children:
            workingobj.right.append(objects[i])
            objects[i].left.append(workingobj)

    return objects, blockers, lstations, rstations, sectors


node_coords = {
    "L1":(50, 100),
    "L2":(50, 150),
    "L3":(50, 250),

    "S1":(120, 100),
    "S2":(120, 200),
    "S3":(300, 50),
    "S4":(300, 150),
    "S5":(500, 50),
    "S6":(500, 200),
    "S7":(720, 100),
    "S8":(900, 150),

    "bA":(100, 250),
    "bB":(280, 150),
    "bC":(280, 200),
    "bD":(480, 50),
    "bE":(480, 100),
    "bF":(480, 150),
    "bG":(480, 200),
    "bH":(480, 250),
    "bI":(700, 100),
    "bJ":(700, 250),
    "bK":(880, 100),
    "bL":(880, 150),

    "R1":(1100, 100),
    "R2":(1100, 150),
    "R3":(1100, 200)
}

def reset_graph(objects):
    for i in objects:
        objects[i].reset_astar()

def astar(start, end, normal_mode=False):
    """ 
        Implementation of Dijkstra's algorithm

        :param start: Sector object to store next step in path of. 
        :param end: String which is the side it should stop at e.x. "R" or "L" 

        :return: List containing all nodes in path
    """
    openset = {start}
    while len(openset) > 0:
        min_weight = None
        for i in openset:
            if min_weight == None or i.weight < min_weight:
                current_node = i
                min_weight = i.weight

        # Reached goal
        if current_node.name[0] == end[0]:
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
                move._parent = current_node
                move.weight = move._distance
                if normal_mode:
                    if start.name[0] == "L":
                        move.weight = current_node.weight - move.coords[1]
                    elif start.name[0] == "R":
                        move.weight = current_node.weight - (1200 - move.coords[1])
 
def app_main():
    app = Application()
    app.mainloop()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.path = None
        self.path_ends = (None, None)
        self.objects, self.blockers, self.lstations, self.rstations, self.sectors = populate_graph(reverse_running_mode)
        self.reverse_running_mode()
        self.normal_mode = False

        self.title("Graph")
        c_width = 1145
        c_height = 300

        main_frame = tk.Frame(self, width=1145, height=175)
        main_frame.grid(row=1, column=2)
        self.toggle_btn = tk.Button(main_frame, text="Reverse Running Mode", width=30, command=self.toggle_normal_mode)
        self.toggle_btn.pack()

        self.canvas = tk.Canvas(main_frame, width=c_width, height=c_height, bg="white", scrollregion=(0, 0, 1145, 175))
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.pack()
        canvas_scrollbar = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL)
        canvas_scrollbar.config(command=self.canvas.xview)
        canvas_scrollbar.pack(side=tk.BOTTOM)
        self.redraw()

    def click(self, event):
        if event:
            for coord in node_coords:
                r = node_coords[coord]
                if r[0] < event.x + 10 and r[0] > event.x - 20 and r[1] < event.y + 20 and r[1] > event.y - 10 and r[1] < event.y + 10:
                    if coord[0] == "L":
                        self.path_ends = (self.objects[coord], "R")
                    elif coord[0] == "R":
                        self.path_ends = (self.objects[coord], "L")
                    elif coord[0] == "b":
                        self.objects[coord].on_click()

        if all(self.path_ends):
            #: I'm sorry this isn't the proper way but I got a deadline
            if self.normal_mode:
                if self.path_ends[0].name[0] == "L":
                    self.set_normal_mode("L")
                else:
                    self.set_normal_mode("R")

                self.path = astar(*self.path_ends, True)
                self.reverse_running_mode()
                self.normal_mode = True
            else:
                self.path = astar(*self.path_ends)

        self.redraw()

    def draw_path(self, path):
        end = None
        for i in range(len(path) - 1):
            connections = self._connect(path[i], path[i+1])
            self.canvas.create_line(*connections[0], *connections[1], width=5, fill="gold")
            if end:
                self.canvas.create_line(*end, *connections[0], width=5, fill="gold")
            end = connections[1]
    def toggle_normal_mode(self):
        self.normal_mode = not self.normal_mode
        if self.normal_mode:
            self.toggle_btn.config(text="Normal Mode")
        else:
            self.toggle_btn.config(text="Reverse Running Mode")
        self.click(None)

    def set_graph(self, connections_graph):
        for i in self.objects:
            self.objects[i].left = []
            self.objects[i].right = []

        for connect in connections_graph:
            workingobj = self.objects[connect]
            children = connections_graph[connect]
            for i in children:
                workingobj.right.append(self.objects[i])
                self.objects[i].left.append(workingobj)

    def reverse_running_mode(self):
        self.normal_mode = False
        self.set_graph(reverse_running_mode)

    def set_normal_mode(self, direction):
        self.normal_mode = True
        if direction == "L":
            self.set_graph(normal_mode_left)
        elif direction == "R":
            self.set_graph(normal_mode_right)

    def _connect(self, object1, object2):
        start = object1.coords
        end = object2.coords
        if isinstance(object1, Blocker) or isinstance(object1, Station):
            start = object1.coords
        else:
            if object1.coords[1] < object2.coords[1]: # draw from bottom
                start = (object1.coords[0] + 100, object1.coords[1] + 50)
            else:
                start = (object1.coords[0] + 100, object1.coords[1])

        if isinstance(object2, Blocker) or isinstance(object2, Station):
            end = object2.coords
        else:
            if object1.coords[1] > object2.coords[1]: # draw from bottom
                end = (object2.coords[0], object2.coords[1] + 50)
            else:
                end = (object2.coords[0], object2.coords[1])

        return (start, end)
        

    def draw_connections(self):
        for start in reverse_running_mode:
            for end in reverse_running_mode[start]:
                connections = self._connect(self.objects[start], self.objects[end])
                self.canvas.create_line(*connections[0], *connections[1], width=4)

    def redraw(self):
        self.canvas.delete("all")
        reset_graph(self.objects)
        for i in self.sectors:
            self.sectors[i].draw(self.canvas)

        for i in self.lstations:
            self.lstations[i].selected = self.path_ends[0] and self.path_ends[0].name == i
            self.lstations[i].draw(self.canvas)

        for i in self.rstations:
            self.rstations[i].selected = self.path_ends[0] and self.path_ends[0].name == i
            self.rstations[i].draw(self.canvas)

        self.draw_connections()

        if self.path:
            self.draw_path(self.path)

        for i in self.blockers:
            self.blockers[i].draw(self.canvas)


if __name__ == "__main__":
    app_main() 
