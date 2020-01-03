
import libtcodpy as tcod

class BasicMonster:
    def take_turn(self, fov_map, game_map, entities):
        results = []

        # print('The ' + self.owner.name + ' wonders when it will get to move.')
        monster = self.owner
        if tcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(self.owner.target) >= 2:
                monster.move_astar(entities, game_map)

            elif self.owner.target._class.hp > 0:
                attack_res = monster._class.attack(self.owner.target)
                results.extend (attack_res)
        
        return results