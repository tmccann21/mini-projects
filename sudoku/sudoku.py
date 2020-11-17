"""
The Sudoku Problem Formulation for the PuLP Modeller
Authors: Antony Phillips, Dr Stuart Mitchell
edited by Nathan Sudermann-Merx
adapted by Trevor McCann for magic square sudoku
"""

# Import PuLP modeler functions
from pulp import *
import math

# All rows, columns and values within a Sudoku take values from 1 to 9
VALS = ROWS = COLS = DIAGONAL = range(1, 10)

# The boxes list is created, with the row and column index of each square in each box
BOXES = [
    [(3*i+k+1, 3*j+l+1) for k in range(3) for l in range(3)]
    for i in range(3) for j in range(3)
]

# The prob variable is created to contain the problem data        
prob = LpProblem("magic_square_sudoku")

# A dictionary of the decision variables for each cell
choices = LpVariable.dicts("choice", (VALS, ROWS, COLS), cat="Binary")

# Decision variable for the sum of the magic square
magic_square = LpVariable("magic_square_sum", cat="Integer")

# A constraint ensuring that only one value can be in each square is created
for r in ROWS:
    for c in COLS:
        prob += lpSum([choices[r][c][v] for v in VALS]) == 1

# The row, column and box constraints are added for each value
for v in VALS:
    for r in ROWS:
        prob += lpSum([choices[r][c][v] for c in COLS]) == 1
        
    for c in COLS:
        prob += lpSum([choices[r][c][v] for r in ROWS]) == 1

    for b in BOXES:
        prob += lpSum([choices[r][c][v] for (r, c) in b]) == 1

# Each major diagonal contains only one of each value
for v in VALS:
    prob += lpSum([choices[d][d][v] for d in DIAGONAL]) == 1
    prob += lpSum([choices[10 - d][d][v] for d in DIAGONAL]) == 1

# The sum of each row, column and diagonal of the magic square is the same
for r in range(3):
    prob += lpSum([v * choices[4 + r][4 + c][v] for v in VALS for c in range(3)] + (magic_square * -1)) == 0

for c in range(3):
    prob += lpSum([v * choices[4 + r][4 + c][v] for v in VALS for r in range(3)] + (magic_square * -1)) == 0

prob += lpSum([v * choices[4 + d][4 + d][v] for d in range(3) for v in VALS] + (magic_square * -1)) == 0
prob += lpSum([v * choices[6 - d][4 + d][v] for d in range(3) for v in VALS] + (magic_square * -1)) == 0

# Each of the valid knights moves
KNIGHTS_MOVES = [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2)]
knights_move_constraint_count = 0

# Helper function to avoid invalid indices as well as a small optimization to avoid checking knight's moves
# in the same 3x3 square
def isUsefulKnightsMove(r, c, r_off, c_off):
    r_tgt = r + r_off
    c_tgt = c + c_off

    return (1 <= r_tgt <= 9
        and 1 <= c_tgt <= 9
        and (math.ceil(r / 3) != math.ceil(r_tgt / 3) or math.ceil(c / 3) != math.ceil(c_tgt / 3 )))

# Create the knight's moves constraints
for r in ROWS:
    for c in COLS:
        for (r_off, c_off) in KNIGHTS_MOVES:
            if isUsefulKnightsMove(r, c, r_off, c_off):
                for v in VALS:
                    expr = [choices[r][c][v], choices[r + r_off][c + c_off][v]]
                    prob += lpSum(expr) <= 1
                    knights_move_constraint_count += 1

# The starting numbers are entered as constraints

prob += choices[4][1][3] == 1
prob += choices[4][2][8] == 1
prob += choices[4][3][4] == 1

prob += choices[9][9][2] == 1

# The problem data is written to an .lp file
prob.writeLP("MagicSquare.lp")

# The problem is solved using PuLP"s choice of Solver
prob.solve()

# The status of the solution is printed to the screen
print("Status:", LpStatus[prob.status])

sudokuout = open("sudokuout.txt","w")

for r in ROWS:
    if r in [1, 4, 7]:
        sudokuout.write("+-------+-------+-------+\n")
    for c in COLS:
        for v in VALS:
            if value(choices[r][c][v]) == 1:
                if c in [1, 4, 7]:
                    sudokuout.write("| ")
                sudokuout.write(str(v) + " ")
                if c == 9:
                    sudokuout.write("|\n")

sudokuout.write("+-------+-------+-------+\n\n")
sudokuout.write("Magic Square Sum: " + str(value(magic_square)) + "\n")
sudokuout.write("Knights Move Constraints: " + str(knights_move_constraint_count) + "\n")
sudokuout.write("Total Constraints: " + str(len(prob.constraints)) + "\n")
sudokuout.close()

# The location of the solution is give to the user
print("Solution Written to sudokuout.txt")

#
# Solution to the Magic Square Sudoku:
#
#     +-------+-------+-------+
#     | 8 4 3 | 5 6 7 | 2 1 9 |
#     | 2 7 5 | 9 1 3 | 8 4 6 |
#     | 6 1 9 | 4 2 8 | 3 7 5 |
#     +-------+-------+-------+
#     | 3 8 4 | 6 7 2 | 9 5 1 |
#     | 7 2 6 | 1 5 9 | 4 8 3 |
#     | 9 5 1 | 8 3 4 | 6 2 7 |
#     +-------+-------+-------+
#     | 5 3 7 | 2 8 6 | 1 9 4 |
#     | 4 6 2 | 7 9 1 | 5 3 8 |
#     | 1 9 8 | 3 4 5 | 7 6 2 |
#     +-------+-------+-------+
#
