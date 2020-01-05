from Entities.entity import Entity
import libtcodpy as tcod
from renderer import RenderOrder
from components import classes
from components import enemyAI

class Monster ():
    def __init__(self):
        pass

    def get (self):
        return self.monster

class Orc (Monster):
    def __init__(self, x, y, target=None):
        self.monster = Entity(x, y, 'o', tcod.desaturated_green, 'Orc', blocks=True, renderOrder=RenderOrder.ACTOR, _class=classes.Fighter(hp=10, defense=1, power=5), ai=enemyAI.BasicMonster(), target=target)

class Troll (Monster):
    def __init__(self, x, y, target=None):
       self.monster = Entity(x, y, 'T', tcod.darker_green, 'Troll', blocks=True, renderOrder=RenderOrder.ACTOR, _class=classes.Fighter(hp=16, defense=2, power=7), ai=enemyAI.BasicMonster(), target=target)