""" Module Description:

This file contains the hierarchy of Goal classes and related helper functions.
"""
from __future__ import annotations
import random
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> list[Goal]:
    """Return a randomly generated list of goals with length <num_goals>.

    Each goal must be randomly selected from the two types of Goals provided
    and must have a different randomly generated colour from COLOUR_LIST.
    No two goals can have the same colour.

    Preconditions:
    - num_goals <= len(COLOUR_LIST)
    """
    goal_class = [PerimeterGoal, BlobGoal]
    # creating a deep copy of COLOURLIST
    colours = [colour for colour in COLOUR_LIST]
    goals = []
    for _ in range(num_goals):
        colour = colours[random.randint(0, len(colours) - 1)]
        goals.append(goal_class[random.randint(0, 1)](colour))
        colours.remove(colour)
    return goals


def flatten(block: Block) -> list[list[tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j].

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.children == [] and block.max_depth == block.level:
        return [[block.colour]]
    elif block.children == []:
        columns = []
        for i in range(2 ** (block.max_depth - block.level)):
            column = []
            for _ in range(2 ** (block.max_depth - block.level)):
                column.append(block.colour)
            columns.append(column)
        return columns
    else:
        flat_children = []
        for child in block.children:
            flat_children.append(flatten(child))
        columns = []
        for i in range(len(flat_children[1])):
            columns.append(flat_children[1][i] + flat_children[2][i])
        for i in range(len(flat_children[0])):
            columns.append(flat_children[0][i] + flat_children[3][i])
        i = 0
        return columns


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    Instance Attributes:
    - colour: The target colour for this goal, that is the colour to which
              this goal applies.
    """
    colour: tuple[int, int, int]

    def __init__(self, target_colour: tuple[int, int, int]) -> None:
        """Initialize this goal to have the given <target_colour>.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given <board>.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal to maximize the presence of this goal's target colour
    on the board's perimeter.
    """

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a PerimeterGoal is defined to be the number of unit cells
        on the perimeter whose colour is this goal's target colour. Corner cells
        count twice toward the score.
        """
        flat_board = flatten(board)
        perimeter = (flat_board[0] + [col[0] for col in flat_board]
                     + flat_board[-1] + [col[-1] for col in flat_board])
        score = 0
        for cell in perimeter:
            if cell == self.colour:
                score += 1
        return score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return (f'Place the greatest possible number of units of colour '
                f'{colour_name(self.colour)} on the perimeter of the board')


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a BlobGoal is defined to be the total number of
        unit cells in the largest connected blob within this Block.
        """
        flat_board = flatten(board)
        visited = [[-1 for _ in col] for col in flat_board]
        blob_max = 0
        for i in range(len(flat_board)):
            for j in range(len(flat_board[0])):
                blob = self._undiscovered_blob_size((i, j), flat_board, visited)
                if blob > blob_max:
                    blob_max = blob
        return blob_max

    def _undiscovered_blob_size(self, pos: tuple[int, int],
                                board: list[list[tuple[int, int, int]]],
                                visited: list[list[int]]) -> int:
        """Return the size of the largest connected blob in <board> that (a) is
        of this Goal's target <colour>, (b) includes the cell at <pos>, and (c)
        involves only cells that are not in <visited>.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure (to <board>) that, in each cell,
        contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.

        If <pos> is out of bounds for <board>, return 0.
        """
        i, j = pos
        if (i < 0 or i >= len(board[0]) or j < 0
                or j >= len(board)):
            return 0
        if visited[i][j] != -1:
            return 0
        if board[i][j] == self.colour:
            visited[i][j] = 1
            blob = 1
            blob += self._undiscovered_blob_size((i - 1, j), board, visited)
            blob += self._undiscovered_blob_size((i, j - 1), board, visited)
            blob += self._undiscovered_blob_size((i + 1, j), board, visited)
            blob += self._undiscovered_blob_size((i, j + 1), board, visited)
        else:
            blob = 0
            visited[i][j] = 0
        return blob

    def description(self) -> str:
        """Return a description of this goal.
        """
        return f'Create the largest blob of colour {colour_name(self.colour)}'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
