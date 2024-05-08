""" Module Description:

This file contains the Block class, the main data structure used in the game.
"""
from __future__ import annotations
import random
import math

from settings import colour_name, COLOUR_LIST

# constants
ROT_CW = 1
ROT_CCW = 3
SWAP_HORZ = 0
SWAP_VERT = 1


def _block_to_squares(board: Block) -> list[tuple[tuple[int, int, int],
                                                  tuple[int, int], int]]:

    """Return a list of tuples describing all the squares that must be drawn
    in order to render this Block.

    For every undivided Block, the list must contain one tuple that describes
    the square to draw for that Block. Each tuple contains:
    - the colour of the block,
    - the (x, y) coordinates of the top left corner of the block, and
    - the size of the block,
    in that order.

    The order of the tuples does not matter.
    """
    if board.children == []:
        return [(board.colour, board.position, board.size)]
    squares = []
    for child in board.children:
        squares.extend(_block_to_squares(child))
    return squares


def generate_board(max_depth: int, size: int) -> Block:
    """Return a new game board with a depth of <max_depth> and dimensions of
    <size> by <size>.

    >>> board = generate_board(3, 750)
    >>> board.max_depth
    3
    >>> board.size
    750
    >>> len(board.children) == 4
    True
    """
    board = Block((0, 0), size, random.choice(COLOUR_LIST), 0, max_depth)
    board.smash()

    return board


