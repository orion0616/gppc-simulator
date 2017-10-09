from PIL import Image
import sys
import numpy as np

def convert_points(line):
    return list(map(lambda s: list(map(int,s[1:].split(","))), line.split(")")[:-1]))

def parse_path():
    filename = sys.argv[1]
    with open(filename, 'r') as fin:
        lines = fin.readlines()
    mapfile = lines[0].strip()
    paths = list(map(convert_points, lines[1:]))
    return (mapfile, paths) 

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

    if height > 600 or width > 1000:
        return image
    img_array.flags.writeable = True
    zipped = np.array(list(zip(img_array, img_array)))
    horizontal_double = np.array(list(map(lambda c: np.ndarray.flatten(np.array(list(zip(c[0],c[1])))), zipped))).reshape(height,width*2,3)
    doubled = np.ndarray.flatten(np.array(list(zip(horizontal_double,horizontal_double)))).reshape(height*2,width*2,3)
    return Image.fromarray(doubled, "RGB")

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

    map_array = draw_path(map_array, path)

    image = Image.fromarray(map_array, "RGB")
    image = upsize_image(image)
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

def main():
    mapfile, paths = parse_path()
    mapData = load_map(mapfile)

    # validate and simulate
    if (validate_path(mapData, paths[300])):
        image = create_image(mapData, paths[300])
        image.save("path.png")

if __name__ == "__main__":
    main()
