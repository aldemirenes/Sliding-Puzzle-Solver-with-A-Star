from Queue import PriorityQueue
from copy import copy
import sys
import time

class Piece(object):
    def __init__(self, piece_row, piece_column, start_x, start_y, pid, max_row, max_column):
        self.piece_row = piece_row
        self.piece_column = piece_column
        self.start_x = start_x
        self.start_y = start_y
        self.pid = pid
        self.max_row = max_row
        self.max_column = max_column

    def print_piece(self):
        print "pid: " + str(self.pid), self.start_x, self.start_y, self.piece_column, self.piece_row

    def is_identical(self, other_piece):
        if self.pid == other_piece.pid and \
           self.piece_row == other_piece.piece_row and \
           self.piece_column == other_piece.piece_column and \
           self.start_x == other_piece.start_x and \
           self.start_y == other_piece.start_y:
            return True
        else:
            return False

    def collision_check(self, piece2):
        #return true if two pieces are colliding.
        piece1_start_x = self.start_x
        piece1_end_x = piece1_start_x + self.piece_column-1
        piece1_start_y = self.start_y
        piece1_end_y = piece1_start_y + self.piece_row-1

        piece2_start_x = piece2.start_x
        piece2_end_x = piece2_start_x + piece2.piece_column-1
        piece2_start_y = piece2.start_y
        piece2_end_y = piece2_start_y + piece2.piece_row-1


        if (piece1_end_x >= piece2.start_x and
            piece1_start_x <= piece2_end_x and
            piece1_start_y <= piece2_end_y and
            piece1_end_y >= piece2_start_y):
            return True
        else:
            return False


    def is_in_board(self):
        #method for checking whether moved tile is on the board
        start_x = self.start_x
        start_y = self.start_y
        end_x = start_x + self.piece_column - 1
        end_y = start_y + self.piece_row - 1
        if (end_y < self.max_row and start_y >= 0) and \
           (end_x < self.max_column and start_x >= 0):
            return True
        else:
            return False

    def move_right(self):
        return Piece(piece_row = self.piece_row,
                     piece_column = self.piece_column,
                     start_x = self.start_x+1,
                     start_y = self.start_y,
                     pid = self.pid,
                     max_row = self.max_row,
                     max_column = self.max_column)

    def move_left(self):
        return Piece(piece_row = self.piece_row,
                     piece_column = self.piece_column,
                     start_x = self.start_x-1,
                     start_y = self.start_y,
                     pid = self.pid,
                     max_row = self.max_row,
                     max_column = self.max_column)

    def move_up(self):
        return Piece(piece_row = self.piece_row,
                     piece_column = self.piece_column,
                     start_x = self.start_x,
                     start_y = self.start_y-1,
                     pid = self.pid,
                     max_row = self.max_row,
                     max_column = self.max_column)

    def move_down(self):
        return Piece(piece_row = self.piece_row,
                     piece_column = self.piece_column,
                     start_x = self.start_x,
                     start_y = self.start_y+1,
                     pid = self.pid,
                     max_row = self.max_row,
                     max_column = self.max_column)

