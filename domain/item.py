from random import choice, randint

class Item:
    food = {'хлеб': 15, 'хвост волка': 5, 'Селедка': 13, "пирог": 25, 'гниль': 1, 'бутерброд': 18, 'бульмени(от горячей штучки)': 22, 'булдак': -1, 'МЯСО': 41}
    flasks = {'хп-фляга': {'count': 20, 'time': 15}, 'зеленая фляга': {'count': 5, 'time': 15}, 'красная фляга': {'count': 5, 'time': 15}}
    scrolls = {'свиток-хп': 10, "свиток силы": 2, "свиток ловкости": 2}
    weapons = {'Зуб Дракона': 25, 'Утигатана': 20, "ветка от дерева": 3, 'Кинжал Присциллы': 10, 'Меч Черного Рыцаря': 30, 'Цестус': 15}
    type_item = {'еда': food, 'оружие': weapons, 'свитки': scrolls, 'фляги': flasks}

    def __init__(self, y=None, x=None):
        self.type = choice(list(self.type_item.keys()))
        self.subtype = choice(list(self.type_item[self.type].keys()))
        self.y = y
        self.x = x
        if self.type == 'еда':
            self.health = self.food[self.subtype]
            self.show = '๑'
        elif self.type == 'оружие':
            self.strength = self.weapons[self.subtype]
            self.damage = self.convert_damage()
            self.show = '†'
        elif self.type == 'свитки':
            self.show = '₪'
            self.max_health = self.scrolls[self.subtype] if self.subtype == 'свиток-хп' else 0
            self.agility = self.scrolls[self.subtype] if self.subtype == 'свиток ловкости' else 0
            self.strength = self.scrolls[self.subtype] if self.subtype == 'свиток силы' else 0
        elif self.type == 'фляги':
            self.show = '☤'
            self.max_health = self.flasks[self.subtype]['count'] if self.subtype == 'хп-фляга' else 0
            self.agility = self.flasks[self.subtype]['count'] if self.subtype == 'зеленая фляга' else 0
            self.strength = self.flasks[self.subtype]['count'] if self.subtype == 'красная фляга' else 0    
            self.time = self.flasks[self.subtype]['time']
    
    def convert_damage(self):
        """Конвертация силы оружия в урон"""
        match self.subtype:
            case 'Кинжал Присциллы':
                return self.strength * 2
            case 'Зуб Дракона':
                return self.strength * 1.5
            case 'Цестус':
                return self.strength * 1.1
            case _:
                return self.strength

    def update_init(self, **kwargs):
        self.type = kwargs['type']
        self.subtype = kwargs['subtype']
        self.y = kwargs['y']
        self.x = kwargs['x']
        self.show = kwargs['show']
        if self.type == 'еда':
            self.health = kwargs['health']
        elif self.type == 'оружие':
            self.strength = kwargs['strength']
            self.damage = self.convert_damage()
        elif self.type == 'свитки':
            self.max_health = kwargs['max_health']
            self.agility = kwargs['agility']
            self.strength = kwargs['strength']
        elif self.type == 'фляги':
            self.max_health = kwargs['max_health']
            self.agility = kwargs['agility']
            self.strength = kwargs['strength']
            self.time = kwargs['time']
        return self

class Treasures(Item):
    def __init__(self):
        self.type = 'Сокровище'
        self.count = randint(5, 80)