class Block:
    """A square Block in the Blocky game, represented as a tree.

    In addition to its tree-related attributes, a Block also contains attributes
    that describe how the Block appears on a Cartesian plane. All positions
    describe the upper left corner (x, y), and the origin is at (0, 0). All
    positions and sizes are in the unit of pixels.

    When a block has four children, the order of its children impacts each
    child's position. Indices 0, 1, 2, and 3 are the upper-right child,
    upper-left child, lower-left child, and lower-right child, respectively.

    Attributes
    - position: The (x, y) coordinates of the upper left corner of this Block.
    - size: The height and width of this square Block.
    - colour: If this block is not subdivided, <colour> stores its colour.
              Otherwise, <colour> is None.
    - level: The level of this block within the overall block structure.
             The outermost block, corresponding to the root of the tree,
             is at level zero. If a block is at level i, its children are at
             level i+1.
    - max_depth: The deepest level allowed in the overall block structure.
    - children: The blocks into which this block is subdivided. The children are
                stored in this order: upper-right child, upper-left child,
                lower-left child, lower-right child.

    Representation Invariants:
    - self.level <= self.max_depth
    - len(self.children) == 0 or len(self.children) == 4
    - If this Block has children:
        - their max_depth is the same as that of this Block.
        - their size is half that of this Block.
        - their level is one greater than that of this Block.
        - their position is determined by the position and size of this Block,
          and their index in this Block's list of children.
        - this Block's colour is None.
    - If this Block has no children:
        - its colour is not None.
    """
    position: tuple[int, int]
    size: int
    colour: tuple[int, int, int] | None
    level: int
    max_depth: int
    children: list[Block]

    def __init__(self, position: tuple[int, int], size: int,
                 colour: tuple[int, int, int] | None, level: int,
                 max_depth: int) -> None:
        """Initialize this block with <position>, dimensions <size> by <size>,
        the given <colour>, at <level>, and with no children.

        Preconditions:
        - position[0] >= 0 and position[1] >= 0
        - size > 0
        - level >= 0
        - max_depth >= level

        >>> block = Block((0, 0), 750, (0, 0, 0), 0, 1)
        >>> block.position
        (0, 0)
        >>> block.size
        750
        >>> block.colour
        (0, 0, 0)
        >>> block.level
        0
        >>> block.max_depth
        1
        """
        self.position = position
        self.size = size
        self.colour = colour
        self.level = level
        self.max_depth = max_depth
        self.children = []

    def __str__(self) -> str:
        """Return this Block in a string format.

        >>> block = Block((0, 0), 750, (1, 128, 181), 0, 1)
        >>> str(block)
        'Leaf: colour=Pacific Point, pos=(0, 0), size=750, level=0'
        """
        if len(self.children) == 0:
            indents = '\t' * self.level
            colour = colour_name(self.colour)
            return f'{indents}Leaf: colour={colour}, pos={self.position}, ' \
                   f'size={self.size}, level={self.level}'
        else:
            indents = '\t' * self.level
            result = f'{indents}Parent: pos={self.position},' \
                     f'size={self.size}, level={self.level}'

            for child in self.children:
                result += f'\n{child}'

            return result

    def __eq__(self, other: Block) -> bool:
        """Return True iff this Block and all its descendents are equivalent to
        the <other> Block and all its descendents.

        >>> b1 = Block((0, 0), 750, (0, 0, 0), 0, 1)
        >>> b2 = Block((0, 0), 750, (0, 0, 0), 0, 1)
        >>> b1 == b2
        True
        >>> b3 = Block((0, 0), 750, (255, 255, 255), 0, 1)
        >>> b1 == b3
        False
        """
        if len(self.children) == 0 and len(other.children) == 0:
            # Both self and other are leaves.
            return (self.position == other.position
                    and self.size == other.size
                    and self.colour == other.colour
                    and self.level == other.level
                    and self.max_depth == other.max_depth)
        elif len(self.children) != len(other.children):
            # One of self or other is a leaf while the other is not.
            return False
        else:
            # Both self and other have four children.
            # Because of RIs, don't need to check any attributes other
            # than the children, since will eventually hit base case!
            return self.children == other.children  # elementwise compare

    def child_size(self) -> int:
        """Return the size of this Block's children.
        """
        return round(self.size / 2.0)

    def children_positions(self) -> list[tuple[int, int]]:
        """Return the (x, y) coordinates of this Block's four children.

        The positions are returned in this order: upper-right child, upper-left
        child, lower-left child, lower-right child.
        """
        x = self.position[0]
        y = self.position[1]
        size = self.child_size()

        return [(x + size, y), (x, y), (x, y + size), (x + size, y + size)]

    def _update_children_positions(self, position: tuple[int, int]) -> None:
        """Set the position of this Block to <position> and update all its
        descendants to have positions consistent with this Block's position.

        <position> is the (x, y) coordinates of the upper-left corner of this
        Block.
        """
        self.position = position
        x, y = position
        size = self.child_size()
        positions = [(x + size, y), (x, y), (x, y + size), (x + size, y + size)]
        if self.children != []:
            for i in range(4):
                self.children[i]._update_children_positions(positions[i])

    def smashable(self) -> bool:
        """Return True iff this block can be smashed.

        A block can be smashed if it has no children and its level is not at
        max_depth.
        """
        return self.level != self.max_depth and len(self.children) == 0

    def smash(self) -> bool:
        """ Return True iff the smash was performed successfully.
        A smash is successful if the block genrates four children blocks and
        has no colour anymore.

        Smashing a block requires that the block has no children and that the
        block's level is less than the max_depth.

        For each new child, there is a chance the child will be smashed as well.
        The procedure for determining whether a child will be smashed is as
        follows:
        - Use function `random.random` to generate a random number in the
            interval [0, 1).
        - If the random number is less than `math.exp(-0.25 * level)`, where
            `level` is the level of this child `Block`, then the child `Block`
            will be smashed.
        - If the child `Block` is not smashed, uniform randomly assign the child
            a color from the list of colours in `settings.COLOUR_LIST`.

        If this Block's level is <max_depth>, do nothing. If this block has
        children, do nothing.

        >>> position = (0, 0)
        >>> size = 750
        >>> level = 0
        >>> max_depth = 1
        >>> b1 = Block(position, size, (0, 0, 0), level, max_depth)
        >>> b1.smash()
        True
        >>> b1.position == position
        True
        >>> b1.size == size
        True
        >>> b1.level == level
        True
        >>> b1.colour is None
        True
        >>> len(b1.children) == 4
        True
        >>> b1.max_depth == max_depth
        True
        """
        if not self.smashable():
            return False
        self.colour = None
        positions = self.children_positions()
        for i in range(4):
            num = random.random()
            child = Block(positions[i], self.child_size(), None,
                          self.level + 1, self.max_depth)
            self.children.append(child)
            if num < math.exp(-0.25 * self.level):
                if not child.smash():
                    child.colour = COLOUR_LIST[random.randint(0, 3)]
            else:
                child.colour = COLOUR_LIST[random.randint(0, 3)]
        return True

    def swap(self, direction: int) -> bool:
        """Swap the child Blocks of this Block.

        If this Block has no children, do nothing. Otherwise, if <direction> is
        SWAP_VERT, swap vertically.
        If <direction> is SWAP_HORZ, swap horizontally.

        Return True iff the swap was performed.

        Precondition:
        - <direction> is either (SWAP_VERT, SWAP_HORZ)
        """
        if self.children == []:
            return False
        if direction == SWAP_VERT:
            save = self.children[0]
            self.children[0] = self.children[3]
            self.children[3] = save
            save = self.children[1]
            self.children[1] = self.children[2]
            self.children[2] = save
            self._update_children_positions(self.position)
            return True
        else:
            save = self.children[0]
            self.children[0] = self.children[1]
            self.children[1] = save
            save = self.children[2]
            self.children[2] = self.children[3]
            self.children[3] = save
            self._update_children_positions(self.position)
            return True

    def rotate(self, direction: int) -> bool:
        """Rotate this Block and all its descendents.

        If this Block has no children, do nothing (no rotation is performed).
        If <direction> is ROT_CW, rotate clockwise.
        If <direction> is ROT_CCW, rotate counter-clockwise.

        Return True iff the rotation was performed.

        Preconditions:
        - direction in (ROT_CW, ROT_CCW)
        """
        if self.children == []:
            return False
        for child in self.children:
            child.rotate(direction)
        if direction == ROT_CW:
            save_3 = self.children[3]
            self.children[3] = self.children[0]
            save_2 = self.children[2]
            self.children[2] = save_3
            save_1 = self.children[1]
            self.children[1] = save_2
            self.children[0] = save_1
            self._update_children_positions(self.position)
            return True
        else:
            save_0 = self.children[0]
            self.children[0] = self.children[3]
            save_1 = self.children[1]
            self.children[1] = save_0
            save_2 = self.children[2]
            self.children[2] = save_1
            self.children[3] = save_2
            self._update_children_positions(self.position)
            return True

    def paint(self, colour: tuple[int, int, int]) -> bool:
        """Change this Block's colour iff it is a leaf at a level of max_depth
        and its colour is different from <colour>.

        Return True iff this Block's colour was changed.
        """
        if (self.children == [] and self.level == self.max_depth
                and self.colour != colour):
            self.colour = colour
            return True
        return False

    def combine(self) -> bool:
        """Turn this Block into a leaf based on the majority colour of its
        children.  Each child block must also be a leaf.

        The majority colour is the colour with the most child blocks of that
        colour. A tie does not constitute a majority (e.g., if there are two red
        children and two blue children, then there is no majority colour).

        The method should do nothing for the following cases:
        - If there is no majority colour among the children.
        - If the block has no children.

        Return True iff this Block was turned into a leaf node.
        """
        if self.children == []:
            return False
        colour_streak = {}
        for child in self.children:
            if child.children != []:
                return False
            if child.colour in colour_streak:
                colour_streak[child.colour] += 1
            else:
                colour_streak[child.colour] = 1
                pick = child.colour
        for colour in colour_streak:
            if colour_streak[colour] > colour_streak[pick]:
                pick = colour
        for colour in colour_streak:
            if colour != pick and colour_streak[colour] == colour_streak[pick]:
                return False
        self.children = []
        self.colour = pick
        return True

    def create_copy(self) -> Block:
        """Return a new Block that is a deep copy of this Block.

        Remember that a deep copy has new blocks (not aliases) at every level.

        >>> block = generate_board(3, 750)
        >>> copy = block.create_copy()
        >>> id(block) != id(copy)
        True
        >>> block == copy
        True
        """
        if self.children == []:
            return Block(self.position, self.size, self.colour, self.level,
                         self.max_depth)
        copy = Block(self.position, self.size, self.colour, self.level,
                     self.max_depth)
        for child in self.children:
            copy.children.append(child.create_copy())
        return copy


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', '__future__', 'math',
            'settings'
        ],
        'max-attributes': 15,
        'max-args': 6
    })

    import doctest

    doctest.testmod()

    # This is a board consisting of only one block.
    b1 = Block((0, 0), 750, COLOUR_LIST[0], 0, 1)
    print("tiny board:")
    print(b1)

    # Now let's make a random board.
    b2 = generate_board(3, 750)
    print("\nrandom board:")
    print(b2)
