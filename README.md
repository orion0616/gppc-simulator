# GPPC Path Simulator
[![CircleCI](https://circleci.com/gh/orion46/gppc-simulator.svg?style=svg)](https://circleci.com/gh/orion46/gppc-simulator)

<img width="270" height="400" alt="simulator-image" src="https://user-images.githubusercontent.com/10744451/31373119-c1201044-add3-11e7-9ec1-5d72ad35dad2.png" align="left" />

GPPC([Grid-Based Path Planning Competition](http://movingai.com/GPPC/)) is a competition of grid-based path planning.
GPPC Path Simulator is a simulator that validates and shows solutions of problems.
If you give this simulator a path as input, you can see a graphical map, path, and a result of its validaty.

## Install
Run this code on your terminal.
```
git clone git@github.com:orion46/gppc-simulator.git
```

## How to use it
```
python simulator.py PATHFILE
```

## A format of path file
In the first line, one string is given. It's a map file name

In the following lines, each line has one path. Paths' format are like below.
```
(1,2)(2,3)(3,4)(4,5)
```
