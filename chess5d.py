import chess as chess2d
import chess.svg as chess2dsvg
from PIL import Image

from GameObject import *
from functions import *

from chess import Board as Board2d
import re
import numpy as np
from typing import Union
from copy import copy, deepcopy

NOTATIONS = {
    'rook': 'R',
    'knight': 'N',
    'bishop': 'B',
    'king': 'K',
    'queen': 'Q',
    'pawn': 'P',
}


class SuperspacialBoard:
    pass
class Piece:
    pass

class SpacialBoard:
    pass

class Square:
    pass
class Position(str):
    def __new__(cls, text: str):
        return str.__new__(cls, text)

class SpacialPosition(Position): #Spacial Position
    def __new__(cls, x: Union[int, str], y:int = None):
        if y is None:
            if isinstance(x,int):
                i = x
                x = int(i/8)
                y = i % 8
                return cls.__new__(cls,y,x)
            if isinstance(x,str):
                x, y = parse_spacial_position(x)
                return cls.__new__(cls,x,y)

        if 0<=x<8 and 0<=y<8:
            self = Position.__new__(cls, f'{"abcdefgh"[x]}{y+1}')
            self.x = x
            self.y = y
            return self
        
        raise ValueError(f'argument x, y with values ({x}, {y}) must be in range(8)')
    
    def check(self):
        position = SpacialPosition(self.x, self.y)
        if position != self:
            raise ValueError



class SuperPosition(Position): #Spacial Position
    def __new__(
            cls,
            world_index: Union[int,str] = 0,
            turn_time: float = None):
        
        if turn_time is None:
            if isinstance(world_index, str):
                literal = world_index
                index, time = parse_super_position(literal)
                return cls.__new__(cls, index, time)
            raise TypeError
            
        i, t = world_index, turn_time
        side = roll('W', floor(t)==t, 'B')
        self = Position.__new__(cls, f'{i}{side}{floor(t)}')
        self.index = i
        self.time = t
        self.side = side
        return self


    def _check(self):
        position = SuperPosition(self.index, self.time)
        if position != self:
            raise ValueError
    
    def next(self):
        return SuperPosition(self.index, self.time + 0.5)

if_else = lambda a,b,c: roll(b,a,c)

class SuperspacialPosition(str): #Superspacial Position
    def __new__(
            cls,
            world_index: Union[int, str],
            turn_time: Union[int, str] = None,
            x: Union[int, str] = None,
            y: int = None):
        
        ii, tt, xx, yy = world_index, turn_time, x, y
        if isinstance(world_index, str):
            ii, tt = parse_super_position(world_index)
            if not isinstance(turn_time, str):
                xx, yy = parse_spacial_position(world_index[len(world_index)-2:])
        
        if isinstance(turn_time, str):
            xx, yy = parse_spacial_position(turn_time)
        
        if isinstance(x, str):
            xx, yy = parse_spacial_position(x)
        self = Position.__new__(cls, f'{SuperPosition(ii,tt)}{SpacialPosition(xx,yy)}')
        self.index, self.time, self.x, self.y = ii, tt, xx, yy
        return self

    def _check(self):
        position = SuperspacialPosition(self.index, self.time, self.x, self.y)
        if position != self:
            raise ValueError
    def next(self):
        return SuperspacialPosition(self.index, self.time+0.5, self.x, self.y)
        
    def side(self):
        self._check()
        return roll("W",self.t == floor(self.t),"B")
    
    def spacial(self):
        return SpacialPosition(self.x, self.y)
    
    def super(self):
        return SuperPosition(self.index, self.time)
    
class Piece(GameObject):
    
    all = []

    def __init__(
            self, name: str,
            notation: str,
            square: Square,
            ascii: str = None,
            color: str = "white",):
        GameObject.__init__(self)
        self.name: str = name
        self.notation: str = notation
        self.square = square
        self.parent = square
        self.ascii = notation
        if ascii:
            self.ascii = ascii
        self.color = color
        #movement of the piece
        self.directions = []
        self.limit = None

        self.worldline: list = [square]
        
    def forward(self):
        next = self.square.superspacial_position.next()
        superspacial_board = self.get('superspacial_board')
        square = superspacial_board[next]
        self.square = square
        square.piece = self



    def move(i,t,x,y):
        pass


    def exceptions(self) -> list:
        return []
    
    def additionals(self) -> list:
        return []

BASE = np.array([
        (0,0,0,1),
        (0,0,1,0),
        (0,1,0,0),
        (1,0,0,0),])

class King(Piece):
    def __init__(self,square: Square = None):
        Piece.__init__(self, 'King', 'K', square)
        for i in range(4):
            dir = BASE[i]
            dir = list(map(int,dir))
            self.rule.directions.append(dir)

        for i in range(4):
          for j in range(i+1,4):
            dir = BASE[i] + BASE[j]
            dir = (dir/dir.max()).tolist()
            dir = list(map(int,dir))
            self.rule.directions.append(dir)
        self.rule.limit = 1

        


