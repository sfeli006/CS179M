import os, copy, queue, pickle, glob
from datetime import datetime
from queue import PriorityQueue
from tkinter import *
import tkinter.messagebox, tkinter.filedialog as fd

class Ship:
    # REPRESENTATION
    def __init__(self, width, height, grid, bay):
        self.width  = width
        self.height = height
        self.grid   = grid
        self.bay    = bay

    # OPERATORS
    # Where definitions for move, balance, and swap containers operators go.
    def swap(self, x_1, y_1, x_2, y_2):
        index_1 = (y_1 - 1) + ((x_1 -1) * 12)
        index_2 = (y_2 - 1) + ((x_2 -1) * 12)

        tmp_container = copy.deepcopy(self.grid[index_1])
        self.grid[index_1] = self.grid[index_2]
        self.grid[index_1].xPos = x_1
        self.grid[index_1].yPos = y_1

        self.grid[index_2] = tmp_container
        self.grid[index_2].xPos = x_2
        self.grid[index_2].yPos = y_2

        # TODO: Change position values for moved containers in self.bay too

    # OUTPUT
    # For terminal display visualization. Useful for displaying each state.
    # Invalid slots (NAN) are displayed as '█'.
    # Empty slots (UNUSED) are displayed as '-'.
    # Containers are displayed as the first letter of their name.
    def __repr__(self):
        ret_str = ''
        for y in range(self.height - 1, -1, -1):
            for x in range(0, self.width):
                index = x + (y*12)
                curr_container = self.grid[index]
                if (curr_container.name == 'NAN'):
                    ret_str += '█ '
                elif (curr_container.name == 'UNUSED'):
                    ret_str += '- '
                else:
                    ret_str += ((curr_container.name[0]) + ' ')

                pass
            if (y != 0):
                ret_str += '\n'
        return ret_str

class Buffer:
    # REPRESENTATION
    def __init__(self, grid, containers=None):
        self.width          = 24
        self.height         = 4
        self.grid           = grid
        self.containers     = containers

    # OPERATORS
    # Where definitions for move, balance, and swap containers operators go.
    def swap(self, x_1, y_1, x_2, y_2):
        index_1 = (y_1 - 1) + ((x_1 -1) * 12)
        index_2 = (y_2 - 1) + ((x_2 -1) * 12)

        tmp_container = copy.deepcopy(self.grid[index_1])
        self.grid[index_1] = self.grid[index_2]
        self.grid[index_1].xPos = x_1
        self.grid[index_1].yPos = y_1

        self.grid[index_2] = tmp_container
        self.grid[index_2].xPos = x_2
        self.grid[index_2].yPos = y_2

        # TODO: Change position values for moved containers in self.bay too

    # OUTPUT
    # For terminal display visualization. Useful for displaying each state.
    # Invalid slots (NAN) are displayed as '█'.
    # Empty slots (UNUSED) are displayed as '-'.
    # Containers are displayed as the first letter of their name.
    def __repr__(self):
        ret_str = ''
        for y in range(self.height - 1, -1, -1):
            for x in range(0, self.width):
                index = x + (y*12)
                curr_container = self.grid[index]
                if (curr_container.name == 'NAN'):
                    ret_str += '█ '
                elif (curr_container.name == 'UNUSED'):
                    ret_str += '- '
                else:
                    ret_str += ((curr_container.name[0]) + ' ')

                pass
            if (y != 0):
                ret_str += '\n'
        return ret_str

class Container:
    # REPRESENTATION
    def __init__(self, xPos, yPos, weight, name):
        self.xPos   = xPos  #row
        self.yPos   = yPos  #column
        self.weight = weight
        self.name   = name

    # OPERATORS
    def get_dist(self, xPos_new, yPos_new):
        # Manhatten Distance
        return (abs(xPos_new - self.xPos) + abs(yPos_new - self.yPos))

    def get_index(self):
        return (self.yPos -1) + ((self.xPos - 1) * 12)

    # OUTPUT
    # Used for outputting to new Manifest.
    def __repr__(self) -> str:
        ret_str =   ('['+(str(self.xPos).zfill(2))
                    +','+(str(self.yPos).zfill(2))+']'+", "
                    +'{'+(str(self.weight).zfill(5))+'}'+", "
                    +self.name)
        return ret_str

def addLogComment(str):
    f = open("log.txt", "a")
    now = datetime.now()
    time_str = now.strftime("%B %d %Y: %H:%M")
    if len(str) > 0 and str != "\n":
        f.write(time_str + " " + str)
    else:
        pop_up(1)
    f.close()
    
def loadManifest(manifest_file_path):
    #path = input("Manifest File Path:")
    f           = open(manifest_file_path, "r")
    lines       = f.readlines()

    bay         = []
    grid        = []

    for line in lines:
        temp = line.split(", ")
        pos_str = temp[0].strip("[]").split(",")
        xPos = int(pos_str[0])
        yPos = int(pos_str[1])
        weight = int(temp[1].strip("{}"))
        name = temp[2].strip("\n")
        container = Container(xPos, yPos, weight, name)

        if name != "NAN" and name != "UNUSED":
            bay.append(container)

        # print(xPos, yPos, weight, name)
        grid.append(container)  # index = (xPos-1)*12+(yPos-1)

    ret_ship    = Ship(12, 8, grid, bay)
    f.close()
    temp = "Manifest " + manifest_file_path + " is opened, there are " + str(len(bay)) + " containers on the ship.\n"
    addLogComment(temp)
    return ret_ship