class Board(object):
    def __init__(self, final_states, pieces, parent, which_heuristic, row_num, column_num):
        if which_heuristic == "M":
            self.h_func = self.compute_manhattan_distance
        elif which_heuristic == "H":
            self.h_func = self.compute_hamming_sum
        self.which_heuristic = which_heuristic
        self.final_states = final_states
        self.pieces = pieces
        self.f_value = 0
        self.g_value = 0
        #initially only find h_value for first final state, finding h_value for other final states is done in the expand method
        self.h_value = self.h_func(final_states[0])
        self.parent = parent
        self.row_num = row_num
        self.column_num = column_num

    def compute_manhattan_distance(self, final_state):
        manhattan_distance = 0
        for pid in self.pieces.keys():
            piece_start_x = self.pieces[pid].start_x
            final_start_x = final_state[pid].start_x

            piece_start_y = self.pieces[pid].start_y
            final_start_y = final_state[pid].start_y

            distance_x = abs(piece_start_x - final_start_x)
            distance_y = abs(piece_start_y - final_start_y)

            manhattan_distance +=  (distance_x + distance_y)

        return manhattan_distance


    def compute_hamming_sum(self, final_state):
        hamming_sum = 0
        for pid in self.pieces.keys():
            if not self.pieces[pid].is_identical(final_state[pid]):
                hamming_sum += 1

        return hamming_sum

    def is_identical(self, other_board):
        #check whether two board states are identical or not.
        for pid in self.pieces.keys():
            if not self.pieces[pid].is_identical(other_board[pid]):
                return False

        return True

    def does_collide_with_others(self, checking_piece):
        #check whether two board is colliding or not.
        for piece in self.pieces.values():
            if checking_piece.collision_check(piece) and \
               not piece.pid == checking_piece.pid :
                return True

        return False

    def is_legal_move(self, moved_piece, pid):
        if not self.does_collide_with_others(moved_piece) and moved_piece.is_in_board():
            #for creating two different objects, copy function is used
            changed_pieces = copy(self.pieces)
            changed_pieces[pid] = moved_piece
            new_board = Board(final_states = self.final_states,
                              pieces = changed_pieces,
                              parent = self,
                              which_heuristic = self.which_heuristic,
                              row_num = self.row_num,
                              column_num = self.column_num)
            return new_board

        return None


    def expand(self):
        result_boards = []
        #every piece is moved to the 4 directions and created search space with different boards.
        #h_value is found for every new state.
        for pid in self.pieces.keys():
            moved_right = self.pieces[pid].move_right()
            result = self.is_legal_move(moved_right, pid)
            if not result ==  None:
                result.g_value = self.g_value+1
                for final_state in self.final_states:
                    new_h_value = self.h_func(final_state)
                    if new_h_value < result.h_value:
                        result.h_value = new_h_value
                result.f_value = result.g_value + result.h_value
                result_boards.append(result)

            moved_left = self.pieces[pid].move_left()
            result = self.is_legal_move(moved_left, pid)
            if not result == None:
                result.g_value = self.g_value+1
                for final_state in self.final_states:
                    new_h_value = self.h_func(final_state)
                    if new_h_value < result.h_value:
                        result.h_value = new_h_value
                result.f_value = result.g_value + result.h_value
                result_boards.append(result)

            moved_up = self.pieces[pid].move_up()
            result = self.is_legal_move(moved_up, pid)
            if not result == None:
                result.g_value = self.g_value+1
                for final_state in self.final_states:
                    new_h_value = self.h_func(final_state)
                    if new_h_value < result.h_value:
                        result.h_value = new_h_value
                result.f_value = result.g_value + result.h_value
                result_boards.append(result)

            moved_down = self.pieces[pid].move_down()
            result = self.is_legal_move(moved_down, pid)
            if not result == None:
                result.g_value = self.g_value+1
                for final_state in self.final_states:
                    new_h_value = self.h_func(final_state)
                    if new_h_value < result.h_value:
                        result.h_value = new_h_value
                result.f_value = result.g_value + result.h_value
                result_boards.append(result)

        return result_boards

    def is_in_list(self, search_list):
        for board in search_list:
            if self.is_identical(board.pieces):
                return {"res":True, "f_value":board.f_value}

        return {"res":False, "f_value":None}

    def print_board(self):
        state_matrix = []
        for i in range(0, self.row_num):
            temp_row = []
            for j in range(0, self.column_num):
                temp_row.append(0)
            state_matrix.append(temp_row)

        for pid in self.pieces.keys():
            piece_start_x = self.pieces[pid].start_x
            piece_start_y = self.pieces[pid].start_y
            piece_row_num = self.pieces[pid].piece_row
            piece_column_num = self.pieces[pid].piece_column
            for x in range(piece_start_x, piece_start_x + piece_column_num):
                for y in range(piece_start_y, piece_start_y + piece_row_num):
                    state_matrix[y][x] = pid

        output = ""
        for curr_row in state_matrix:
            for curr_column in curr_row:
                output += str(curr_column) + " "
            output += "\n"
        print output


def A_star(board):
    open_list = PriorityQueue()
    open_list.put((board.f_value, board))
    closed = []

    while not open_list.empty():
        curr_board = open_list.get()[1] #getting board with minimum f_value
        closed.append(curr_board)
        for final_state in curr_board.final_states:
            if curr_board.is_identical(final_state):
                return curr_board
        #new board state will be generated, and
        #every new state will be checked whether new state is on closed_list and open_list
        expanded = curr_board.expand()
        for generated_board in expanded:
            result_dict = generated_board.is_in_list(closed)
            is_in_closed = result_dict["res"]
            f_value = result_dict["f_value"]

            open_list_converted = [b for (a, b) in open_list.queue]
            result_dict = generated_board.is_in_list(open_list_converted)
            is_in_open = result_dict["res"]
            f_value = result_dict["f_value"]

            if not is_in_closed and not is_in_open:
                open_list.put((generated_board.f_value, generated_board))

    return "failure"



