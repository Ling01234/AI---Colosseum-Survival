# Student agent: Add your own agent here
from copy import copy, deepcopy
from platform import node
from unittest.case import _BaseTestCaseContext
from agents.agent import Agent
from store import register_agent
import sys
import numpy as np
import time
import random


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

        self.opposites = {0: 2, 1: 3, 2: 0, 3: 1}
        self.directions = ((-1, 0), (0, 1), (1, 0), (0, -1))

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        # Get an array of all possible squares we can move to

        # time constraint
        global start_time
        start_time = time.time()
        global move_time
        move_time = 1.95

        moves = self.get_moves(chess_board, my_pos, max_step, adv_pos, [])
        final_moves = self.total_moves(moves, chess_board)

        ok_moves = self.remove_suicidal_moves(
            my_pos, adv_pos, chess_board, final_moves)

        # check if mating is possible
        mate = self.check_instant_win(
            my_pos, adv_pos, chess_board, final_moves)

        if len(mate) != 0:
            return mate[0]

        bad_move = self.remove_box_myself(my_pos, chess_board)
        if bad_move != 0 and bad_move in ok_moves:
            ok_moves.remove(bad_move)

        good_move = self.box_opponent(adv_pos, chess_board)
        if good_move != 0 and good_move in final_moves:
            return good_move

        if len(ok_moves) != 0:
            return random.choice(ok_moves)

        try:
            return random.choice(final_moves)
        except:
            return self.random_walk(my_pos, adv_pos, max_step, chess_board)

        for depth in range(100):
            score, move = self.alpha_beta(
                (my_pos, 1), chess_board, max_step, depth, -np.inf, np.inf)

            # save move on time out
            if move:
                bestscore, bestmove = score, move
                return bestmove

    def get_moves(self, chess_board, my_pos, max_step, adv_pos, moves):

        r, c = my_pos
        adv_r, adv_c = adv_pos

        moves.append(my_pos)

        # Check the right
        if (max_step != 0 and not chess_board[r, c, self.dir_map["r"]] and (r, c + 1) not in moves and not (adv_r == r and adv_c == c+1)):
            moves + self.get_moves(chess_board, (r, c + 1),
                                   max_step-1, adv_pos, moves)

        # Check the down
        if (max_step != 0 and not chess_board[r, c, self.dir_map["d"]] and (r + 1, c) not in moves and not (adv_r == r+1 and adv_c == c)):
            moves + self.get_moves(chess_board, (r + 1, c),
                                   max_step-1, adv_pos, moves)

        # Check the left
        if (max_step != 0 and not chess_board[r, c, self.dir_map["l"]] and (r, c - 1) not in moves and not (adv_r == r and adv_c == c-1)):
            moves + self.get_moves(chess_board, (r, c - 1),
                                   max_step-1, adv_pos, moves)

        # Check the up
        if (max_step != 0 and not chess_board[r, c, self.dir_map["u"]] and (r - 1, c) not in moves and not (adv_r == r-1 and adv_c == c)):
            moves + self.get_moves(chess_board, (r - 1, c),
                                   max_step-1, adv_pos, moves)

        return moves

    # --------------------------------------------------------------------------------------------------------------------------------------

    def random_walk(self, my_pos, adv_pos, max_step, chess_board):
        """
        Randomly walk to the next position in the board.

        Parameters
        ----------
        my_pos : tuple
            The position of the agent.
        adv_pos : tuple
            The position of the adversary.
        """
        ori_pos = deepcopy(my_pos)
        steps = np.random.randint(0, max_step + 1)
        # Random Walk
        for _ in range(steps):
            r, c = my_pos
            dir = np.random.randint(0, 4)
            m_r, m_c = ((-1, 0), (0, 1), (1, 0), (0, -1))[dir]
            my_pos = (r + m_r, c + m_c)

            # Special Case enclosed by Adversary
            k = 0
            while chess_board[r, c, dir] or my_pos == adv_pos:
                k += 1
                if k > 300:
                    break
                dir = np.random.randint(0, 4)
                m_r, m_c = ((-1, 0), (0, 1), (1, 0), (0, -1))[dir]
                my_pos = (r + m_r, c + m_c)

            if k > 300:
                my_pos = ori_pos
                break

        # Put Barrier
        dir = np.random.randint(0, 4)
        r, c = my_pos
        while chess_board[r, c, dir]:
            dir = np.random.randint(0, 4)

        return my_pos, dir

    # --------------------------------------------------------------------------------------------------------------------------------------

    # Returns the walls that are possible for a single square
    def check_wall(self, r, c, chess_board):
        possible_directions = []

        for my_dir in self.dir_map:
            if not chess_board[r, c, self.dir_map[my_dir]]:
                possible_directions.append(my_dir)

        return possible_directions

    def total_moves(self, moves, chess_board):
        final_moves = []

        for pos in moves:
            r, c = pos
            possible_directions = self.check_wall(r, c, chess_board)
            for direction in possible_directions:
                new_tuple = ((r, c), self.dir_map[direction])
                final_moves.append(new_tuple)

        return final_moves

    def check_instant_win(self, my_pos, adv_pos, chess_board, moves):
        mate = []
        for move in moves:
            pos, dir = move
            r, c = pos
            # Set the barrier to True
            chess_board[r, c, dir] = True
            # Set the opposite barrier to True
            move1 = self.directions[dir]
            chess_board[r + move1[0], c + move1[1], self.opposites[dir]] = True

            is_endgame, my_score, adv_score = self.check_endgame(
                chess_board, pos, adv_pos)
            if is_endgame and my_score > adv_score:
                mate.append(move)
                chess_board[r, c, dir] = False
                # Set the opposite barrier to True
                move1 = self.directions[dir]
                chess_board[r + move1[0], c + move1[1],
                            self.opposites[dir]] = False
                return mate
            # Set the barrier to True
            chess_board[r, c, dir] = False
            # Set the opposite barrier to True
            move1 = self.directions[dir]
            chess_board[r + move1[0], c + move1[1],
                        self.opposites[dir]] = False

        return []

    def check_endgame(self, chess_board, my_pos, adv_pos):
        """
        Check if the game ends and compute the current score of the agents.

        Returns
        -------
        is_endgame : bool
            Whether the game ends.
        player_1_score : int
            The score of player 1.
        player_2_score : int
            The score of player 2.
        """

        # Union-Find
        father = dict()
        for r in range(chess_board.shape[0]):
            for c in range(chess_board.shape[0]):
                father[(r, c)] = (r, c)

        def find(pos):
            if father[pos] != pos:
                father[pos] = find(father[pos])
            return father[pos]

        def union(pos1, pos2):
            father[pos1] = pos2

        for r in range(chess_board.shape[0]):
            for c in range(chess_board.shape[0]):
                for dir, move in enumerate(
                    ((-1, 0), (0, 1), (1, 0), (0, -1))[1:3]
                ):  # Only check down and right
                    if chess_board[r, c, dir+1]:
                        continue

                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(chess_board.shape[0]):
            for c in range(chess_board.shape[0]):
                find((r, c))

        p0_r = find(my_pos)
        p1_r = find(adv_pos)

        my_score = list(father.values()).count(p0_r)
        adv_score = list(father.values()).count(p1_r)

        if p0_r == p1_r:
            return False, my_score, adv_score
        player_win = None
        win_blocks = -1
        if my_score > adv_score:
            player_win = 0
            win_blocks = my_score
        elif my_score < adv_score:
            player_win = 1
            win_blocks = adv_score
        else:
            player_win = -1  # Tie

        return True, my_score, adv_score

    # --------------------------------------------------------------------------------------------------------------------------------------

    # Returns a number of walls around the player n squares away (ONLY RETURNS THE NUMBER OF OUTSIDE WALLS, NOT INSIDE ONES)

    def check_surrounding_outside_walls(self, my_pos, chess_board, n):
        count = 0
        startRow, startColumn = my_pos
        maxCoord = chess_board.shape[0]

        # Check top-right border + top square
        row = startRow - n
        column = startColumn
        cutoffCheck = 0
        while column < maxCoord and row >= 0 and column <= startColumn + n:
            if chess_board[row, column, 0]:
                count = count + 1

            column = column + 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startRow - n >= 0:
            count = count + 1

        # Check top-left border excluding top square
        row = startRow - n
        column = startColumn - 1
        cutoffCheck = 1
        while column >= 0 and row >= 0 and column >= startColumn - n:
            if chess_board[row, column, 0]:
                count = count + 1

            column = column - 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startRow - n >= 0:
            count = count + 1

        # Check right-up border + right square
        row = startRow
        column = startColumn + n
        cutoffCheck = 0
        while column < maxCoord and row >= 0 and row >= startRow - n:
            if chess_board[row, column, 1]:
                count = count + 1

            row = row - 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startColumn + n < maxCoord:
            count = count + 1

        # Check right-down border excluding right square
        row = startRow + 1
        column = startColumn + n
        cutoffCheck = 1
        while column < maxCoord and row < maxCoord and row <= startRow + n:
            if chess_board[row, column, 1]:
                count = count + 1

            row = row + 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startColumn + n < maxCoord:
            count = count + 1

        # Check bottom-right border + bottom square
        row = startRow + n
        column = startColumn
        cutoffCheck = 0
        while column < maxCoord and row < maxCoord and column <= startColumn + n:
            if chess_board[row, column, 2]:
                count = count + 1

            column = column + 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startRow + n < maxCoord:
            count = count + 1

        # Check bottom-left border excluding bottom square
        row = startRow + n
        column = startColumn - 1
        cutoffCheck = 1
        while column >= 0 and row < maxCoord and column >= startColumn - n:
            if chess_board[row, column, 2]:
                count = count + 1

            column = column - 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startRow + n < maxCoord:
            count = count + 1

        # Check left-up border + left square
        row = startRow
        column = startColumn - n
        cutoffCheck = 0
        while column >= 0 and row >= 0 and row >= startRow - n:
            if chess_board[row, column, 3]:
                count = count + 1

            row = row - 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startColumn - n >= 0:
            count = count + 1

        # Check left-down border excluding left square
        row = startRow + 1
        column = startColumn - n
        cutoffCheck = 1
        while column >= 0 and row < maxCoord and row <= startRow + n:
            if chess_board[row, column, 3]:
                count = count + 1

            row = row + 1
            cutoffCheck = cutoffCheck + 1

        # Need this to check if one side got cut off early (check ipad for further explanation)
        if cutoffCheck - 1 != n and startColumn - n >= 0:
            count = count + 1

        return count
    # Returns a number of walls around the player n squares away (ONLY RETURNS THE NUMBER OF INSIDE WALLS, NOT OUTSIDE ONES)

    def check_surrounding_inside_walls(self, my_pos, chess_board, n):
        count = 0
        startRow, startColumn = my_pos
        maxCoord = chess_board.shape[0]

        # Check top-right border
        row = startRow - n
        column = startColumn + 1
        while column < maxCoord and row >= 0 and column <= startColumn + n:
            # Check the left border
            if chess_board[row, column, 3]:
                count = count + 1

            column = column + 1

        # Check top-left border
        row = startRow - n
        column = startColumn - 1

        while column >= 0 and row >= 0 and column >= startColumn - n:
            # Check the right border
            if chess_board[row, column, 1]:
                count = count + 1

            column = column - 1

        # Check right-up border
        row = startRow - 1
        column = startColumn + n

        while column < maxCoord and row >= 0 and row >= startRow - n:
            # Check the bottom border
            if chess_board[row, column, 2]:
                count = count + 1

            row = row - 1

        # Check right-down border
        row = startRow + 1
        column = startColumn + n

        while column < maxCoord and row < maxCoord and row <= startRow + n:
            # Check the top border
            if chess_board[row, column, 0]:
                count = count + 1

            row = row + 1

        # Check bottom-right border
        row = startRow + n
        column = startColumn + 1
        cutoffCheck = 0
        while column < maxCoord and row < maxCoord and column <= startColumn + n:
            # Check the left border
            if chess_board[row, column, 3]:
                count = count + 1

            column = column + 1

        # Check bottom-left border
        row = startRow + n
        column = startColumn - 1

        while column >= 0 and row < maxCoord and column >= startColumn - n:
            # Check the right border
            if chess_board[row, column, 1]:
                count = count + 1

            column = column - 1

        # Check left-up border
        row = startRow - 1
        column = startColumn - n
        cutoffCheck = 0
        while column >= 0 and row >= 0 and row >= startRow - n:
            # Check the bottom border
            if chess_board[row, column, 2]:
                count = count + 1

            row = row - 1

        # Check left-down border
        row = startRow + 1
        column = startColumn - n

        while column >= 0 and row < maxCoord and row <= startRow + n:
            # Check the top border
            if chess_board[row, column, 0]:
                count = count + 1

            row = row + 1

        return count
    # Gets all surrounding walls around the player up to n squares away

    def check_surroundings_walls(self, my_pos, chess_board, n):
        count = 0

        for i in range(0, n+1):
            count = count + \
                self.check_surrounding_outside_walls(
                    my_pos, chess_board, i)/(2 * i+1)
            if i > 0:
                count = count + \
                    self.check_surrounding_inside_walls(
                        my_pos, chess_board, i)/(2 * i+1)

        return count

