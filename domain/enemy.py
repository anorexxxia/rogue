from random import choice
from collections import namedtuple

EnemyStats = namedtuple('EnemyStats', ['show', 'health', 'agility', 'strength', 'hostility'])

class Enemy:
    stats = {"low": 4, "average": 7, "high": 10, 'very_high': 13}
    hostility_levels = {"low": 1, "average": 2, "high": 3}
    hp = {"low": 25, "average": 35, "high": 50}
    
    enemy_data = {
        'Зомби': EnemyStats('z', 'high', 'low', 'average', 'average'),
        'Вампир': EnemyStats('v', 'high', 'high', 'average', 'high'),
        'Призрак': EnemyStats('g', 'low', 'high', 'low', 'low'),
        'Огр': EnemyStats('O', 'high', 'low', 'high', 'average'),
        'Змей-маг': EnemyStats('s', 'low', 'very_high', 'low', 'high')
    }

    def __init__(self, y=None, x=None):
        self.type = choice(list(self.enemy_data.keys()))
        self.y = y
        self.x = x
        data = self.enemy_data[self.type]
        self.show = data.show
        self.health = self.hp[data.health]
        self.agility = self.stats[data.agility]
        self.strength = self.stats[data.strength]
        self.hostility = self.hostility_levels[data.hostility]
        self.persecution = False
        self.status = None
        self.treasure = self.tresuare_calculation()  # Расчет сокровищ врага при его создании
        if self.type == 'Вампир':
            self.first_hit = True  # Флаг для первого удара по вампиру
        if self.type == 'Огр':
            self.sleep_one_step = False # Флаг для сна огра на один ход после атаки

    def tresuare_calculation(self):
        """Расчет сокровищ врага в зависимости от его здоровья, силы, ловкости и приследования"""
        return self.health // 5 + self.strength // 2 + self.agility // 2 + self.hostility

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
        return self.health

    def is_alive(self):
        return self.health > 0
    
    def __str__(self):
        return f"{self.type} (HP: {self.health})"