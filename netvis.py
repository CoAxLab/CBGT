from tkinter import filedialog
from tkinter import *
import math
import random

node_map = {}
link_map = {}
cvs_map = {}

root = Tk()

cvs_width = 1000
cvs_height = 600

show_all_lbls = BooleanVar()

def get(i):
    if i in node_map:
        return node_map[i]
    node_map[i] = Node(i)
    return node_map[i]

class Node():
    i = None
    x = None
    y = None
    cvs_obj = None
    cvs_lbl = None
    def __init__(self, i):
        self.i = i
    def label(self):
        return "   " + str(self.i)

class Link():
    link_name = None
    from_node = None
    to_node = None
    cvs_obj = None
    cvs_lbl = None
    lbl_rnd = 0.5
    def __init__(self, link_name, from_node_i, to_node_i):
        self.link_name = link_name
        self.from_node = get(from_node_i)
        self.to_node = get(to_node_i)
    def label(self):
        return self.link_name

Label(root,
      text="""NODES""",
      justify = LEFT,
      padx = 100).pack()

drag_item = None
mouse_dx = 0
mouse_dy = 0

def press(event):
    global mouse_dy
    global mouse_dx
    global drag_item
    canvas = event.widget
    mouse_x = canvas.canvasx(event.x)
    mouse_y = canvas.canvasy(event.y)
    s = canvas.find_closest(mouse_x, mouse_y)[0]
    # print (s,mouse_x,mouse_y)
    drag_item = cvs_map[s]
    if type(drag_item) is Node:
        mouse_dx = mouse_x - drag_item.x
        mouse_dy = mouse_y - drag_item.y
    render()
    render_hlght(drag_item)

def rightpress(event):
    render()

def drag(event):
    global mouse_dy
    global mouse_dx
    global drag_item
    canvas = event.widget
    mouse_x = canvas.canvasx(event.x)
    mouse_y = canvas.canvasy(event.y)
    if type(drag_item) is Node:
        drag_item.x = mouse_x - mouse_dx
        drag_item.y = mouse_y - mouse_dy
        render()
        render_hlght(drag_item)

def release(event):
    global drag_item
    if type(drag_item) is Node:
        for key,link in link_map.items():
            if link.to_node is drag_item or link.from_node is drag_item:
               link.lbl_rnd = None
    drag_item = None

canvas = Canvas(root, width=cvs_width, height=cvs_height, borderwidth=0, highlightthickness=0, bg="white")
canvas.bind("<ButtonPress-1>", press)
canvas.bind("<ButtonPress-3>", rightpress)
canvas.bind("<B1-Motion>", drag)
canvas.bind("<ButtonRelease-1>", release)
canvas.pack()

def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
Canvas.create_circle = _create_circle

def fix_boundaries(val):
    border = 10
    if val.x < border:
        val.x = border
    if val.y < border:
        val.y = border
    if val.x > cvs_width - border*2:
        val.x = cvs_width - border*2
    if val.y > cvs_height - border:
        val.y = cvs_height - border

def render_hlght(val):
    if type(val) is Node:
        canvas.delete(val.cvs_obj)
        obj = canvas.create_circle(val.x, val.y, 7, fill="red", outline="")
        val.cvs_obj = obj
        cvs_map[obj] = val
        for key,link in link_map.items():
            if link.to_node is val or link.from_node is val:
               render_hlght(link)
    if type(val) is Link:
        canvas.delete(val.cvs_obj)
        canvas.delete(val.cvs_lbl)
        if val.lbl_rnd == None:
            val.lbl_rnd = random.uniform(0.3,0.7)
        lbl = canvas.create_text(val.from_node.x*val.lbl_rnd + val.to_node.x*(1-val.lbl_rnd) - 20,
                                 val.from_node.y*val.lbl_rnd + val.to_node.y*(1-val.lbl_rnd),text=val.label(),anchor="w")
        val.cvs_lbl = lbl
        cvs_map[lbl] = val
        obj = canvas.create_line(val.from_node.x, val.from_node.y,
                                 val.to_node.x, val.to_node.y, fill="blue", dash=(8, 8))
        val.cvs_obj = obj
        cvs_map[obj] = val

def render():
    global cvs_map
    global canvas
    global show_all_lbls
    canvas.delete("all")
    cvs_map = {}
    for key,val in node_map.items():
        fix_boundaries(val)
        obj = canvas.create_circle(val.x, val.y, 5, fill="green", outline="")
        val.cvs_obj = obj
        cvs_map[obj] = val
        lbl = canvas.create_text(val.x, val.y,text=val.label(),anchor="w")
        val.cvs_lbl = lbl
        cvs_map[lbl] = val
    for key,val in link_map.items():
        obj = canvas.create_line(val.from_node.x, val.from_node.y,
                                 val.to_node.x, val.to_node.y, fill="red", dash=(4, 4))
        val.cvs_obj = obj
        cvs_map[obj] = val
        if show_all_lbls.get()== 1:
            if val.lbl_rnd == None:
                val.lbl_rnd = random.uniform(0.3,0.7)
            lbl = canvas.create_text(val.from_node.x*val.lbl_rnd + val.to_node.x*(1-val.lbl_rnd) - 20,
                                     val.from_node.y*val.lbl_rnd + val.to_node.y*(1-val.lbl_rnd),text=val.label(),anchor="w")
            val.cvs_lbl = lbl
            cvs_map[lbl] = val


def openfile():
    root.filename =  filedialog.askopenfilename(title = "Select file",filetypes = (("CSV/AUX","*.csv *.aux"),("all files","*.*")))
    #print (root.filename)
    fh = open(root.filename,"r")
    lines = fh.readlines()
    for i in range(len(lines)):
        if i > 0:
            (link_name,from_node_i,to_node_i) = lines[i].strip().split(",")
            #print(link_name + "," + from_node_i + "," + to_node_i)
            link_map[link_name] = Link(link_name, from_node_i, to_node_i)

    index = 0
    index_map = {}
    def dfs(node):
        nonlocal index_map
        nonlocal index
        if not node in index_map:
            index_map[node] = index
            index = index + 1
            for key,link in link_map.items():
                if link.to_node is node:
                    dfs(link.from_node)
                if link.from_node is node:
                    dfs(link.to_node)

    for key,node in node_map.items():
        dfs(node)

    max_index = len(node_map)
    for key,val in node_map.items():
        val.x = math.ceil(cvs_width * (0.5 + .4 * math.cos(2.0 * math.pi * index_map[val] / max_index)))
        val.y = math.ceil(cvs_height * (0.5 - .4 * math.sin(2.0 * math.pi * index_map[val] / max_index)))
        #print(str(key), "=>", str(val.x), str(val.y))
    render()

menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=openfile)
#filemenu.add_command(label="Save", command=savefile)
#filemenu.add_separator()
#filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
viewmenu = Menu(menubar, tearoff=0)
viewmenu.add_checkbutton(label="Show All Labels", onvalue=1, offvalue=False, variable=show_all_lbls, command=render)
menubar.add_cascade(label="View", menu=viewmenu)
root.config(menu=menubar)

openfile()

mainloop()