# -----------------------------------------------------------------------------------------------------------------
    def set_barrier(self, chess_board, r, c, dir, exist):

        # Set the barrier to True
        chess_board[r, c, dir] = exist
        # Set the opposite barrier to True
        move = self.directions[dir]
        chess_board[r + move[0], c + move[1], self.opposites[dir]] = exist

# --------------------------------------------------------------------------------------------------------------------------------------

    # If the opponent is surrounded by 2 walls, return the square the move that places a wall s.t. the opponent must flee towards a border
    # Returns 0 if the opponent is not surrounded by exactly 2 walls

    def box_opponent(self, adv_pos, chess_board):
        if self.check_surroundings_walls(adv_pos, chess_board, 0) != 2:
            return 0

        r, c = adv_pos
        possible_directions = self.check_wall(r, c, chess_board)

        maxCoord = chess_board.shape[0]
        minDist = (100, 0)  # default: (distance, direction)

        for dir in possible_directions:
            r, c = adv_pos
            count = 0   # Counts number of squares from adv_pos to a border of the chess board
            # Get the opposite direction
            opp_dir = self.opposites[self.dir_map[dir]]

            # While the coordinates are within the bounds of the board...
            while r < maxCoord and r >= 0 and c < maxCoord and c >= 0:
                r = r + self.directions[opp_dir][0]
                c = c + self.directions[opp_dir][1]
                count = count + 1

            if count < minDist[0]:
                minDist = (count, self.dir_map[dir])

        # Now we have the wall that we want to place. We must get the move for our agent
        r, c = adv_pos
        dir = minDist[1]

        # Move one square towards dir
        r = r + self.directions[dir][0]
        c = c + self.directions[dir][1]

        # Reverse the direction
        dir = self.opposites[dir]

        # Return the move
        return ((r, c), dir)

    # I am between 2 walls, remove moves that will push myself towards a border
    def remove_box_myself(self, my_pos, chess_board):
        if self.check_surroundings_walls(my_pos, chess_board, 0) != 2:
            return 0

        r, c = my_pos
        possible_directions = self.check_wall(r, c, chess_board)

        maxCoord = chess_board.shape[0]
        minDist = (100, 0)  # default: (distance, direction)

        for dir in possible_directions:
            r, c = my_pos
            count = 0   # Counts number of squares from my_pos to a border of the chess board
            # Get the opposite direction
            opp_dir = self.opposites[self.dir_map[dir]]

            # While the coordinates are within the bounds of the board...
            while r < maxCoord and r >= 0 and c < maxCoord and c >= 0:
                r = r + self.directions[opp_dir][0]
                c = c + self.directions[opp_dir][1]
                count = count + 1

            if count > minDist[0]:
                minDist = (count, self.dir_map[dir])

        # Return the move
        return ((r, c), minDist[1])

    def remove_suicidal_moves(self, my_pos, adv_pos, chess_board, moves):
        good_moves = moves
        for move in moves:
            pos, dir = move
            r, c = pos
            self.set_barrier(chess_board, r, c, dir, True)

            is_endgame, my_score, adv_score = self.check_endgame(
                chess_board, pos, adv_pos)
            if is_endgame and my_score < adv_score:
                good_moves.remove(move)

            self.set_barrier(chess_board, r, c, dir, False)

        return good_moves