def loadShip():
    global root
    global port_mass_label
    global starboard_mass_label
    global run_OnOffload
    global run_balance

    global init_ship_state
    global manifest_name
    global buffer
    global solution_nodes
    global curr_load_node
    global onlist
    global offlist
    global mode
    global empty_ship
    global finish_flag


    finish_flag = False
    solution_nodes = []

    filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
    )
    file = fd.askopenfile(filetypes=filetypes)

    if (file != None):
        path = os.path.abspath(file.name)
        manifest_name = path.split("\\")[-1].split(".txt")[0]
        with open(".cache/manifest_name.txt", 'wb') as pickle_file:
            pickle.dump(manifest_name, pickle_file)

        init_ship_state = loadManifest(path)
        empty_ship = (len(init_ship_state.bay) == 0)
        buffer = initialize_empty_buffer()
        onlist = []
        offlist = []
        mode = 1
        curr_load_node = 0

        with open(".cache/onlist.txt", 'wb') as pickle_file:
            pickle.dump(onlist, pickle_file)
        with open(".cache/offlist.txt", 'wb') as pickle_file:
            pickle.dump(offlist, pickle_file)
        with open(".cache/mode.txt", 'wb') as pickle_file:
            pickle.dump(mode, pickle_file)

        draw_grid(init_ship_state.grid)

        port_mass = "0"
        port_mass_label.configure(text="Port Mass: "+port_mass, fg="#000000", width=20, font=("Arial", 10))
        starboard_mass = "0"
        starboard_mass_label.configure(text="Starboard Mass: "+starboard_mass, fg="#000000", width=20, font=("Arial", 10))

        run_OnOffload = Button(text="Run On/Offload", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: run_load(init_ship_state))
        run_OnOffload.grid(row=3, column=14, padx=7)
        run_balance = Button(text="Run Balance", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: run_balancing(init_ship_state))
        run_balance.grid(row=3, column=15, padx=7)

        entry = Entry(width=40)
        entry_display = entry.grid(row=2, column=14, padx=1, sticky=N)
        add_onload_btn = Button(text="Add To Onload", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: add_to_onload(init_ship_state.grid, entry)).grid(row=2, column=15, padx=1, sticky=N)

        root.title(manifest_name)

def initialize_empty_buffer():
    grid        = []
    for x in range(0, 4):
        for y in range(0, 24):
            curr_spot = Container(x+1, y+1, 0, "UNUSED")
            grid.append(curr_spot)

    ret_buffer  = Buffer(grid)
    return ret_buffer

def initialize_empty_ship():
    bay     = []
    grid    = []
    for x in range(0, 12):
        for y in range(0, 8):
            curr_spot = Container(x+1, y+1, 0, "UNUSED")
            grid.append(curr_spot)

    ret_ship = Ship(12, 8, grid, bay)
    return ret_ship

class OnOffNode:
    # Representing each state of Ship & Buffer.
    def __init__(self, curr_grid, onlist, offlist, parent, operation, cost, fn):
        self.grid = curr_grid    # list of containers
        self.onlist = onlist
        self.offlist = offlist
        self.parent = parent
        self.operation = operation  # string
        self.estimated_time = cost
        self.fn = fn

    def checkTop(self, index):  # return all boxes on top of the container (with this index) and the top box
        curX = self.grid[index].xPos
        curY = self.grid[index].yPos
        boxes = []
        topBox = index
        for i in range(curX+1, 9):  # from curX+1(spot on top) to 8
            if self.grid[(i-1)*12+(curY-1)].name != "UNUSED":
                boxes.append((i-1)*12+(curY-1))
                topBox = (i-1)*12+(curY-1)
        return boxes, topBox

    def available_spot(self, x, y):
        available_spots = []
        for i in range(12):
            row = 1
            while row <= 8 and self.grid[(row-1)*12 + i].name != "UNUSED":
                row = row + 1

            if row == 9:
                pass
            elif self.grid[(row-1)*12 + i].name == "UNUSED":
                if x == 9 or (y-1) != i:
                    available_spots.append((row-1)*12 + i)
        return available_spots

    def nearest_available_spot(self, x, y):  # from x, y to nearest empty spot that's not on top of boxes need to be removed
        spots = self.available_spot(x, y)
        nearest = spots[0]
        minDist = self.grid[spots[0]].get_dist(x, y)
        for i in range(len(spots)):
            if (x != 9 and self.grid[spots[i]].yPos != y) or x == 9:
                dist = self.grid[spots[i]].get_dist(x, y)
                if dist < minDist:
                    minDist = dist
                    nearest = spots[i]
        return minDist, nearest     # return the minimum distance and the index of the nearest spot in grid

    def box_with_least_cost(self, boxes):   # the index of the box_with_least_cost and the cost
        minCost = 100000   # a very large number
        box_to_remove = boxes[0]
        for i in range(len(boxes)):
            x = self.grid[boxes[i]].xPos
            y = self.grid[boxes[i]].yPos
            if boxes[i] in self.offlist:   # from current pos to {9,1} + 2 mins
                cost = abs(9 - x) + abs(1 - y)
                cost = cost + 2     # transfer between truck and ship, so +2 mins
                if cost < minCost:
                    minCost = cost
                    box_to_remove = boxes[i]
            else:   # not target box
                minDist, nearest = self.nearest_available_spot(x, y)
                cost = minDist
                if cost < minCost:
                    minCost = cost
                    box_to_remove = boxes[i]

        return minCost, box_to_remove

    # 2 operations:
    # (1) load to nearest available spot (load)
    # (2) remove the one with the least cost (offload)
    def expand(self):
        box_can_be_removed = []     #box can be moved
        boxes_on_top = []
        ops = []
        for i in range(len(self.offlist)):
            boxes, topbox = self.checkTop(self.offlist[i])
            box_can_be_removed.append(topbox)
            boxes_on_top.extend(boxes)
        # operation 1:
        if len(self.onlist) > 0:
            new_onlist = copy.deepcopy(self.onlist)
            new_offlist = copy.deepcopy(self.offlist)
            new_grid = copy.deepcopy(self.grid)
            temp = new_onlist.pop(0)   # container
            onDist, dest = self.nearest_available_spot(9, 1)    # virtual pink spot, problem slide pg32
            hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top)  # current state to goal state
            gn = 2 + onDist   # cost to get to this node
            fn = hn+gn
            new_grid[dest].name = temp.name
            new_grid[dest].weight = temp.weight
            operation_str = "Load \'" + temp.name + "\' to {" + str(new_grid[dest].xPos) + ", " + str(new_grid[dest].yPos) + "}"

            op1 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            ops.append(op1)

        # operation 2:
        if len(self.offlist) > 0:
            new_onlist = copy.deepcopy(self.onlist)
            new_offlist = copy.deepcopy(self.offlist)
            new_grid = copy.deepcopy(self.grid)
            cost, temp = self.box_with_least_cost(box_can_be_removed)
            if temp in new_offlist:     # if it's target box
                new_offlist.remove(temp)
                gn = cost
                hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top)
                fn = gn + hn
                operation_str = "Remove \'" + new_grid[temp].name + "\' from {" + str(new_grid[temp].xPos) + ", " + str(new_grid[temp].yPos) + "}"
                new_grid[temp].name = "UNUSED"
                new_grid[temp].weight = 0
                op2 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            else:
                gn = cost
                hn = len(new_onlist) + len(new_offlist) + len(boxes_on_top) - 1    # remove 1 from boxes_on_top
                fn = gn + hn
                offDist, dest = self.nearest_available_spot(new_grid[temp].xPos, new_grid[temp].yPos)   # temp -> target
                operation_str = "Move \'" + new_grid[temp].name + "\' from {" + str(new_grid[temp].xPos) + ", " + str(new_grid[temp].yPos) + "} to {" + str(new_grid[dest].xPos) + ", " + str(new_grid[dest].yPos) + "}"
                new_grid[dest].name = new_grid[temp].name
                new_grid[dest].weight = new_grid[temp].weight
                new_grid[temp].name = "UNUSED"
                new_grid[temp].weight = 0
                op2 = OnOffNode(new_grid, new_onlist, new_offlist, self, operation_str, gn, fn)
            ops.append(op2)

        return ops

