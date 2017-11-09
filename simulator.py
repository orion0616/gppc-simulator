import time
import threading
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

def convert_points(line):
    return list(map(lambda s: list(map(int, s[1:].split(","))), line.split(")")[:-1]))

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
        ".": Qt.white,
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
        self.initUI()

    def initUI(self):
        next_button = QPushButton('Next', self)
        prev_button = QPushButton('Prev', self)
        play_button = QPushButton('Play', self)
        next_button.resize(next_button.sizeHint())
        prev_button.resize(prev_button.sizeHint())
        play_button.resize(play_button.sizeHint())
        next_button.move(0, self.height + 50)
        prev_button.move(80, self.height + 50)
        play_button.move(160, self.height + 50)
        next_button.clicked.connect(self.next_clicked)
        prev_button.clicked.connect(self.prev_clicked)
        play_button.clicked.connect(self.play_multi)

        self.setGeometry(0, 0, self.width + 50, self.height+100)
        self.setWindowTitle('Points')
        self.show()

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
        self.qp.setPen(self.color_map["EXPANDED"])
        for expanded in self.expanded:
            self.qp.drawPoint(expanded[0], expanded[1])

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
        self.expanded = []
        for node in expanded:
            self.expanded.append(node)
            time.sleep(0.02)
            self.update()

    def play_multi(self):
        threading.Thread(target=self.play_clicked, name="a").start()

def main():
    mapfile, paths = parse_path()
    map_data = load_map(mapfile)
    app = QApplication(sys.argv)
    window = Window(0, map_data, paths)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