# -----------------------------------------------------------------------------------------------------------------
    # initialize a graph of depth n
    bestscore = -np.inf

    def alpha_beta(self, move, chess_board, max_step, depth, alpha, beta):
        if time.time() - start_time > move_time:
            return None, None

        if depth == 0:
            return self.heuristic(move)

        def find(move1):
            pos, dir = move1
            moves = self.get_moves(chess_board, pos, max_step, [])
            return self.total_moves(moves, chess_board)

        final_moves = find(move)

        for m in final_moves:
            chess_board, new_pos = self.makemove(chess_board, m)
            score = -self.alpha_beta(m, chess_board,
                                     max_step - 1, -alpha, -beta)
            if score > bestscore:
                bestscore = score
            chess_board = self.undomove(chess_board, move)
            if bestscore > alpha:
                alpha = bestscore
            if alpha >= beta:
                break

        return bestscore

    # returns a tuple (chess_board, new_pos)
    def makemove(self, chess_board, move):
        new_pos, dir = move
        r, c = new_pos
        self.set_barrier(self, chess_board, r, c, dir, True)
        return chess_board, new_pos

    # return chess_board with move undone
    def undomove(self, chess_board, move):
        pos, dir = move
        r, c = pos
        self.set_barrier(self, chess_board, r, c, dir, False)
        return chess_board

    def limit_opponent_moves(self, chess_board, adv_pos, moves, max_step):
        sum = 0
        d = dict()

        # given a position, return the size of possible moves
        def find(pos, chess_board1):
            moves = self.get_moves(chess_board1, pos, max_step, [])
            return len(self.total_moves(moves, chess_board1))

        for move in moves:
            chess_board, new_pos = self.makemove(chess_board, move)
            count = find(adv_pos, chess_board)
            d[move] = count
            sum += count
            self.undomove(chess_board, move)
        average = sum / len(moves)

        for move in d:
            if d[move] < average:
                d[move] = 1
            else:
                d[move] = 0
        return d

    # check_surroundings_walls(self, my_pos, chess_board, n)

    def heuristic_walls(self, adv_pos, chess_board, moves, max_step):
        n = chess_board.shape[0] // 2
        total_points = 4 * n
        d = dict()

        def find(move):
            pos, dir = move
            moves1 = self.get_moves(chess_board, pos, max_step, [])
            return self.total_moves(moves1, chess_board)

        for move in moves:
            chess_board, new_pos = self.makemove(chess_board, move)
            number_of_walls = self.check_surroundings_walls(adv_pos, chess_board, n)
            if number_of_walls <= n:
                d[move] = 0
            if number_of_walls > n:
                d[move] = 1
            if number_of_walls > 2 * n:
                d[move] = 2.5
            if number_of_walls > 3 * n:
                d[move] = 4

        return d