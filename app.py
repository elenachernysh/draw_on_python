import copy
import os
from dataclasses import dataclass, fields

from utils import constants
from utils.utils import Attr, validate_int


@dataclass
class Point:
    x: int = Attr(int, validate_int, True)
    y: int = Attr(int, validate_int, True)

    def __add__(self, other):
        return Point(*(getattr(self, dim.name) + getattr(other, dim.name) for dim in fields(self)))


class Shape:
    EXPECTED_ATTRS_QUANTITY = NotImplementedError('Expected quantity of attrs is not set')

    @classmethod
    def constructor(cls, *args):
        return cls(*args)

    @classmethod
    def validate_and_create(cls, *args):
        if len(args) == cls.EXPECTED_ATTRS_QUANTITY:
            try:
                return cls.constructor(*args)
            except Exception as e:
                raise Exception(f'{constants.ERROR_MESSAGE_FAILED_PARAM} {cls.__name__}: {repr(e)}')
        else:
            raise Exception(
                f'Invalid {cls.__name__} input data - expected {cls.EXPECTED_ATTRS_QUANTITY} '
                f'params, but {len(args)} were given'
            )

    def draw(self, *args):
        raise NotImplementedError('Method draw() is not set')

    def draw_line(self, matrix, start, end, symbol_horizontal='x', symbol_vertical='x'):
        try:
            if start.x == end.x:
                for position in range(start.y, end.y + 1):
                    matrix[position][start.x] = (symbol_vertical,)

            elif start.y == end.y:
                arr = matrix[start.y]
                for position in range(min(start.x, end.x + 1), max(start.x, end.x + 1)):
                    arr[position] = (symbol_horizontal,)
                matrix[start.y] = arr

            return matrix
        except IndexError:
            raise IndexError(f'{self.__class__.__name__} {constants.ERROR_MESSAGE_POINT_OUT_OF_CANVAS}')


class Line(Shape):
    EXPECTED_ATTRS_QUANTITY = 4

    def __init__(self, x1, y1, x2, y2):
        self.start = Point(x1, y1)
        self.end = Point(x2, y2)

    def draw(self, matrix):
        return self.draw_line(matrix, self.start, self.end)


class Rectangle(Shape):
    EXPECTED_ATTRS_QUANTITY = 4

    def __init__(self, x1, y1, x2, y2):
        self.corners = (Line(x1, y1, x2, y1),
                        Line(x2, y1, x2, y2),
                        Line(x1, y2, x2, y2),
                        Line(x1, y1, x1, y2))

    def draw(self, matrix):
        for corner in self.corners:
            matrix = self.draw_line(matrix, corner.start, corner.end)
        return matrix


class Fill(Shape):
    EXPECTED_ATTRS_QUANTITY = 3
    vectors = (
        Point(0, -1),  # up
        Point(1, -1),  # up-right
        Point(1, 0),  # forward
        Point(1, 1),  # down-right
        Point(0, 1),  # down
        Point(1, -1),  # down-left
        Point(-1, 0),  # back
        Point(-1, -1),  # up-left
    )

    def __init__(self, x, y, symbol_line='o'):
        self.start_point = Point(x, y)
        self.symbol_line = symbol_line

    def draw(self, matrix):
        return self._sunshine(self.start_point, matrix)

    def _sunshine(self, point, matrix):
        try:
            current_point = matrix[point.y][point.x]
            if not isinstance(current_point, tuple) and current_point != self.symbol_line:
                matrix[point.y][point.x] = self.symbol_line
                for vector in self.vectors:
                    next_cell = point + vector
                    matrix = self._sunshine(next_cell, matrix)

            return matrix
        except IndexError:
            raise IndexError(f'{self.__class__.__name__} {constants.ERROR_MESSAGE_POINT_OUT_OF_CANVAS}')


class Canvas(Rectangle):
    EXPECTED_ATTRS_QUANTITY = 2

    def __init__(self, width, height, horizontal_border_symbol='-', vertical_border_symbol='|'):
        self.width = width
        self.height = height
        self.horizontal_border_symbol = horizontal_border_symbol
        self.vertical_border_symbol = vertical_border_symbol
        super().__init__(0, 0, self.width + 1, self.height + 1)

    @classmethod
    def constructor(cls, *args):
        try:
            width = int(args[0])
            height = int(args[1])
            return cls(width, height)
        except ValueError as e:
            raise e

    def draw(self, matrix):
        matrix = [[' ' for _ in range(0, self.width + 2)]
                  for _ in range(0, self.height + 2)]

        for corner in self.corners:
            if corner.start.y == corner.end.y:
                matrix = self.draw_line(matrix, corner.start, corner.end, self.horizontal_border_symbol,
                                        self.vertical_border_symbol)
            else:
                corner.start.y += 1
                corner.end.y -= 1
                matrix = self.draw_line(matrix, corner.start, corner.end, self.horizontal_border_symbol,
                                        self.vertical_border_symbol)
        return matrix


class Creator:
    MAP_SHAPES = {
        'C': Canvas,
        'L': Line,
        'R': Rectangle,
        'B': Fill
    }

    def __init__(self, input_file_name, output_file_name, file_path=''):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.file_path = file_path
        self.matrix = []

    def execute(self):
        with open(self.input_file_name, 'r') as input_file, open(self.output_file_name, 'w') as output_file:
            while line := input_file.readline():
                self.process_line(line.rstrip())
                copy_matrix = copy.deepcopy(self.matrix)
                ready = self.prepare_write_to_file(copy_matrix)
                output_file.write(ready)

    def process_line(self, line):
        try:
            data = line.split(' ')

            key_shape = data.pop(0)
            obj_cls = self.MAP_SHAPES.get(key_shape)

            if not obj_cls:
                raise ValueError(f'{constants.ERROR_MESSAGE_NO_FIGURE} {str(key_shape)}')

            obj = obj_cls.validate_and_create(*data)

            if obj_cls != Canvas and len(self.matrix) == 0:
                raise Exception(constants.ERROR_MESSAGE_NO_CANVAS)

            self.matrix = obj.draw(self.matrix)
            return
        except Exception as exc:
            raise exc

    def prepare_write_to_file(self, matrix):
        for index, item in enumerate(matrix):
            if isinstance(item, list):
                self.prepare_write_to_file(item)
            matrix[index] = ''.join(item)
        return '\n'.join(matrix) + '\n'


if __name__ == "__main__":
    file_dir = os.path.dirname(__file__)
    input_file_path = os.path.join(file_dir, 'files/input.txt')
    output_file_path = os.path.join(file_dir, 'files/output.txt')

    creator = Creator(input_file_path, output_file_path)
    creator.execute()
