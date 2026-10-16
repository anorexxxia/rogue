from random import randint, shuffle, choice
from .room import Room
from .item import Item
from .enemy import Enemy

class GenerateLvl:
    # Размер всего уровня (терминал)
    LEVEL_WIDTH = 100
    LEVEL_HEIGHT = 40

    # Сколько секций по горизонтали и вертикали
    SECTIONS_X = 3  
    SECTIONS_Y = 3  

    # Размер одной секции
    SECTION_WIDTH = LEVEL_WIDTH // SECTIONS_X   # ≈ 40
    SECTION_HEIGHT = LEVEL_HEIGHT // SECTIONS_Y # ≈ 13

    def __init__(self, player, lvl=1, chance_spawn_enemy=40, chance_spawn_item=70):
        self.lvl = lvl
        self.rooms = self.generate_level() #list of Room's
        self.corridors = self.generate_corridors_random(self.rooms) #list
        self.map_grid = self.create_map_grid() #list
        self.items = []  # Список всех сущностей на уровне (для удобства)
        self.enemy = []
        choice(self.rooms).start_room = True  # Стартовая комната — случайная
        choice([room for room in self.rooms if not room.start_room]).exit_room = True  # Выбираем комнату, которая не стартовая, как конечную
        self.chance_spawn_enemy = chance_spawn_enemy
        self.chance_spawn_item = chance_spawn_item
        self.exit_y = None
        self.exit_x = None
        self.player = self.filling_the_world(player)  # Заполняем уровень врагами и предметами
        if self.lvl > 1:
            self.strengthening_enemies()


    @staticmethod
    def strengthening_enemies():
        for stat in Enemy.stats:
            Enemy.stats[stat] += 1
        
        for h in Enemy.hp:
            Enemy.hp[h] += 2


    def filling_the_world(self, player):
        for room in self.rooms:
            if room.start_room:  # Спавним игрока только в первой комнате первого уровня:
                player.y = randint(room.lvl_y + 1, room.lvl_y + room.y - 2)
                player.x = randint(room.lvl_x + 1, room.lvl_x + room.x - 2)
                room.update_entity_position(player, player.y, player.x)
            else:
                item = room.spawn_entity(Item, chance=self.chance_spawn_item) # Спавним врагов и предметы в остальных комнатах
                enemy = room.spawn_entity(Enemy, chance=self.chance_spawn_enemy)
                if item:
                    self.update_entity_position(item, item.y, item.x)  # Обновляем позицию предмета на карте уровня
                    self.items.append(item)  # Добавляем предмет в список предметов уровня
                if enemy:
                    if enemy.type == 'Призрак':
                        enemy.lvl_y = room.lvl_y
                        enemy.lvl_x = room.lvl_x
                        enemy.room_y = room.y
                        enemy.room_x = room.x
                    self.update_entity_position(enemy, enemy.y, enemy.x)  # Обновляем позицию врага на карте уровня
                    self.enemy.append(enemy)  # Добавляем врага в список врагов уровня
                if room.exit_room:  # Если это комната с выходом, то спавним там выход
                    while True:
                        y = randint(room.lvl_y + 1, room.lvl_y + room.y - 2)
                        x = randint(room.lvl_x + 1, room.lvl_x + room.x - 2)
                        if self.is_passable(y, x):
                            self.exit_y = y
                            self.exit_x = x
                            self.map_grid[y][x] = '∏'  # Символ выхода
                            break

        return player  

    def is_passable(self, y, x):
        """Проверяет, можно ли пройти в клетку (y, x) на карте уровня"""
        if 0 <= y < self.LEVEL_HEIGHT and 0 <= x < self.LEVEL_WIDTH:
            return self.map_grid[y][x] == '.'
            # return self.map_grid[y][x] in ['.', '๑', '†', '₪', '☤']  # Проходимые клетки: пол, игрок, предмет, враг
        return False
    
    def update_entity_position(self, entity, new_y, new_x):
        """Обновляет позицию сущности на карте уровня"""
        if entity is None:
            return
        
        # Стираем старое положение
        if 0 <= entity.y < self.LEVEL_HEIGHT and 0 <= entity.x < self.LEVEL_WIDTH:
            self.map_grid[entity.y][entity.x] = '.'
        
        # Рисуем новое положение
        if 0 <= new_y < self.LEVEL_HEIGHT and 0 <= new_x < self.LEVEL_WIDTH:
            self.map_grid[new_y][new_x] = entity.show
            entity.y = new_y
            entity.x = new_x
    
    def create_map_grid(self):
        """Создаёт общую карту уровня, объединяя комнаты и коридоры"""
        map_grid = [[' ' for _ in range(self.LEVEL_WIDTH)] for _ in range(self.LEVEL_HEIGHT)]

        # Рисуем коридоры
        for corridor in self.corridors:
            for x, y in corridor:
                if 0 <= y < self.LEVEL_HEIGHT and 0 <= x < self.LEVEL_WIDTH and map_grid[y][x] != '.':
                    map_grid[y-1][x] = '▓'
                    map_grid[y+1][x] = '▓'
                    map_grid[y][x-1] = '▓'
                    map_grid[y][x+1] = '▓'

        # Рисуем комнаты▓
        for room in self.rooms:
            for y in range(room.y):
                for x in range(room.x):
                    map_y = room.lvl_y + y
                    map_x = room.lvl_x + x
                    if 0 <= map_y < self.LEVEL_HEIGHT and 0 <= map_x < self.LEVEL_WIDTH:
                        map_grid[map_y][map_x] = room.get_cell(map_y, map_x)

        # Рисуем коридоры
        for corridor in self.corridors:
            for x, y in corridor:
                if 0 <= y < self.LEVEL_HEIGHT and 0 <= x < self.LEVEL_WIDTH and map_grid[y][x] != '.':
                    map_grid[y][x] = '.'
        
        return map_grid

    def generate_room_in_section(self, section_index):
        """
        Генерирует комнату внутри заданной секции
        """
        # Определяем, в какой строке и столбце секция
        section_x = section_index % self.SECTIONS_X  # 0, 1, 2
        section_y = section_index // self.SECTIONS_X  # 0, 1, 2
        
        # Границы секции
        sec_left = section_x * self.SECTION_WIDTH
        sec_top = section_y * self.SECTION_HEIGHT
        
        # Отступ от краёв секции (чтобы комната не прилипала к границам)
        margin = 2
        
        # Максимальные размеры комнаты
        max_width = self.SECTION_WIDTH - 2 * margin
        max_height = self.SECTION_HEIGHT - 2 * margin
        
        # Случайные размеры комнаты (минимум 3×3)
        width = randint(6, max_width)
        height = randint(6, max_height)
        
        # Случайное положение внутри секции
        x = sec_left + margin + randint(0, self.SECTION_WIDTH - width - 2 * margin)
        y = sec_top + margin + randint(0, self.SECTION_HEIGHT - height - 2 * margin)
        
        return Room(y, x, height, width)
    
    def generate_level(self):
        """Генерирует уровень с 9 комнатами"""
        rooms = []
        
        for section_index in range(9):  # 0, 1, 2, ..., 8
            room = self.generate_room_in_section(section_index)
            rooms.append(room)
        
        return rooms

    def create_corridor(self, room1, room2):
        """Создаёт коридор между двумя комнатами (по прямой линии)"""
        x1, y1 = room1.center()
        x2, y2 = room2.center()
        
        corridor = []
        
        # Двигаемся горизонтально от (x1, y1) к (x2, y1)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            corridor.append((x, y1))
        # Двигаемся вертикально от (x2, y1) к (x2, y2)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            corridor.append((x2, y))

        return corridor
    
    def generate_corridors_random(self, rooms):
        # Все возможные соединения между соседними комнатами
        possible_connections = [
            (0, 1), (1, 2),  # верхняя строка
            (3, 4), (4, 5),  # средняя строка
            (6, 7), (7, 8),  # нижняя строка
            (0, 3), (3, 6),  # левый столбец
            (1, 4), (4, 7),  # средний столбец
            (2, 5), (5, 8),  # правый столбец
        ]

        shuffle(possible_connections)  # Перемешиваем порядок соединений

        corridors = []
        connect_rooms = set()  # Множество уже соединённых комнат

        while len(connect_rooms) != 9 or not self.check_connectivity(rooms, corridors):  # Пока не все комнаты соединены
            room1_idx, room2_idx = possible_connections.pop()  # Берём следующее соединение из перемешанного списка
            corridor = self.create_corridor(rooms[room1_idx], rooms[room2_idx])
            corridors.append(corridor)
            connect_rooms |= {room1_idx, room2_idx}  # Добавляем обе комнаты в множество соединённых

        return corridors

    def check_connectivity(self, rooms, corridors):
        """Проверяет, что все комнаты связаны коридорами (для отладки)"""
        # Создаём граф комнат
        graph = {i: set() for i in range(len(rooms))}
        
        for corridor in corridors:
            # Находим, какие комнаты соединяет этот коридор
            connected_rooms = set()
            for x, y in corridor:
                for i, room in enumerate(rooms):
                    if (room.lvl_x <= x < room.lvl_x + room.x and
                        room.lvl_y <= y < room.lvl_y + room.y):
                        connected_rooms.add(i)
            
            # Добавляем рёбра в граф
            for r1 in connected_rooms:
                for r2 in connected_rooms:
                    if r1 != r2:
                        graph[r1].add(r2)
                        graph[r2].add(r1)
        
        # Проверяем связность графа (DFS или BFS)
        visited = set()
        
        def dfs(node):
            visited.add(node)
            for neighbor in graph[node]:
                if neighbor not in visited:
                    dfs(neighbor)
        
        dfs(0)  # Начинаем с первой комнаты
        
        return len(visited) == len(rooms)  # Все комнаты должны быть посещены