class Square(GameObject):
    def __init__(
            self,
            spacial_board: SpacialBoard = None,
            spacial_position: SpacialPosition = None):
        GameObject.__init__(self)
        self.spacial_board = spacial_board
        self.parent = spacial_board
        self.spacial_position = spacial_position
        self.piece = None
        self.superspacial_position = SuperspacialPosition(self.get('super_position'),self.spacial_position)
    


    #def superspacialPosition(self):
    #    return SuperspacialPosition(self.get('super_position'),self.spacial_position)
    



class SpacialBoard(GameObject):
    def __init__(
            self,
            superspacial_board: SuperspacialBoard = None,
            super_position: SuperPosition = None,
            size:int = 8): 
        GameObject.__init__(self)
        self.superspacial_board = superspacial_board
        self.parent = superspacial_board
        self.super_position = super_position

        self.squares = {}

        self.next = None
        self.last = None

        for x in range(size):
            for y in range(size):
                spacial = SpacialPosition(x,y)
                self.squares[spacial] = Square(self, spacial)

    def __getitem__(self, keys):
        items = []
        if not isinstance(keys, list):
            keys = [keys]
        for arg in keys:
            if isinstance(arg,str) or isinstance(arg,str):
                spacial = SpacialPosition(arg)
                items.append(self.squares[spacial])
            elif isinstance(arg, tuple) or isinstance(arg, list):
                x, y = arg
                spacial = SpacialPosition(x,y)
                items.append(self.squares[spacial])
            else:
                items.append(None)
        if len(items) == 1:
            return items[0]
        return items
    
    def __str__(self) -> str:
        return self.board2d().__str__()
    
    def present(self):
        return 0

    def fen(self):
        result = ''
        for rank in range(8):
            for file in range(8):
                spacial = SpacialPosition(file,7-rank)
                if spacial in self.squares.keys():
                    if self[spacial].piece:
                        notation = self[spacial].piece.notation
                        if self[spacial].piece.color == 'black':
                            notation = notation.lower()
                        result += notation
                    else:
                        result += '_'
            result += '/'
        result = result[:len(result)-1]
        subf = lambda m: str(len(m.group()))
        result = re.sub('_+', subf, result)
        side = self.super_position.side.lower()
        return result +  f' {side} KQkq - 0 1'

    def append(self):
        if self.next:
            return self.next
        next = self.super_position.next()
        self.next = SpacialBoard(self.superspacial_board,next)
        self.superspacial_board.spacial_boards[next] = self.next
        self.next.last = self
        for square in self.squares.values():
            if square.piece:
                square.piece.forward()


    def board2d(self):
        return chess2d.Board(self.fen())
        
    def svg(self, *args):
        return chess2dsvg.board(self.board2d(), *args)
    

    
    def default_fill(self):
        board2d = chess2d.Board()
        for i, pieces2d in board2d.piece_map().items():
            spacial = SpacialPosition(i)
            name = chess2d.PIECE_NAMES[pieces2d.piece_type]
            self.squares[spacial].piece = Piece(
                name = name,
                notation = NOTATIONS[name],
                square = self.squares[spacial],
                color = chess2d.COLOR_NAMES[pieces2d.color])

            
    
class SuperspacialBoard(GameObject):
    def __init__(
            self,):
        GameObject.__init__(self)
        self.spacial_boards = {}


    def __getitem__(self, keys):
        items = []
        if not isinstance(keys, list):
            keys = [keys]
        for arg in keys:
            if isinstance(arg,str) or isinstance(arg,str):
                if re.match(SUPER_POSITION + SPACIAL_POSITION, arg):
                    ssp = SuperspacialPosition(arg)
                    items.append(self[ssp.super()][ssp.spacial()])
                else:
                    super = SuperPosition(arg)
                    items.append(self.spacial_boards[super])
            elif isinstance(arg, tuple) or isinstance(arg, list):
                index, time = arg
                super = SuperPosition(index,time)
                items.append(self.spacial_boards[super])
            else:
                items.append(None)
        if len(items) == 1:
            return items[0]
        return items
    
    def parse_move(self, move):
        origin, target, iswarp = parse_move(self, move)
        return SuperspacialPosition(origin), SuperspacialPosition(target), iswarp
    
    def force_push(self, origin, target, iswarp): 
        if not iswarp:
            self[origin.super()].append()
            onext = origin.next()
            tnext = target.next()
            if self[tnext].piece:
                self[tnext].piece.square = None
            self[onext].piece.square = self[tnext]
            self[tnext].piece = self[onext].piece
            self[onext].piece = None
        return
    
    def push_move(self,move):
        origin, target, iswarp = self.parse_move(move)
        self.force_push(origin, target, iswarp)


    def default_fill(self):
        board = SpacialBoard(self,SuperPosition(0,0))
        board.default_fill()
        self.spacial_boards[SuperPosition(0,0)] = board

if __name__ == '__main__':
    board = SuperspacialBoard()
    board.default_fill()
    svgstr = board['0W0'].svg()
    with open('chess.svg','w') as f:
        f.write(svgstr)