def construct_initial_boards(start_matrix, final_matrixes, piece_amount, row, column, which_heuristic):
    pieces_start_matrix = {}
    for i in range(1, piece_amount+1):
        pieces_start_matrix[i] = Piece(piece_row = 0,
                                       piece_column = 0,
                                       start_x = None,
                                       start_y = None,
                                       pid = i,
                                       max_row = row,
                                       max_column = column)

    for y in range(0, row):
        for x in range(0, column):
            piece_num = start_matrix[y][x]
            if piece_num == 0:
                continue

            if pieces_start_matrix[piece_num].start_x == None:
                pieces_start_matrix[piece_num].start_x = x
            if pieces_start_matrix[piece_num].start_y == None:
                pieces_start_matrix[piece_num].start_y = y

            if x > pieces_start_matrix[piece_num].piece_column:
                pieces_start_matrix[piece_num].piece_column = x
            if y > pieces_start_matrix[piece_num].piece_row:
                pieces_start_matrix[piece_num].piece_row = y


    for piece_num in range(1, piece_amount+1):
        pieces_start_matrix[piece_num].piece_column -= pieces_start_matrix[piece_num].start_x
        pieces_start_matrix[piece_num].piece_column += 1
        pieces_start_matrix[piece_num].piece_row -= pieces_start_matrix[piece_num].start_y
        pieces_start_matrix[piece_num].piece_row += 1


    pieces_final_matrixes = []
    for k in range(0, len(final_matrixes)):
        current_final_matrix = final_matrixes[k]
        pieces_final_matrix = {}
        for i in range(1, piece_amount+1):
            pieces_final_matrix[i] = Piece(piece_row = 0,
                                           piece_column = 0,
                                           start_x = None,
                                           start_y = None,
                                           pid = i,
                                           max_row = row,
                                           max_column = column)
        for y in range(0, row):
            for x in range(0, column):
                piece_num = current_final_matrix[y][x]
                if piece_num == 0:
                    continue

                if pieces_final_matrix[piece_num].start_x == None:
                    pieces_final_matrix[piece_num].start_x = x
                if pieces_final_matrix[piece_num].start_y == None:
                    pieces_final_matrix[piece_num].start_y = y

                if x > pieces_final_matrix[piece_num].piece_column:
                    pieces_final_matrix[piece_num].piece_column = x
                if y > pieces_final_matrix[piece_num].piece_row:
                    pieces_final_matrix[piece_num].piece_row = y

        for piece_num in range(1, piece_amount+1):
                pieces_final_matrix[piece_num].piece_column -= pieces_final_matrix[piece_num].start_x
                pieces_final_matrix[piece_num].piece_column += 1
                pieces_final_matrix[piece_num].piece_row -= pieces_final_matrix[piece_num].start_y
                pieces_final_matrix[piece_num].piece_row += 1

        pieces_final_matrixes.append(pieces_final_matrix)

    return Board(final_states = pieces_final_matrixes,
                 pieces = pieces_start_matrix,
                 parent = None,
                 which_heuristic = which_heuristic,
                 row_num = row,
                 column_num = column)

if __name__== '__main__':
    fp = open(sys.argv[1], "r")
    heuristic = int(fp.readline().strip())
    temp = [int(i) for i in fp.readline().strip().split()]
    row_num = temp[0]
    column_num = temp[1]
    piece_num = temp[2]
    final_matrixes_num = temp[3]
    start_matrix = []
    final_matrixes = []
    fp.readline()
    for _ in range(0, row_num):
        temp_row = [int(i) for i in fp.readline().strip().split()]
        start_matrix.append(temp_row)
    for _ in range(0, final_matrixes_num):
        temp_final_matrix = []
        fp.readline()
        for _ in range(0, row_num):
            temp_row = [int(i) for i in fp.readline().strip().split()]
            temp_final_matrix.append(temp_row)
        final_matrixes.append(temp_final_matrix)

    if heuristic == 0:
        heuristic_char = "M"
    if heuristic == 1:
        heuristic_char = "H"

    board = construct_initial_boards(start_matrix, final_matrixes, piece_num, row_num, column_num, heuristic_char)
    result = A_star(board)

    result_list = []
    if result == "failure":
        print "failure"
        sys.exit()

    #beginning from final state, solution path is transferred to result list
    while not result == None:
        result_list.append(result)
        result = result.parent
    while not len(result_list) == 0:
              temp_result = result_list.pop()
              temp_result.print_board()