def OnOff_goal_test(node):
    if len(node.onlist) == 0 and len(node.offlist) == 0:
        return True
    else:
        return False

class BalanceNode:
    def __init__(self, ship=None, parent=None, children=[], operation='Start balancing', cost=0, estimated_time = 0, depth=0):
        self.ship           = ship
        self.parent         = parent
        self.children       = children
        self.operation      = operation
        self.cost           = cost
        self.estimated_time = estimated_time
        self.depth          = depth
        self.grid = ship.grid
        
    # Get mass on left-hand side of the ship.
    def get_port_mass(self):
        port_mass = 0
        for y in range(0, self.ship.height):
            for x in range (0, int(self.ship.width/2)):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                port_mass += curr_container.weight
        return port_mass

    # Get mass on right-hand side of the ship.
    def get_starboard_mass(self):
        starboard_mass = 0
        for y in range(0, self.ship.height):
            for x in range (int(self.ship.width/2), self.ship.width):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                starboard_mass += curr_container.weight
        return starboard_mass

    # Get containers on left-hand side of the ship.
    def get_port_containers(self):
        port_containers = []
        for y in range(0, self.ship.height):
            for x in range (0, int(self.ship.width/2)):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                if ((curr_container.name != 'NAN') and (curr_container.name != 'UNUSED')):
                    port_containers.append(curr_container.name)
        return sorted(port_containers)

    # Get containers on right-hand side of the ship.
    def get_starboard_containers(self):
        starboard_containers = []
        for y in range(0, self.ship.height):
            for x in range (int(self.ship.width/2), self.ship.width):
                index = x + (y*12)
                curr_container = self.ship.grid[index]
                if ((curr_container.name != 'NAN') and (curr_container.name != 'UNUSED')):
                    starboard_containers.append(curr_container.name)
        return sorted(starboard_containers)

    # Return all valid positions to move a container to.
    def available_spots(self, selected_container):
        arr_available_spots = []
        for x in range(self.ship.width):
            y = 0
            curr_index = x + (y*12)
            while((self.ship.grid[curr_index].name != "UNUSED") and (y < self.ship.height)):
                y += 1
                if (y != self.ship.height):
                    curr_index = x + (y*12)
            available_spot = self.ship.grid[curr_index]

            if ((available_spot.name == "UNUSED") and (selected_container.yPos != available_spot.yPos)):
                arr_available_spots.append(available_spot)
        return arr_available_spots
    
    # Return containers at the top of each column, if any.
    def accessable_containers(self):
        arr_accessable_containers = []
        for x in range(self.ship.width): 
            y = 0
            curr_index = x + (y*12)
            curr_container = self.ship.grid[curr_index]
            while((curr_container.name != "UNUSED") and (y < (self.ship.height - 1))):
                if (self.ship.grid[x + ((y+1) * 12)].name != "UNUSED"):
                    y += 1
                    if (y != self.ship.height):
                        curr_index = x + (y*12)
                    curr_container = self.ship.grid[curr_index]
                else:
                    break
            if (curr_container.name != "UNUSED" and curr_container.name != "NAN"):
                arr_accessable_containers.append(curr_container)
        return arr_accessable_containers

    def expand(self, selected_container):
        arr_available_spots         = self.available_spots(selected_container)
        init_balance_offset         = abs(self.get_port_mass() - self.get_starboard_mass())

        x_1 = selected_container.xPos
        y_1 = selected_container.yPos

        attempted_nodes     = []
        attempted_weights   = []
        attempted_distances = []

        for spot in arr_available_spots:
            x_2 = spot.xPos
            y_2 = spot.yPos

            child = BalanceNode(copy.deepcopy(self.ship))
            child.parent = self
            child.ship.swap(x_1, y_1, x_2, y_2)
            child.operation         =   ("Move Container \'"
                                        + selected_container.name
                                        +"\' at ["+str(x_1).zfill(2)+","+str(y_1).zfill(2)
                                        +"] to ["
                                        +str(x_2).zfill(2)+","+str(y_2).zfill(2)+"]")
            distance_heursitic      = selected_container.get_dist(x_2, y_2)
            balance_heuristic       = abs(child.get_port_mass() - child.get_starboard_mass())
            child.cost              = distance_heursitic + balance_heuristic
            child.depth             = self.depth + 1
            child.estimated_time    = distance_heursitic

            if (balance_heuristic != init_balance_offset):
                attempted_nodes.append(child)
                attempted_distances.append(distance_heursitic)
                attempted_weights.append(balance_heuristic)       
        
        expanded_nodes = select_best_balance_children(  attempted_weights, 
                                                        list(set(attempted_weights)), 
                                                        attempted_distances, 
                                                        attempted_nodes)        
        self.children = expanded_nodes
        return expanded_nodes
    
    def expand_SIFT(self, goal_grid):
        _parent_operation = self.operation
        _child_operations = []


        expanded_nodes              = []
        arr_accessable_containers   = self.accessable_containers()
        for selected_container in arr_accessable_containers:
            c_i = selected_container.get_index()
            goal_spot = goal_grid[c_i]
            if ((goal_spot.name != selected_container.name) or (goal_spot.weight != selected_container.weight)):
                move_spot       = None
                move_spot_index = 0
                x_1             = selected_container.xPos
                y_1             = selected_container.yPos

                while (move_spot == None):
                    if ((goal_grid[move_spot_index].name == selected_container.name) and 
                        (goal_grid[move_spot_index].weight == selected_container.weight)):
                        move_spot = goal_grid[move_spot_index]
                    else:
                        move_spot_index += 1

                x_2 = move_spot.xPos
                y_2 = move_spot.yPos

                container_at_move_spot = self.ship.grid[move_spot_index]

                if ((container_at_move_spot.name == "UNUSED") and ((x_1 != x_2) or (y_1 != y_2))):
                    child = BalanceNode(copy.deepcopy(self.ship))
                    child.parent = self
                    child.ship.swap(x_1, y_1, x_2, y_2)
                    child.operation         =   ("Move Container \'"
                                                + selected_container.name
                                                +"\' at ["+str(x_1).zfill(2)+","+str(y_1).zfill(2)
                                                +"] to ["
                                                +str(x_2).zfill(2)+","+str(y_2).zfill(2)+"]")
                    distance_heursitic      = selected_container.get_dist(x_2, y_2)
                    child.cost              = distance_heursitic
                    child.depth             = self.depth + 1
                    child.estimated_time    = distance_heursitic
                    expanded_nodes.append(child)
                    _child_operations.append(child.operation)

        self.children = expanded_nodes
        return expanded_nodes

    def balance_goal_test(self):
        if (len(self.ship.bay) == 0):
            return True
        elif((self.get_port_mass() >= (self.get_starboard_mass() * 0.9)) and
                (self.get_port_mass() <= (self.get_starboard_mass() * 1.1))):
                return True
        return False

    def SIFT_goal_test(self, goal_grid):
        for i in range(0, len(goal_grid)):
            if ((self.ship.grid[i].name != goal_grid[i].name) and
                (self.ship.grid[i].weight != goal_grid[i].weight)):
                return False
        return True

    def __lt__(self, other):
        return self.cost < other.cost

