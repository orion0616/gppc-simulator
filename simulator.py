import time
import sys
import threading
from PIL import Image
from PIL import ImageTk
import numpy as np
import tkinter as tk

def convert_points(line):
    return list(map(lambda s: list(map(int,s[1:].split(","))), line.split(")")[:-1]))

def parse_path():
    filename = sys.argv[1]
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    mapfile = lines[0].strip()
    paths = list(map(convert_points, lines[1:]))
    return (mapfile, paths)

def get_expanded(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    expanded = list(map(convert_points, lines))
    return expanded[0]


def load_map(mapfile):
    with open(mapfile, 'r') as fin:
        lines = fin.readlines()
    mapData = list(map(lambda line: line.strip(), lines[4:]))
    h = int(lines[1].split(" ")[1])
    w = int(lines[2].split(" ")[1])
    assert len(mapData) == h and len(mapData[0]) == w, "Check map size"
    return mapData

def draw_path(map_array, path):
    for step in path:
        map_array[step[1]][step[0]] = [255, 0, 0];
    return map_array

def upsize_image(image):
    img_array = np.asarray(image)
    height = len(img_array)
    width =  len(img_array[0])

    if height >= 400 or width >= 600:
        return image
    img_array.flags.writeable = True
    zipped = np.array(list(zip(img_array, img_array)))
    horizontal_double = np.array(list(map(lambda c: np.ndarray.flatten(np.array(list(zip(c[0],c[1])))), zipped))).reshape(height,width*2,3)
    doubled = np.ndarray.flatten(np.array(list(zip(horizontal_double,horizontal_double)))).reshape(height*2,width*2,3)
    return upsize_image(Image.fromarray(doubled, "RGB"))

def create_image(map_data, path):
    color_map = {".": [255, 255, 255],
                "G": [255, 255, 255],
                "@": [  0,   0,   0],
                "O": [  0,   0,   0],
                "T": [  0, 255,   0],
                "S": [142,   0, 204],
                "W": [ 25, 135,  22]
                }
    # had better to resize when its size is too small.
    map_array = np.uint8(list(map(lambda s: list(map(lambda c: color_map[c], s)), map_data)))
    
    if path is not None:
        map_array = draw_path(map_array, path)

    image = Image.fromarray(map_array, "RGB")
    # image = upsize_image(image)
    return image

def create_image_with_expanded(map_data, path, expanded):
    color_map = {".": [255, 255, 255],
                "G": [255, 255, 255],
                "@": [  0,   0,   0],
                "O": [  0,   0,   0],
                "T": [  0, 255,   0],
                "S": [142,   0, 204],
                "W": [ 25, 135,  22]
                }
    # had better to resize when its size is too small.
    map_array = np.uint8(list(map(lambda s: list(map(lambda c: color_map[c], s)), map_data)))

    for step in expanded:
        map_array[step[1]][step[0]] = [255, 160, 160];
    if path is not None:
        map_array = draw_path(map_array, path)

    image = Image.fromarray(map_array, "RGB")
    # image = upsize_image(image)
    return image

def add_an_expand_to_image(image, point):
    image.putpixel((point[0],point[1]),(255,160,160))
    return image

def validate_path(mapData, path):
    for (i, step) in enumerate(path):
        x = path[i][0]
        y = path[i][1]
        # detect range error
        if 0 > x or 0 > y or x >= len(mapData[0]) or y >= len(mapData):
            sys.stderr.write("Out of range\n")
            return False
        # detect unpermmited area
        info = mapData[y][x]
        if info == "@" or info == "O" or info == "T" or info == "W":
            sys.stderr.write("Located at unpermitted area\n")
            return False

        if i == 0:
            continue
        # detect illegal move
        dx = x - path[i-1][0]
        dy = y - path[i-1][1]
        if abs(dx) > 1 or abs(dy) > 1:
            sys.stderr.write("Illegal move\n")
            return False
    return True

def button_pressed(label, num, mapData, paths, isNext):
    print("a")
    if isNext:
        photo = ImageTk.PhotoImage(create_image(mapData, paths[300]))
        label.image = photo
    else:
        photo = ImageTk.PhotoImage(create_image(mapData, paths[300]))
        label.image = photo

class Frame(tk.Frame):
    def __init__(self,num, mapData, paths):
        tk.Frame.__init__(self, None)
        self.master.title("GPPC Simulator")
        self.num = num
        self.mapData = mapData
        self.paths = paths
        f_button = tk.Frame(self)
        f_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        self.buff = tk.StringVar()
        self.buff.set("Hello")
        self.statusbar = tk.Label(self, textvariable = self.buff)
        self.statusbar.pack(side=tk.BOTTOM)

        if validate_path(self.mapData, self.paths[self.num]):
            self.cache = create_image(self.mapData, self.paths[self.num])
            self.image = ImageTk.PhotoImage(self.cache)
            self.show_valid()
        else:
            self.cache = create_image(self.mapData, None)
            self.image = ImageTk.PhotoImage(self.cache)
            self.show_invalid()
        self.label = tk.Label(self, image=self.image)
        self.label.pack()

        next_button = tk.Button(f_button, text="Next", command=self.next_image)
        prev_button = tk.Button(f_button, text="Prev", command=self.prev_image)
        play_button = tk.Button(f_button, text="Play", command=self.play_multi)
        next_button.pack(side = tk.LEFT)
        prev_button.pack(side = tk.LEFT)
        play_button.pack(side = tk.LEFT)

        self.now = tk.StringVar()
        self.now.set(str(self.num+1))
        self.entry = tk.Entry(f_button, textvariable = self.now)
        self.entry.pack(side = tk.LEFT)
        self.entry.bind('<Return>', self.move)

        self.size = tk.StringVar()
        self.size.set("/ " + str(len(paths)))
        self.denominator = tk.Label(f_button, textvariable = self.size)
        self.denominator.pack(side = tk.LEFT)
        
    def move(self, event):
        if self.now.get():
            value = eval(self.now.get())
            if value < 1 or value > len(self.paths):
                self.now.set("invalid number")
                self.cache = create_image(self.mapData, None)
                self.image = ImageTk.PhotoImage(self.cache)
                self.label.config(image = self.image)
                self.show_invalid()
                return
            self.now.set(str(value))
            self.num = value-1
            self.validate_and_show()

    def validate_and_show(self):
        if validate_path(self.mapData, self.paths[self.num]):
            self.cache = create_image(self.mapData, self.paths[self.num])
            self.image = ImageTk.PhotoImage(self.cache)
            self.label.config(image = self.image)
            self.show_valid()
        else:
            self.cache = create_image(self.mapData, None)
            self.image = ImageTk.PhotoImage(self.cache)
            self.label.config(image = self.image)
            self.show_invalid()

    def next_image(self):
        if self.num == len(self.paths)-1:
            self.num = 0
        else:
            self.num += 1
        self.now.set(str(self.num+1))
        self.validate_and_show()

    def prev_image(self):
        if self.num == 0:
            self.num = len(self.paths) - 1
        else:
            self.num -= 1
        self.now.set(str(self.num+1))
        self.validate_and_show()

    def play_multi(self):
        threading.Thread(target=self.play, name="a").start()

    def play(self):
        pre = "-".join(sys.argv[1].split("-")[:-1])
        filename = "expanded/" + pre + "-" + str(self.num) + "-expanded.txt"
        expanded = get_expanded(filename)
        self.cache = create_image(self.mapData, None)
        self.image = ImageTk.PhotoImage(self.cache)
        self.label.config(image = self.image)
        for i in range(len(expanded)):
            self.cache = add_an_expand_to_image(self.cache, expanded[i:i+1][0])
            self.image = ImageTk.PhotoImage(self.cache)
            # self.image = ImageTk.PhotoImage(create_image_with_expanded(self.mapData, None, expanded[:i]))
            self.label.config(image = self.image)
            time.sleep(0.005)
        self.image = ImageTk.PhotoImage(create_image_with_expanded(self.mapData, self.paths[self.num], expanded))
        self.label.config(image = self.image)


    def show_valid(self):
        self.buff.set("Valid Path")

    def show_invalid(self):
        self.buff.set("Invalid Path")

def main():
    mapfile, paths = parse_path()
    mapData = load_map(mapfile)
    f = Frame(0, mapData, paths)
    f.pack()
    f.mainloop()

if __name__ == "__main__":
    main()
