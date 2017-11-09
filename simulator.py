import time
import threading
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

class Point:
    def __init__(self, x, y, f = 0, g = 0, h = 0):
        self.x = x
        self.y = y
        self.f = f
        self.g = g
        self.h = h

def convert_to_points(line):
    return list(map(lambda s: list(map(int, s[1:].split(","))), line.split(")")[:-1]))

def convert_expanded_to_points(line):
    # like [[1,2],[2,3]]
    lists = list(map(lambda s: list(map(float, s[1:].split(","))), line.split(")")[:-1]))
    return list(map(lambda p: Point(p[0], p[1], p[2], p[3], p[4]),lists))

def parse_path():
    filename = sys.argv[1]
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    mapfile = lines[0].strip()
    paths = list(map(convert_to_points, lines[1:]))
    return (mapfile, paths)

def get_expanded(filename):
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    # expanded = list(map(convert_to_points, lines))
    expanded = list(map(convert_expanded_to_points, lines))
    return expanded[0]

def load_map(mapfile):
    with open(mapfile, 'r') as fin:
        lines = fin.readlines()
    mapData = list(map(lambda line: line.strip(), lines[4:]))
    h = int(lines[1].split(" ")[1])
    w = int(lines[2].split(" ")[1])
    assert len(mapData) == h and len(mapData[0]) == w, "Check map size"
    return mapData

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

class Window(QWidget):
    color_map = {
        ".": QColor.fromRgb(255,255,255),
        "G": Qt.white,
        "@": Qt.black,
        "O": Qt.black,
        "T": Qt.green,
        "S": Qt.magenta,
        "W": Qt.cyan,
        "PATH": Qt.red,
        "EXPANDED": Qt.gray
    }

    def __init__(self, num, map_data, paths):
        super().__init__()
        self.num = num
        self.map_data = map_data
        self.height = len(map_data)
        self.width = len(map_data[0])
        self.paths = paths
        self.expanded = []
        self.maxvalue = 0
        self.initUI()

    def initUI(self):
        self.setButton('Next', 0, self.height + 50, self.next_clicked)
        self.setButton('Prev', 80, self.height + 50, self.prev_clicked)
        self.setButton('f-value', 0, self.height + 100, self.play_f)
        self.setButton('g-value', 80, self.height + 100, self.play_g)
        self.setButton('h-value', 160, self.height + 100, self.play_h)

        self.setGeometry(0, 0, self.width + 80, self.height+160)
        self.setWindowTitle('Points')
        self.show()

    def setButton(self, name, x, y, connect):
        button = QPushButton(name, self)
        button.resize(button.sizeHint())
        button.move(x, y)
        button.clicked.connect(connect)

    def paintEvent(self, e):
        self.qp = QPainter()
        self.qp.begin(self)
        self.draw_map()
        self.qp.end()

    def draw_map(self):
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[0])):
                self.qp.setPen(self.color_map[self.map_data[y][x]])
                self.qp.drawPoint(x, y)
        if self.validate():
            self.draw_expanded()
            self.draw_path()

    def draw_path(self):
        self.qp.setPen(self.color_map["PATH"])
        for step in self.paths[self.num]:
            self.qp.drawPoint(step[0], step[1])

    def draw_expanded(self):
        for expanded in self.expanded:
            if self.maxvalue == 0:
                self.maxvalue = 255
            if self.mode == "f":
                rate = expanded.f/self.maxvalue
            if self.mode == "g":
                rate = expanded.g/self.maxvalue
            if self.mode == "h":
                rate = expanded.h/self.maxvalue
            red   = 255 - 128*rate
            blue  = 255 - 255*rate
            green = 127 + 128*rate
            self.qp.setPen(QColor.fromRgb(red , blue, green))
            self.qp.drawPoint(expanded.x, expanded.y)

    def validate(self):
        return validate_path(self.map_data, self.paths[self.num])

    def next_clicked(self):
        self.expanded = []
        if self.num == len(self.paths)-1:
            self.num = 0
        else:
            self.num += 1
        self.update()

    def prev_clicked(self):
        self.expanded = []
        if self.num == 0:
            self.num = len(self.paths) - 1
        else:
            self.num -= 1
        self.update()

    def play_clicked(self):
        pre = "-".join(sys.argv[1].split("-")[:-1])
        filename = "expanded/" + pre + "-" + str(self.num) + "-expanded.txt"
        expanded = get_expanded(filename)
        if self.mode == "f":
            self.maxvalue = max(list(map(lambda lst: lst.f, expanded)))
        if self.mode == "g":
            self.maxvalue = max(list(map(lambda lst: lst.g, expanded)))
        if self.mode == "h":
            self.maxvalue = max(list(map(lambda lst: lst.h, expanded)))
        self.expanded = []
        for node in expanded:
            self.expanded.append(node)
            time.sleep(0.01)
            self.update()

    def play_f(self):
        self.mode = "f"
        threading.Thread(target=self.play_clicked, name="f").start()

    def play_g(self):
        self.mode = "g"
        threading.Thread(target=self.play_clicked, name="g").start()

    def play_h(self):
        self.mode = "h"
        threading.Thread(target=self.play_clicked, name="h").start()

def main():
    mapfile, paths = parse_path()
    map_data = load_map(mapfile)
    app = QApplication(sys.argv)
    window = Window(0, map_data, paths)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