def select_best_balance_children(weights, unique_weights, attempted_distances, attempted_nodes):
    best_nodes = []
    for weight in unique_weights:
            indicies = []
            for idx, value in enumerate(weights):
                if value == weight:
                    indicies.append(idx)
            curr_distances = []
            curr_min_distance = 99999
            curr_min_idx = -1
            for idx in indicies:
                if attempted_distances[idx] < curr_min_distance:
                    curr_min_distance = attempted_distances[idx]
                    curr_min_idx = idx
            best_nodes.append(attempted_nodes[curr_min_idx])
    return best_nodes

def get_SIFT_goal_state(ship):
    # Hard-coded as all expected ship sizes have 12 columns.
    column_order = [6, 7, 5, 8, 4, 9, 3, 10, 2, 11, 1, 12]

    goal_grid = copy.deepcopy(ship.grid)
    sorted_containers = queue.Queue()
    for y in range(ship.height - 1, -1, -1):
        for x in range(0, ship.width):
            index = x + (y*12)
            curr_container = goal_grid[index]
            if ((curr_container.name != "UNUSED") and (curr_container.name != "NAN")):
                curr_container.name = "UNUSED"
                curr_container.weight = 0
    
    tmp_bay = copy.deepcopy(ship.bay)

    heaviest_container  = None
    heaviest_weight     = 0
    while (len(tmp_bay) != 0):
        i = len(tmp_bay) - 1
        while (i >= 0):
            if (tmp_bay[i].weight > heaviest_weight):
                heaviest_container  = tmp_bay[i]
                heaviest_weight     = heaviest_weight
            i -= 1

        sorted_containers.put(heaviest_container)    
        tmp_bay.remove(heaviest_container)
        heaviest_container  = None
        heaviest_weight     = 0

    row = 1
    i = 0
    while (sorted_containers.empty() == False):
        index = ((column_order[i]) -1) + ((row -1) * 12)
        curr_pos = goal_grid[index]
        if (curr_pos.name == "UNUSED"):
            curr_container  = sorted_containers.get()
            curr_pos.name   = curr_container.name
            curr_pos.weight = curr_container.weight
        i += 1
        if (i >= 12):
            i = 0
            row += 1
        
    return goal_grid

def queueing_function(nodes):
    nodes.sort(key=lambda x: x.fn)
    return nodes

def traceback_solution(terminal_node):
    traceback_queue = queue.LifoQueue()
    ret_node_path   = []

    curr_node = terminal_node
    traceback_queue.put(curr_node)
    while(curr_node.parent != None):
        traceback_queue.put(curr_node.parent)
        curr_node = curr_node.parent

    while(traceback_queue.empty() == False):
        curr_node = traceback_queue.get()
        print(curr_node.ship)
        print(curr_node.operation)
        print('')
        ret_node_path.append(curr_node)

    return ret_node_path

def is_full_ship(ship):
    for i in range(len(ship.grid)):
        if ship.grid[i].name == "UNUSED":
            return False
    return True

def on_off_load(ship):  # general search
    count = 0
    global onlist
    global offlist
    # onlist = [Container(9, 1, 120, "test1")]     # list of containers
    # offlist = [24]    # index (int) in grid
    print(len(onlist))
    print(len(offlist))
    if is_full_ship(ship) and len(onlist) > 0:
        text_display_str = "Can't load to full ship"
        text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
        return
    global on_off_nodes
    new_grid = copy.deepcopy(ship.grid)
    on_off_nodes = [OnOffNode(new_grid, onlist, offlist, None, "Start On/Offload", 0, 0)]
    node = on_off_nodes.pop(0)
    while not OnOff_goal_test(node):
        expanded_nodes = node.expand()    # 2 operations so 2 new nodes
        for i in range(len(expanded_nodes)):
            on_off_nodes.append(expanded_nodes[i])

        on_off_nodes = queueing_function(on_off_nodes)
        node = on_off_nodes.pop(0)

    operation_sequence = ""
    result_nodes = []
    while node != None:
        operation_sequence = node.operation + "\n" + operation_sequence
        result_nodes.insert(0, node)
        node = node.parent
    onlist = []
    offlist = []
    print(operation_sequence)
    return result_nodes

