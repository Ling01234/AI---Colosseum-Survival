# Student agent: Add your own agent here
from copy import copy
from agents.agent import Agent
from store import register_agent
import sys


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
        self.moves = []

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
        all_moves = self.get_moves(chess_board, my_pos, max_step, "r")

        final_moves = self.total_moves(all_moves, chess_board)
        print(final_moves)
        # # Box myself
        # r, c = my_pos
        # if not chess_board[r, c, 3]:
        #     return my_pos, self.dir_map["l"]
        # elif not chess_board[r, c, 0]:
        #     return my_pos, self.dir_map["u"]
        # elif not chess_board[r, c, 1]:
        #     return my_pos, self.dir_map["r"]
        # elif not chess_board[r, c, 2]:
        #     return my_pos, self.dir_map["d"]

        mate = self.check_instant_win(
            my_pos, adv_pos, chess_board, final_moves)
        print(mate)
        if len(mate) != 0:
            return mate[0]

        # else:
        #     print("else")
        #     return final_moves[0]
        # return final_moves[0]

    def get_moves(self, chess_board, my_pos, max_step, my_dir):

        r, c = my_pos

        self.moves.append(my_pos)

        # Check the right
        if (max_step != 0 and not chess_board[r, c, self.dir_map["r"]] and (r, c + 1) not in self.moves):
            self.get_moves(chess_board, (r, c + 1), max_step-1, "r")

        # Check the down
        if (max_step != 0 and not chess_board[r, c, self.dir_map["d"]] and (r + 1, c) not in self.moves):
            self.get_moves(chess_board, (r + 1, c), max_step-1, "d")

        # Check the left
        if (max_step != 0 and not chess_board[r, c, self.dir_map["l"]] and (r, c - 1) not in self.moves):
            self.get_moves(chess_board, (r, c - 1), max_step-1, "l")

        # Check the up
        if (max_step != 0 and not chess_board[r, c, self.dir_map["u"]] and (r - 1, c) not in self.moves):
            self.get_moves(chess_board, (r - 1, c), max_step-1, "u")

        return self.moves

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
        original_board = copy(chess_board)
        for move in moves:
            pos, dir = move
            r, c = pos
            original_board[r, c, dir] = True
            is_endgame, my_score, adv_score = self.check_endgame(
                original_board, pos, adv_pos)
            if is_endgame and my_score > adv_score:
                print("IS_ENDGAME = TRUE")
                mate.append(move)
                # print("MATE:")
                # print(mate)
                return mate
            original_board = chess_board

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
                    if chess_board[r, c, dir + 1]:
                        continue

                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)

        for r in range(chess_board.shape[0]):
            for c in range(chess_board.shape[0]):
                find((r, c))

        p0_r = find(tuple(my_pos))
        p1_r = find(tuple(adv_pos))
        my_score = list(father.values()).count(p0_r)
        adv_score = list(father.values()).count(p1_r)

        if p0_r == p1_r:
            return False, my_score, adv_score
        player_win = None
        win_blocks = -1
        if my_score > adv_score:
            print("CHECK ENDGAME7!!!!!!!!!!!!")
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
                    my_pos, chess_board, i)/(i+1)
            if i > 0:
                count = count + \
                    self.check_surrounding_inside_walls(
                        my_pos, chess_board, i)/(i+1)

        return count

# -----------------------------------------------------------------------------------------------------------------
