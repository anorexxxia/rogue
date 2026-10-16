from random import randint


class Room:
    def __init__(self, lvl_y, lvl_x, y, x):
        self.lvl_y = lvl_y
        self.lvl_x = lvl_x
        self.y = y
        self.x = x
        self.room = self.create_room()
        self.start_room = False
        self.exit_room = False

    def center(self):
        """Возвращает координаты центра комнаты"""
        return (self.lvl_x + self.x // 2, self.lvl_y + self.y // 2)

    def create_room(self):
        return [['▓' if x == 0 or x == self.x-1 or y == 0 or y == self.y-1 else '.' for x in range(self.x)] for y in range(self.y)]

    def is_passable(self, y, x):
        """Можно ли пройти в клетку (y, x)?"""
        if self.lvl_y <= y < self.lvl_y + self.y and self.lvl_x <= x < self.lvl_x + self.x:
            return self.room[y - self.lvl_y][x - self.lvl_x] == '.'
        return False
    
    def get_cell(self, y, x):
        """Возвращает символ клетки"""
        if self.lvl_y <= y < self.lvl_y + self.y and self.lvl_x <= x < self.lvl_x + self.x:
            return self.room[y - self.lvl_y][x - self.lvl_x]
        return "F"

    def spawn_entity(self, entity=None, chance: int = 100, attempts: int = 10):
        """ Спавн энтити в комнате"""
        if randint(1, 100) > chance:
            return None

        while attempts > 0:
            x = randint(self.lvl_x + 1, self.lvl_x + self.x - 2)
            y = randint(self.lvl_y + 1, self.lvl_y + self.y - 2)
            if self.is_passable(y, x):
                en = entity(y, x)
                self.update_entity_position(en, y, x)
                return en
            attempts -= 1

        return None

    def update_entity_position(self, entity, new_y, new_x):
        """Обновляет позицию сущности в комнате"""
        if entity is None:
            return
           
        self.room[entity.y - self.lvl_y][entity.x - self.lvl_x] = '.'
        self.room[new_y - self.lvl_y][new_x - self.lvl_x] = entity.show  # Или другой символ для сущности
        entity.y = new_y
        entity.x = new_x