def balance_ship_SIFT(init_ship_state):
    node            = BalanceNode(init_ship_state)
    node.operation  = "Start balancing, SIFT required!"
    frontier        = PriorityQueue()
    explored        = []
    max_queue_size  = 0
    expand_count    = 0
    max_depth       = 0
    goal_grid       = get_SIFT_goal_state(init_ship_state)

    frontier.put(node)
    while (frontier.qsize() > 0):
        if (frontier.empty()):
            print("ERROR: Failure.")
            return False
        node = frontier.get()
        if (node.SIFT_goal_test(goal_grid)):
            return traceback_solution(node)

        explored.append(node.ship.grid)
        node_children = node.expand_SIFT(goal_grid)

        expand_count    += 1
        max_queue_size  = max(max_queue_size, frontier.qsize())
        max_depth       = max(max_depth, node.depth)

        # Check if children already explored
        # If not explored, put into frontier.
        for child_node in node_children:
            state_found = True
            for curr_grid in explored:
                for i in range(0, len(curr_grid)):
                    if( (curr_grid[i].name != child_node.ship.grid[i].name )and 
                        (curr_grid[i].weight != child_node.ship.grid[i].weight)):
                        state_found = False
                if (state_found == False):
                    frontier.put(child_node)
            else:
                pass

def balance_ship(init_ship_state):
    node            = BalanceNode(init_ship_state)
    frontier        = PriorityQueue()
    explored        = []
    max_queue_size  = 0
    expand_count    = 0
    max_depth       = 0

    frontier.put(node)
    while (frontier.qsize() > 0):
        if (frontier.empty()):
            print("ERROR: Failure.")
            return False
        node = frontier.get()
        if (node.balance_goal_test()):
            # Found solution!
            # Return sequence of operations.
            return traceback_solution(node)
        
        to_explored = []
        to_explored.append(node.get_port_containers())
        to_explored.append(node.get_starboard_containers())

        explored.append(to_explored)
        arr_accessable_containers   = node.accessable_containers()
        # Expand node and get children.
        node_children = []

        for container in arr_accessable_containers:
            node_children += node.expand(container)

        expand_count    += 1
        max_queue_size  = max(max_queue_size, frontier.qsize())
        max_depth       = max(max_depth, node.depth)

        # Check if children already explored
        # If not explored, put into frontier.
        for child_node in node_children:
            to_explored = []
            to_explored.append(child_node.get_port_containers())
            to_explored.append(child_node.get_starboard_containers())

            state_found = False
            for state in explored:
                if ((state[0] == to_explored[0]) and (state[1] == to_explored[1])):
                    state_found = True
            if (state_found == False):
                frontier.put(child_node)
            else:
                pass
    # If this point is reach, SIFT needs to be conducted.
    return balance_ship_SIFT(init_ship_state)

def draw_grid(grid):
    for i in range(8):
        for j in range(12):
            row = i
            if j > 5:
                col = j+1
            else:
                col = j
            if grid[i*12+j].name == "NAN":
                button = Button(bg="#000000", width=6, height=3).grid(row=8-row, column=col, padx=0.5, pady=0.5)
            elif grid[i*12+j].name == "UNUSED":
                button = Button(bg="#969696", width=6, height=3).grid(row=8-row, column=col,  padx=0.5,pady=0.5)
            else:
                button = Button(text=grid[i*12+j].name, bg="#eb755e", fg="#ffffff", width=6, height=3, command=lambda index=i*12+j: add_to_offload(grid, index)).grid(row=8-row, column=col, padx=0.5,pady=0.5)
    midline = Label(text="", bg="#3498eb", height=31).grid(row=1, rowspan=8, column=6)

def display_buffer():
    midline = Label(text="Buffer:").grid(row=11, column=0)
    temp = Frame(root)
    temp.grid(row=12, column=0, columnspan=15)
    for i in range(4):
        for j in range(24):
            button = Button(temp, bg="#969696", width=4, height=2).grid(row=12+4-i, column=j, padx=0.5, pady=0.5)

