from message_log import Message

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        # Result for death of monster
        if self.hp <= 0:
            print (self.owner)
            results.append({'dead': self.owner})

        return results

    def attack(self, target):
        results = []

        damage = self.power - target._class.defense

        # Result for hit
        if damage > 0:
            target._class.take_damage(damage)
            results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)))})
            results.extend(target._class.take_damage(damage))
        # Result for no damage
        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name))})

        return results