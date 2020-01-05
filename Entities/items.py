from Entities.entity import Entity
import libtcodpy as tcod
from renderer import RenderOrder

class Item:
    def __init__(self):
        pass

    def get(self):
        return self.item

class HealingPotion(Item):
    def __init__(self, x, y):
        self.item = Entity(x, y, '!', tcod.violet, 'Healing Potion', item=Item(), renderOrder=RenderOrder.ITEM)