def run_load(ship):
    global next_btn
    global open_btn
    global run_OnOffload
    global run_balance
    
    global mode
    global solution_nodes
    global init_ship_state
    global curr_load_node
    global text_display_str

    mode = 1
    with open(".cache/mode.txt", 'wb') as pickle_file:
        pickle.dump(mode, pickle_file)
    solution_nodes = on_off_load(init_ship_state)
    with open(".cache/solution_nodes.txt", 'wb') as pickle_file:
        pickle.dump(solution_nodes, pickle_file)
    bay = []
    grid = []
    grid = solution_nodes[len(solution_nodes)-1].grid
    for i in range(len(grid)):
        if grid[i].name != "NAN" and grid[i].name != "UNUSED":
            bay.append(grid[i])
    init_ship_state = Ship(12, 8, grid, bay)
    curr_load_node = 0
    with open(".cache/curr_load_node.txt", 'wb') as pickle_file:
        pickle.dump(curr_load_node, pickle_file)
    draw_grid(solution_nodes[curr_load_node].grid)

    text_display_str = solution_nodes[curr_load_node].operation
    text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
    print(solution_nodes[curr_load_node].operation.split(" ")[0])

    run_OnOffload = Button(text="Run On/Offload", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_OnOffload.grid(row=3, column=14, padx=7)
    run_balance = Button(text="Run Balance", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_balance.grid(row=3, column=15, padx=7)

    next_btn = Button(text="Next", bg="#e0e0e0", fg="#000000", width=10, height=1, command=next_operation)
    next_btn.grid(row=10, column=15, padx=7, pady=2)
    open_btn = Button(text='Open Manifest', bg="#909090", fg="#000000", width=15, height=1, command=None)
    open_btn.grid(row=2, column=17, padx=1, sticky=N)

def run_balancing(ship):
    global next_btn
    global open_btn
    global port_mass_label
    global starboard_mass_label

    global mode
    global solution_nodes
    global init_ship_state
    global curr_load_node
    global text_display_str

    mode = 2
    with open(".cache/mode.txt", 'wb') as pickle_file:
        pickle.dump(mode, pickle_file)
    solution_nodes = balance_ship(init_ship_state)
    with open(".cache/solution_nodes.txt", 'wb') as pickle_file:
        pickle.dump(solution_nodes, pickle_file)
    bay = []
    grid = []
    grid = solution_nodes[len(solution_nodes)-1].grid
    for i in range(len(grid)):
        if grid[i].name != "NAN" and grid[i].name != "UNUSED":
            bay.append(grid[i])
    init_ship_state = Ship(12, 8, grid, bay)
    curr_load_node = 0
    with open(".cache/curr_load_node.txt", 'wb') as pickle_file:
        pickle.dump(curr_load_node, pickle_file)
    draw_grid(solution_nodes[curr_load_node].grid)
    
    text_display_str = solution_nodes[curr_load_node].operation
    text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)

    port_mass = solution_nodes[curr_load_node].get_port_mass()  # TODO: put actual port mass
    port_mass_label.configure(text="Port Mass: "+str(port_mass), fg="#000000", width=20, font=("Arial", 10))
    starboard_mass = solution_nodes[curr_load_node].get_starboard_mass()  # TODO: put actual starboard mass
    starboard_mass_label.configure(text="Starboard Mass: "+ str(starboard_mass), fg="#000000", width=20, font=("Arial", 10))

    run_OnOffload = Button(text="Run On/Offload", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_OnOffload.grid(row=3, column=14, padx=7)
    run_balance = Button(text="Run Balance", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_balance.grid(row=3, column=15, padx=7)

    next_btn = Button(text="Next", bg="#e0e0e0", fg="#000000", width=10, height=1, command=next_operation)
    next_btn.grid(row=10, column=15, padx=7, pady=2)
    open_btn = Button(text='Open Manifest', bg="#909090", fg="#000000", width=15, height=1, command=None)
    open_btn.grid(row=2, column=17, padx=1, sticky=N)

# TODO: In both next_operation() and back_operation(), the Back button doesn't properly get updated.
def next_operation():
    global curr_load_node
    global solution_nodes
    global finish_flag
    global back_btn
    global next_btn
    
    if len(solution_nodes) == 0:
        return

    curr_load_node += 1
    if (curr_load_node == 0):
        back_btn = Button(text="Back", bg="#909090", fg="#000000", width=10, height=1, command=None)
        back_btn.grid(row=10, column=14, padx=7, pady=2)
    else:
        back_btn = Button(text="Back", bg="#e0e0e0", fg="#000000", width=10, height=1, command=back_operation)
        back_btn.grid(row=10, column=14, padx=7, pady=2)

    with open(".cache/curr_load_node.txt", 'wb') as pickle_file:
        pickle.dump(curr_load_node, pickle_file)
    if curr_load_node >= len(solution_nodes):
        finish_flag = True
        curr_load_node = len(solution_nodes)
        text_display = Label(text="Done", height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)

        next_btn = Button(text="Finish", bg="#e0e0e0", fg="#000000", width=10, height=1, command=reset_operation)
        next_btn.grid(row=10, column=15, padx=7)
        return

    draw_grid(solution_nodes[curr_load_node].grid)
    global text_display_str
    text_display_str = solution_nodes[curr_load_node].operation
    text_display_str = "Estimated Time: " + str(solution_nodes[curr_load_node].estimated_time)+" minutes\n"+solution_nodes[curr_load_node].operation
    text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
    if mode == 2:
        port_mass = solution_nodes[curr_load_node].get_port_mass()  # TODO: put actual port mass
        port_mass_label = Label(text="Port Mass: "+str(port_mass), fg="#000000", width=20, font=("Arial", 10)).grid(row=9, columnspan=6, column=0)
        starboard_mass = solution_nodes[curr_load_node].get_starboard_mass()  # TODO: put actual starboard mass
        starboard_mass_label = Label(text="Starboard Mass: "+ str(starboard_mass), fg="#000000", width=20, font=("Arial", 10)).grid(row=9, columnspan=6, column=6)
    if solution_nodes[curr_load_node].operation.split(" ")[0] == "Load":
        temp = solution_nodes[curr_load_node].operation.split(" ")[1] + " is onloaded.\n"
        addLogComment(temp)
    elif solution_nodes[curr_load_node].operation.split(" ")[0] == "Remove":
        temp = solution_nodes[curr_load_node].operation.split(" ")[1] + " is offloaded.\n"
        addLogComment(temp)

def back_operation():
    global curr_load_node
    global solution_nodes
    global text_display_str
    global finish_flag
    
    global back_btn
    global next_btn
    global port_mass_label
    global starboard_mass_label

    if (finish_flag == True):
        finish_flag = False
        next_btn.configure(text="Next", bg="#e0e0e0", fg="#000000", width=10, height=1, command=next_operation)

    if len(solution_nodes) == 0:
        return
        
    curr_load_node -= 1
    if (curr_load_node == 0):
        back_btn = Button(text="Back", bg="#909090", fg="#000000", width=10, height=1, command=None)
        back_btn.grid(row=10, column=14, padx=7, pady=2)
    else:
        back_btn = Button(text="Back", bg="#e0e0e0", fg="#000000", width=10, height=1, command=back_operation)
        back_btn.grid(row=10, column=14, padx=7, pady=2)

    if curr_load_node == 0:
        text_display_str = solution_nodes[curr_load_node].operation
        text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
        draw_grid(solution_nodes[curr_load_node].grid)
        return
    elif curr_load_node < 0:
        curr_load_node = 0
        with open(".cache/curr_load_node.txt", 'wb') as pickle_file:
            pickle.dump(curr_load_node, pickle_file)
        return
    draw_grid(solution_nodes[curr_load_node].grid)
    text_display_str = solution_nodes[curr_load_node].operation
    text_display_str = "Estimated Time: "+ str(solution_nodes[curr_load_node].estimated_time)+" minutes\n"+solution_nodes[curr_load_node].operation
    text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
    if mode == 2:
        port_mass = solution_nodes[curr_load_node].get_port_mass()  # TODO: put actual port mass
        port_mass_label.configure(text="Port Mass: "+str(port_mass), fg="#000000", width=20, font=("Arial", 10))
        starboard_mass = solution_nodes[curr_load_node].get_starboard_mass()  # TODO: put actual starboard mass
        starboard_mass_label.configure(text="Starboard Mass: "+ str(starboard_mass), fg="#000000", width=20, font=("Arial", 10))

def reset_operation():
    global root
    global init_ship_state
    global manifest_name
    global buffer
    global solution_nodes
    global curr_load_node
    global onlist
    global offlist
    global mode
    global finish_flag
    global reload

    global next_btn
    global back_btn
    global port_mass_label
    global starboard_mass_label

    updateManifest()
    for f in glob.glob(".cache/*"):
        os.remove(f)
    pop_up_reminder()  

    init_ship_state = initialize_empty_ship()
    manifest_name = ''
    solution_nodes = []
    curr_load_node = 0
    onlist = []
    offlist = []
    mode = 1
    finish_flag = False
    reload = False

    back_btn = Button(text="Back", bg="#909090", fg="#000000", width=10, height=1, command=None)
    back_btn.grid(row=10, column=14, padx=7, pady=2)
    next_btn = Button(text="Next", bg="#909090", fg="#000000", width=10, height=1, command=None)
    next_btn.grid(row=10, column=15, padx=7, pady=2)
    open_btn = Button(text='Open Manifest', bg="#e0e0e0", fg="#000000", width=15, height=1, command=loadShip)
    open_btn.grid(row=2, column=17, padx=1, sticky=N)


    draw_grid(init_ship_state.grid)
    port_mass = "0"
    port_mass_label.configure(text="Port Mass: "+port_mass, fg="#000000", width=20, font=("Arial", 10))
    starboard_mass = "0"
    starboard_mass_label.configure(text="Starboard Mass: "+starboard_mass, fg="#000000", width=20, font=("Arial", 10))

    root.title("Empty Ship")

def print_on_off_list(grid):
    global onlist
    global offlist
    global text_display_str
    text_display_str = "Onlist: "
    for i in range(len(onlist)):
        text_display_str += "\t"+onlist[i].name + ", "
    text_display_str += "\nOfflist: "
    for i in range(len(offlist)):
        text_display_str += "\t"+grid[offlist[i]].name + ", "
    text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)

def add_to_onload(grid, input):
    global onlist
    if input.get() == "":
        text_display_str = "Input can't be empty!!!"
        text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
        return
    info = input.get().split(",")
    if len(info) != 2:
        text_display_str = "Either information missing or incorrect input format!"
        text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)
        return

    w = info[1].strip(" ")

    if not w.isdigit():
        if w[0] == "-" and w[1].isdigit():
            pass
        else:
            pop_up(2)
            return
    if int(w) < 0 or int(w) > 99999:
        pop_up(3)
        return

    print(w, info[0])
    onlist.append(Container(9, 1, int(w), info[0]))
    with open(".cache/onlist.txt", 'wb') as pickle_file:
        pickle.dump(onlist, pickle_file)
    input.delete(0, END)
    print_on_off_list(grid)

def add_to_offload(grid, index):
    global offlist
    print(index)
    offlist.append(index)
    with open(".cache/offlist.txt", 'wb') as pickle_file:
        pickle.dump(offlist, pickle_file)
    print_on_off_list(grid)

def log_out():
    global username
    global root
    comment = username + " signs out\n"
    addLogComment(comment)
    root.destroy()
    login_window()

def interface(ship):
    global submit_comment
    global run_OnOffload
    global run_balance
    global back_btn
    global next_btn
    global open_btn
    global port_mass_label
    global starboard_mass_label
    
    global root
    global empty_ship
    global finish_flag
    global text_display_str
    text_display_str = ""
    
    root = Tk()
    root.title("Empty Ship")
    draw_grid(ship.grid)

    port_mass = "0"
    port_mass_label = Label(text="Port Mass: "+port_mass, fg="#000000", width=20, font=("Arial", 10))
    port_mass_label.grid(row=9, columnspan=6, column=0)

    starboard_mass = "0"
    starboard_mass_label = Label(text="Starboard Mass: "+starboard_mass, fg="#000000", width=20, font=("Arial", 10))
    starboard_mass_label.grid(row=9, columnspan=6, column=6)

    midline = Label(text="", height=31, width=5).grid(row=1, rowspan=8, column=13)
    onload_entry_hint = Label(text="Add Containers(Name, Weight):", width=24, font=("Arial", 10)).grid(row=1, column=14, sticky=S)
    entry = Entry(width=40)
    entry_display = entry.grid(row=2, column=14, padx=1, sticky=N)

    comment = Text(height=10, width=50, bg="#ffffff")
    comment_display = comment.grid(row=6, rowspan=3, column=14, columnspan=3, padx=7)
    submit_comment = Button(text="Comment", bg="#e0e0e0", fg="#000000", width=10, height=1, command=lambda: [addLogComment(comment.get(1.0, END)), comment.delete(1.0, END)])
    submit_comment.grid(row=8, column=17, padx=7, pady=2)
    
    run_OnOffload = Button(text="Run On/Offload", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_OnOffload.grid(row=3, column=14, padx=7)
    run_balance = Button(text="Run Balance", bg="#909090", fg="#000000", width=15, height=1, command=None)
    run_balance.grid(row=3, column=15, padx=7)

    remove_onlist = Button(text="Romove from Onlist", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: remove_window(1))
    remove_onlist.grid(row=4, column=17, padx=7, pady=2)
    remove_offlist = Button(text="Romove from Offlist", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: remove_window(2))
    remove_offlist.grid(row=5, column=17, padx=7, pady=2)

    log_out_btn = Button(text="Log Out", bg="#9c261e", fg="#ffffff", width=10, height=1, command= lambda: log_out()).grid(row=1, column=17, padx=5, pady=5, sticky = NE)

    if (reload == False):
        back_btn = Button(text="Back", bg="#909090", fg="#000000", width=10, height=1, command=None)
        back_btn.grid(row=10, column=14, padx=7, pady=2)

        next_btn = Button(text="Next", bg="#909090", fg="#000000", width=10, height=1, command=None)
        next_btn.grid(row=10, column=15, padx=7)

        open_btn = Button(text='Open Manifest', bg="#e0e0e0", fg="#000000", width=15, height=1, command=loadShip)
        open_btn.grid(row=2, column=17, padx=1, sticky=N)
        add_onload_btn = Button(text="Add To Onload", bg="#909090", fg="#000000", width=15, height=1).grid(row=2, column=15, padx=1, sticky=N)

    else:
        if (curr_load_node == 0):
            back_btn = Button(text="Back", bg="#909090", fg="#000000", width=10, height=1, command=None)
        else:
            back_btn = Button(text="Back", bg="#e0e0e0", fg="#000000", width=10, height=1, command=back_operation)
        back_btn.grid(row=10, column=14, padx=7, pady=2)

        next_btn = Button(text="Next", bg="#e0e0e0", fg="#000000", width=10, height=1, command=next_operation)
        next_btn.grid(row=10, column=15, padx=7)

        open_btn = Button(text='Open Manifest', bg="#909090", fg="#000000", width=15, height=1, command=None)
        open_btn.grid(row=2, column=17, padx=1, sticky=N)
        add_onload_btn = Button(text="Add To Onload", bg="#e0e0e0", fg="#000000", width=15, height=1, command=lambda: add_to_onload(ship.grid, entry)).grid(row=2, column=15, padx=1, sticky=N)


    display_buffer()
    global solution_nodes
    if len(solution_nodes) > 0:
        text_display_str = solution_nodes[curr_load_node].operation
        text_display_str = "Estimated Time: " + str(solution_nodes[curr_load_node].estimated_time)+" minutes\n"+solution_nodes[curr_load_node].operation
        text_display = Label(text=text_display_str, height=6, width=50, bg="#f7faf0").grid(row=4, rowspan=2, column=14, columnspan=3, padx=7)

    root.mainloop()

def remove_window(mode):
    global remove_win
    remove_win = Tk()
    remove_win.geometry("450x100")
    username_hint = Label(remove_win, text="Enter the index of the container you want to remove from the list\n(from 0 to the size of the list):", width=50, font=("Arial", 10)).pack()
    entry = Entry(remove_win, width=40)
    entry_display = entry.pack()
    if(mode == 1):
        submit_btn = Button(remove_win, text="Submit", bg="#e0e0e0", fg="#000000", width=10, height=1, command=lambda: remove_from_onlist(entry)).pack()
    elif(mode == 2):
        submit_btn = Button(remove_win, text="Submit", bg="#e0e0e0", fg="#000000", width=10, height=1, command=lambda: remove_from_offlist(entry)).pack()
    remove_win.mainloop()

def remove_from_onlist(input):
    global remove_win
    global onlist
    global init_ship_state
    index = int(input.get())
    onlist.pop(index)
    remove_win.destroy()
    print_on_off_list(init_ship_state.grid)

def remove_from_offlist(input):
    global remove_win
    global offlist
    global init_ship_state
    index = int(input.get())
    offlist.pop(index)
    remove_win.destroy()
    print_on_off_list(init_ship_state.grid)


def updateManifest():
    global manifest_name
    desktop = os.path.expanduser("~\Desktop\\")
    filename = desktop+manifest_name+"OUTBOUND.txt"
    print(filename)
    f = open(filename, "w")
    global init_ship_state
    grid = init_ship_state.grid
    for i in range(len(grid)):
        temp = str(grid[i])+"\n"
        f.write(temp)
    f.close()

def pop_up_reminder():
    comment = "Finish a cycle. Manifest " + manifest_name + "OUTBOUND.txt was written to desktop, and a reminder pop-up to operator to send file was displayed\n"
    addLogComment(comment)
    tkinter.messagebox.showinfo("Done", "Done! Please don't forget to send the manifest.")

def pop_up(mode):
    if mode == 1: #empty string in comment
        tkinter.messagebox.showinfo("Warning", "Comment can't be empty")
    if mode == 2: #weight is not int
        tkinter.messagebox.showinfo("Warning", "Weight must be integer")
    if mode == 3: #with range
        tkinter.messagebox.showinfo("Warning", "Weight must be in range 0-99999")
    if mode == 4: #empty username
        tkinter.messagebox.showinfo("Warning", "Name entry can't be empty")

def clearCache():
    for f in glob.glob(".cache/*"):
        os.remove(f)

def restore():
    global init_ship_state
    global manifest_name
    global buffer
    global solution_nodes
    global curr_load_node
    global onlist
    global offlist
    global mode
    global empty_ship
    global reload
    empty_ship = False
    reload = True

    with open(".cache/manifest_name.txt", 'rb') as pickle_file:
        manifest_name = pickle.load(pickle_file)
    with open(".cache/solution_nodes.txt", 'rb') as pickle_file:
        solution_nodes = pickle.load(pickle_file)
    with open(".cache/curr_load_node.txt", 'rb') as pickle_file:
        curr_load_node = pickle.load(pickle_file)

    if (curr_load_node >= len(solution_nodes)):
        curr_load_node = len(solution_nodes) - 1

    with open(".cache/mode.txt", 'rb') as pickle_file:
        mode = pickle.load(pickle_file)

    if (mode == 1):
        with open(".cache/onlist.txt", 'rb') as pickle_file:
            onlist = pickle.load(pickle_file)
        with open(".cache/offlist.txt", 'rb') as pickle_file:
            offlist = pickle.load(pickle_file)

        init_ship_state = Ship(12, 8, solution_nodes[curr_load_node].grid, [])
        pass

    elif (mode == 2):
        init_ship_state = solution_nodes[curr_load_node].ship
    # If we end up using the buffer at any point, save buffer to .txt file, and load it with pickle
    buffer = initialize_empty_buffer()

    with open("log.txt", 'a') as f:
        f.write(str(datetime.now().strftime("%B %d %Y: %H:%M"))+" Recovered from crash!\n")

def login_window():
    global window
    window = Tk()
    window.geometry("300x100")
    window.title("Log In")
    username_hint = Label(text="Please type in your name:", width=24, font=("Arial", 10)).grid(row=1, column=0)
    entry = Entry(width=40)
    entry_display = entry.grid(row=2, column=0, padx=20)
    login_btn = Button(text="Log In", bg="#e0e0e0", fg="#000000", width=10, height=1, command=lambda: log_in(entry)).grid(row=3, column=0, sticky=S, pady=10)
    window.mainloop()

def log_in(name):
    global username
    global window
    global init_ship_state
    global reload
    if name.get() == "":
        pop_up(4)
        return
    else:
        username = name.get()
        name.delete(0, END)
        comment = username + " signs in\n"
        addLogComment(comment)
        window.destroy()

        cache_files = os.listdir(".cache")
        if (len(cache_files) != 0):
            restore()
            interface(solution_nodes[curr_load_node])
        else:
            reload = False
            init_ship_state = initialize_empty_ship()
            interface(init_ship_state)

def main():
    global init_ship_state
    global manifest_name
    global buffer
    global solution_nodes
    global curr_load_node
    global onlist
    global offlist
    global mode
    global finish_flag
    global reload
    global username
    username = ""
    finish_flag = False
    solution_nodes = []
    # onlist = []
    # offlist = []
    login_window()



    #signout()

main()

