# Sliding Puzzle Solver

### Introduction

This Python script is made for solving sliding puzzle game. But this version of the sliding puzzle is slightly different than the traditional one. In this version, tile sizes of the sliding puzzle can be different.

```
1 1 0 2 2
1 1 0 2 2
3 3 3 0 0
3 3 3 0 0
3 3 3 4 4
```

```
0 1 1 2 2
0 1 1 2 2
3 3 3 0 0
3 3 3 0 0
3 3 3 4 4
```
Two example states are given above. Every number block is creating one tile. Like in the traditional sliding puzzle, if tile is colliding with other tiles after making the move, we do not allow this move. In the example, 1's block in the first board made one right move and created the second board state.

### Starting

```
python a_star.py inp_file
```

All the states of the board while the reaching the one of the given final states will be printed out as an output.


Example input file is like the following:
```
0 // if number is zero, used heuristic is Manhattan Distance, if number is 1, used heuristic is Misplaced Tiles.
4 3 3 1 // first number is number of column, second number is number of row, third number is number of pieces and last number is number of given final states.
S // State of the initial board
0 0 0
1 2 0
0 3 3
0 3 3
F // State of the one of the candidate final boards
3 3 0
3 3 0
2 0 0
1 0 0
F // State of the one of the candidate final boards
3 3 0
3 3 0
2 0 0
0 1 0
```

Partial output for the given example input above:
```
0 0 0
1 2 0
0 3 3
0 3 3

0 0 0
0 2 0
1 3 3
0 3 3

...
...

0 3 3
0 3 3
2 0 0
1 0 0

3 3 0
3 3 0
2 0 0
1 0 0
```