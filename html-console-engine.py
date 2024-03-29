from chess5d import *
import matplotlib.pyplot as plt

import webbrowser
import os
import pathlib
from yattag import Doc
import re

class Game:
    def __init__(self):
        self.board = SuperspacialBoard()
        self.board.default_fill()
    
    def write_html(self):
        doc, tag, text = Doc().tagtext()

        with tag('html'):
            with tag('body'):

                    files = os.listdir("svgs")
                    mini = int(np.min([SuperPosition(file[:len(file)-4]).index for file in files]))
                    mint = int(2*np.min([SuperPosition(file[:len(file)-4]).time for file in files]))
                    maxi = int(np.max([SuperPosition(file[:len(file)-4]).index for file in files]))
                    maxt = int(2*np.max([SuperPosition(file[:len(file)-4]).time for file in files]))
                    for t in range(mint,maxt+1):
                        with tag('div', style = '''white-space: nowrap;'''):
                            for i in range(mini,maxi+1):
                                with tag(
                                        'image', 
                                        src = f'./svgs/{SuperPosition(i,t/2)}.svg',
                                        width = '300px',
                                        height = '300px'): pass
                        doc.nl()
            
        with open('chess.html', 'w') as f:
            f.write(doc.getvalue())


    def write_svg(self,super_position):
        svgtext = self.board[super_position].svg()
        with open(f'svgs/{super_position}.svg', 'w') as f:
            f.write(svgtext)
    
    def write_svgs(self):
        for super in self.board.spacial_boards.keys():
            self.write_svg(super)

def main():
    url = f'file:///{pathlib.Path().resolve()}/chess.html'
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    game = Game()
    game.write_svgs()
    game.write_html()
    

    driver = webdriver.Chrome()
    driver.get(url)
    command = input()
    while command != 'exit':
        game.board.push_move(command)
        game.write_svgs()
        game.write_html()
        driver.refresh()
        command = input()
    driver.close()

if __name__ == "__main__":
    main()
        