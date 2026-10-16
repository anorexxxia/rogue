from .backpack import Backpack
from .stat import Stat

class Character:
    def __init__(self, name='IGOR\'-stradalec', y=None, x=None):
        self.name = name
        self.max_health = 100
        self.health = 100
        self.agility = 10
        self.strength = 10
        
        self.current_weapon = None
        self.backpack = Backpack()

        self.time_frame_max_health = 0
        self.work_time_flask_h = 0
        self.stat_flask_heath = None
        self.time_frame_agillity = 0
        self.work_time_flask_agil = 0
        self.stat_flask_agil = None
        self.time_frame_strenth = 0
        self.work_time_flask_str = 0
        self.stat_flask_str = None

        self.y = y
        self.x = x

        self.show = '☻'
        self.status = ''
        self.skip_move = False
        self.steps = 0
        self.stat = Stat()

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return self.health
    
    def heals(self, item):
        if item.type == "еда":
            self.health += item.health
        else:
            self.health += item.max_health

        if self.health > self.max_health:
            self.health = self.max_health

    def eat_the_food(self, item):
        self.heals(item)
        return f"использовано {item.subtype}, восстановило {item.health} HP"


    def use_a_scroll(self, item):
        self.max_health += item.max_health
        self.heals(item)
        self.agility += item.agility
        self.strength += item.strength
        for key, value in item.__dict__.items():
            if type(value) is int:
                if value > 0 and key != 'time':
                    if item.type == 'фляги':
                        return f"использована {item.subtype}, увеличено {key} на {value} на {item.time} ходов"
                    else:
                        return f"использовано {item.subtype}, увеличено {key} на {value}"


    def use_a_flask(self, item):
        self.use_a_scroll(item)
        match item.subtype:
            case 'хп-фляга':
                self.time_frame_max_health = item.time
                self.work_time_flask_h += 1
                self.stat_flask_heath = item.max_health
            case 'зеленая фляга':
                self.time_frame_agillity = item.time
                self.work_time_flask_agil += 1
                self.stat_flask_agil = item.agility
            case 'красная фляга':
                self.time_frame_strenth = item.time
                self.work_time_flask_str += 1
                self.stat_flask_str = item.strength

    def check_time_flask(self):
        if self.time_frame_max_health > 0:
            self.time_frame_max_health -= 1
        elif self.time_frame_max_health == 0 and self.work_time_flask_h:
            self.work_time_flask_h -= 1
            self.max_health -= self.stat_flask_heath
            if self.health > self.max_health:
                self.health = self.max_health
            if not self.work_time_flask_h:
                self.stat_flask_heath = None

        if self.time_frame_agillity > 0:
            self.time_frame_agillity -= 1
        elif self.time_frame_agillity == 0 and self.work_time_flask_agil:
            self.work_time_flask_agil -=1
            self.agility -= self.stat_flask_agil
            if not self.work_time_flask_agil:
                self.stat_flask_agil = None

        if self.time_frame_strenth > 0:
            self.time_frame_strenth -= 1
        elif self.time_frame_strenth == 0 and self.work_time_flask_str:
            self.work_time_flask_str -= 1
            self.strength -= self.stat_flask_str
            if not self.work_time_flask_str:
                self.stat_flask_str = None

    def use_item(self, item):
        match item.type:
            case "еда":
                res = self.eat_the_food(item)
                self.stat.skushol += 1
            case "свитки":
                res = self.use_a_scroll(item)
                self.stat.prochital += 1
            case "фляги":
                res = self.use_a_flask(item)
                self.stat.vipil += 1
        
        return res
            
    def is_alive(self):
        return self.health > 0

    def __str__(self):
        return f"{self.name}: HP {self.health}/{self.max_health}, ловкость {self.agility}, сила {self.strength}"