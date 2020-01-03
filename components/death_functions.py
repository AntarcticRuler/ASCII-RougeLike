import libtcodpy as tcod

from game_states import GameStates

from renderer import RenderOrder

from message_log import Message

# Runs when the player is killed
def kill_player(player):
    player.char = '%'
    player.color = tcod.dark_red

    return Message('You died!', tcod.dark_red), GameStates.PLAYER_DEAD

# Runs when a monster is killed
def kill_monster(monster):
    print (monster)
    death_message = Message('{0} is dead!'.format(monster.name.capitalize()), tcod.orange)

    monster.char = '%'
    monster.color = tcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.renderOrder = RenderOrder.CORPSE

    return death_message