from typing import Union
import numpy as np
import re
from chess import Board as Board2d

def if_(booleans: Union[bool,list], item_list = [True,False]):
    if not isinstance(booleans, list):
        booleans = [booleans]
    for i, boolean in enumerate(booleans):
        if boolean:
            return (item_list)[i]
    return item_list[-1]

def roll(*args):
    if not args:
        return None
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        return roll(*args, None)
    if args[1]:
        return args[0]
    return roll(*args[2:])

def floor(x):
    return int(np.floor(x))

SUPER_POSITION = '(?P<index>0|-?[1-9][0-9]*)(?P<time>[WB](0|-?[1-9][0-9]*))'
def parse_super_position(super_Position: str):
    rematch = re.match(SUPER_POSITION,super_Position)
    if rematch is None:
        raise ValueError(f'super_Position "{super_Position}" has syntax error')
    
    d = rematch.groupdict()
    index = int(d["index"])
    side = d['time'][0]
    t = d['time'][1:]
    time = roll(float(t), side=='W', float(t) + 0.5)
    return index, time
  
SPACIAL_POSITION = '(?P<roll>[a-h])(?P<rank>[1-8])'
def parse_spacial_position(spacial_position: str):
    rematch = re.match(SPACIAL_POSITION,spacial_position)
    if rematch is None:
        raise ValueError(f'spacial_Position "{spacial_position}" has syntax error')
    
    d = rematch.groupdict()
    return 'abcdefgh'.index(d["roll"]), int(d['rank']) - 1

def parse_move(superspacialboard, move: str, pieces: str = 'RNBKQP'):
    '''      

        =           finally lands on spacial board
                    as for white, the board they attemp to move to is always white. the board they finally land on is always black
        >           appends spacial board, to which the opponent doesn't have to answer
        >...!       appends spacial board and shifting present for opponent to answer
        >...!?...
                    checking a king's present
        >...!??...
                    checking a king's past
        >...!??...#
                    checkmate



        (<), (x<)
                    attempts backward-timewarp, a.k.a. time travling. x marks capturing
                    there is no (>) because there is no forward-timewarp without involving spacewarp
                    because you cant warp to your own future
        [<], [>], [x<], [>x]
                    attempts spacewarp, a.k.a. multiverse travling
        {<}, {>}, {x<}, {>x}
                    attempts time-spacewarp

                
        Spcial spacial move: 0W0Ka1a2=>0B0
        Translate: White King at 0W0a1 attampts moving to a2, appending(>) and shifting present(!) to board 0B0 for black to answer, finally landing(=) on 0B0

        Capturing: 0W0Ka1xNa2 => 0B0
        Translate: White King at 0W0a1 attampts capturing Na2, appending(>) and shifting present(!) to board 0B0 for black to answer, finally capturing(=) on 0B0

        Move without shifting present: 0W0Ka1xNa2 > 0B0?
        Translate: White King at 0W0a1 attampts moving to a2, appending(>) to board 0B0 for black to answer, finally landing(=) on 0B0, without shifting the present. 
        This means white hea not answered the present, so they have to attamp another additional move to shift the present. 

        Basic timewarp: 1B-1<=0W-1a1(<)0W0Ka1>0B0
        Translate: White King at 0W0a1 attampts backward-timewarp({{) to 0W-1a1, appending(> and <) board 0B0 and 1B-1, shifting present(!) to 1B-1, finally landing(=) on 1B-1

        Timewarp with capture: 1B-1<=0W-1Na1(x<)0W0Ka1>0B0
        Translate: White King at 0W0a1 attampts backward-timewarps to capture 0W-1a1, appendingboard 0B0 and 1B-1, shifting present to 1B-1, finally landing on 1B-1

        Basic spacewarp: 0B0<0W0Ka1[>]1W0a1=>1B0
        Translate: 

        Backward time-spacewarp:  <1W-1a1{<}0W0Ka1
        Translate:



        # 1B-1a1 <= 0W-1 {{ 0W0Ka1
        # 0W0Ka1 ]] -1W0 => 1B-1a1 >=  [[ 
        # 1B-1a1 <x 0W-1 << K @ 0W0a1 > 0B0   # Knight(K) at(@) 0W0a1 warps(<<) to 0W-1, landing(=) on and pushing(<) 1B-1a1 for black to answer, pushing 0B0 for black to answer'''
    warparrow = '[\(\[\{](x<|<|>|>x)[\}\)\]]'
    move = re.sub(' ','',move)
    iswarp = re.match(warparrow,move)
    pieces: str = 'RNBKQP'
    def f(i):
        def f(m):
            s = m.group()
            return s[:len(s)-1] + f'{i}' + '>'
        return f
    p1, p2 = re.sub("<.+?>",f(0),SUPER_POSITION), re.sub("<.+?>",f(0),SPACIAL_POSITION)
    p3, p4 = re.sub("<.+?>",f(1),SUPER_POSITION), re.sub("<.+?>",f(1),SPACIAL_POSITION)
    originrex1 = f'{p1}(?P<p0>[{pieces}]){p2}'
    originrex2 = f'{p3}(?P<p1>[{pieces}]){p4}'
    originrex = '([\(\[\{](x<|<)[\}\)\]]'+f'{originrex1})|({originrex2}'+'[\(\[\{](>|>x)[\}\)\]])'
    originmatch = re.search(originrex,move)
    
    targetrex1 = f'{p1}(?P<p0>[{pieces}])?{p2}'
    targetrex2 = f'{p3}(?P<p1>[{pieces}])?{p4}'
    targetrex = f'({targetrex2}'+'([\(\[\{](x<|<)[\}\)\]]' + ')|(' + '[\(\[\{](>|>x)[\}\)\]])' + f'{targetrex1})'
    targetmatch = re.search(targetrex,move)

    if originmatch :#and targetmatch:
        o = originmatch.groupdict()
        t = targetmatch.groupdict()
        rt = ['','']
        for i,d in enumerate((o,t)):
            if d['index0']:
                index = d['index0']
                time = d['time0']
                roll = d['roll0']
                rank = d['rank0']
                p = d['p0']
            else:
                index = d['index1']
                time = d['time1']
                roll = d['roll1']
                rank = d['rank1']
                p = d['p1']
            rt[i] = index+time+roll+rank
        return rt[0], rt[1], True
    else:
        spacial_move = f'(?P<board>{SUPER_POSITION})?(?P<spacialmove>[^=]+)'
        m = re.match(spacial_move,move)

        if m:
            d = m.groupdict()
            if not d['board']:
                b = superspacialboard['0W0']
                while b.next:
                    b = b.next
                d['board'] = b.super_position
            board2d = superspacialboard[d['board']].board2d()
            move2d = board2d.push_san(d['spacialmove']).__str__()
            return d['board']+move2d[:2], d['board']+move2d[2:], False

if __name__ == '__main__':
    pieces: str = 'RNBKQP'
    move = '0W0e1='

    print(f'(?P<board>{SUPER_POSITION})(<spacialmove>.+)=')    
    print(parse_move(Board2d(),move))
