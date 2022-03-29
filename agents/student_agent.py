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
        all_moves = get_moves(chess, _board, my_pos, max_step, "r")

        final_moves = total_moves(all_moves)

        # Box myself
        r, c = my_pos
        if not chess_board[r, c, 3]:
            return my_pos, self.dir_map["l"]
        elif not chess_board[r, c, 0]:
            return my_pos, self.dir_map["u"]
        elif not chess_board[r, c, 1]:
            return my_pos, self.dir_map["r"]
        elif not chess_board[r, c, 2]:
            return my_pos, self.dir_map["d"]

    moves = []

    def get_moves(self, chess_board, my_pos, max_step, my_dir, moves):
      
        
        r, c = my_pos
    
        moves.append(my_pos)

        # Check the right
        if (max_step != 0 and not chess_board[r, c, self.dir_map["r"]] and (r, c + 1) not in moves):
            get_moves(chess_board, (r, c + 1), max_step-1, "r", moves)

        # Check the down
        if (max_step != 0 and not chess_board[r, c, self.dir_map["d"]] and (r + 1, c) not in moves):
            get_moves(chess_board, (r + 1, c), max_step-1, "d", moves)

        # Check the left
        if (max_step != 0 and not chess_board[r, c, self.dir_map["l"]] and (r, c - 1) not in moves):
            get_moves(chess_board, (r, c - 1), max_step-1, "l", moves)

        # Check the up
        if (max_step != 0 and not chess_board[r, c, self.dir_map["u"]] and (r - 1, c) not in moves):
            get_moves(chess_board, (r - 1, c), max_step-1, "u", moves)

        return moves

    # Returns the walls that are possible for a single square

    def check_wall(self, r, c):
        possible_directions = []

        for my_dir in self.dir_map:
            if chess_board[r, c, self.dir_map[my_dir]]:
                possible_directions.append(my_dir)

        return possible_directions

    def total_moves(self, moves):
        final_moves = []

        for pos in moves:
            r,c = pos
            possible_directions = check_wall(r,c)
            for direction in possible_directions:
                new_tuple = (r, c, direction)
                final_moves.append(new_tuple)
           
        return final_moves