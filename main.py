from tkinter import Tk, Text, END, font


class Game:

    def __init__(self,
                 width=80,
                 height=24,
                 title="Untitled",
                 active_keys=None):

        self._root = Tk()
        self._root.resizable(False, False)
        self._root.title(title)
        if active_keys is None:
            active_keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                           'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                           'u', 'v', 'w', 'x', 'y', 'z',
                           '<Left>', '<Right>', '<Down>', '<Up>']
        for key in active_keys:
            self._root.bind(key, self._render)
        self.width = width
        self.height = height
        print("List of available fonts:")
        print(font.families())
        self._text = Text(
            self._root,
            width=self.width,
            height=self.height,
            bg='black',
            fg='white',
            font=('Dejavu Sans Mono', 20),
        )
        self._text.insert('1.0', ' ' * (self.width * self.height))
        self._text.pack()
        self._text['state'] = 'disabled'

    def _render(self, event):
        self._text['state'] = 'normal'
        self._text.delete('1.0', END)
        content = self.loop(event)
        if len(content) == self.width * self.height:
            self._text.insert('1.0', content)
        else:
            raise ValueError("Game.loop(event) must return a string of "
                             "length {}x{}".format(self.width, self.height))
        self._text.pack()
        self._text['state'] = 'disabled'

    def loop(self, event):
        raise NotImplementedError("Subclass must implement Game.loop(event).")

    def run(self):
        self._root.mainloop()


# Usage example:
import random
import string
from functools import reduce
from dataclasses import dataclass, replace
from typing import List


@dataclass
class Drawable:

    x: int
    y: int
    z: int

    @property
    def char(self):
        return 'Z'

    def tick(self, objs, ev, query):
        raise NotImplementedError


@dataclass
class Wall(Drawable):

    z: int = 1

    @property
    def char(self):
        return '#'

    def tick(self, objs, ev, query):
        pass


@dataclass
class Flame(Drawable):

    z: int = 100

    @property
    def char(self):
        return '*'

    def tick(self, objs, ev, query):
        objs.remove(self)
        if (self.x, self.y) in query:
            for obj in query[(self.x, self.y)]:
                if isinstance(obj, Wall):
                    objs.remove(obj)
                elif isinstance(obj, Bomb) or isinstance(obj, TNT):
                    obj.detonate(objs)
                elif isinstance(obj, Player):
                    obj.dead = True


@dataclass
class Bomb(Drawable):

    secs: int

    @property
    def char(self):
        return 'o'

    def detonate(self, objs):
        objs.append(Flame(self.x, self.y, 100))
        objs.append(Flame(self.x + 1, self.y, 100))
        objs.append(Flame(self.x - 1, self.y, 100))
        objs.append(Flame(self.x, self.y + 1, 100))
        objs.append(Flame(self.x, self.y - 1, 100))
        if self in objs:
            objs.remove(self)

    def tick(self, objs, ev, query):
        if self.secs == 0:
            self.detonate(objs)
        else:
            self.secs -= 1


@dataclass
class TNT(Drawable):

    @property
    def char(self):
        return '/'

    def detonate(self, objs):
        for i in range(-3, 3, 1):
            for j in range(-3, 3, 1):
                objs.append(Flame(self.x + i, self.y + j, 100))
        if self in objs:
            objs.remove(self)

    def tick(self, objs, ev, query):
        pass


@dataclass
class Player(Drawable):

    z: int = 100
    dead: bool = False

    @property
    def char(self):
        if self.dead:
            return 'x'
        return '@'

    def tick(self, objs, ev, query):
        if self.dead:
            return
        nx = self.x
        ny = self.y
        if ev.keysym == 'Left':
            nx -= 1
        elif ev.keysym == 'Right':
            nx += 1
        elif ev.keysym == 'Up':
            ny -= 1
        elif ev.keysym == 'Down':
            ny += 1
        elif ev.keysym == 'a':
            objs.append(Bomb(self.x, self.y, 100, 4))
        elif ev.keysym == 'd':
            objs.append(TNT(self.x, self.y, 100))

        if (nx, ny) in query:
            for obj in query[(nx, ny)]:
                if isinstance(obj, Wall):
                    return
        self.x = nx
        self.y = ny


class Rogue(Game):

    objects = [
        Player(5, 5),
        Wall(10, 10),
        Wall(10, 9),
        Wall(10, 8),
        Wall(10, 7),
        Wall(10, 6),
        Wall(10, 5),
        Wall(10, 4),
        Wall(9, 4),
        Wall(8, 4),
        Wall(7, 4),
        Wall(6, 4),
        Wall(5, 4),
        Wall(4, 4),
    ]
    query = {}

    def render(self):

        out = ''
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.query:
                    maxz = 0
                    maxobj = None
                    for obj in self.query[(x, y)]:
                        if obj.z > maxz:
                            maxz = obj.z
                            maxobj = obj
                    out += maxobj.char
                else:
                    out += '.'
        return out
    
    def loop(self, ev):
        objs = self.objects.copy()
        for obj in self.objects:
            obj.tick(objs, ev, self.query)

        # create query
        self.query = {}
        for obj in objs:
            if (obj.x, obj.y) in self.query:
                self.query[(obj.x, obj.y)].append(obj)
            else:
                self.query[(obj.x, obj.y)] = [obj]

        screen = self.render()
        self.objects = objs
        return screen

Rogue().run()
