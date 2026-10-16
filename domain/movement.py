from random import randint, choice
from domain.combat import attack_enemy, player_attack
from domain.generate_lvl import GenerateLvl

class Movement:
    # Огр двигается по 2 клетки
    directions_oger = [(0, 2), (0, -2), (2, 0), (-2, 0)]
    # Змея двигается по диагонали
    directions_snake = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    # Другие враги двигаются случайно
    directions_other = [(0, 1), (0, -1), (1, 0), (-1, 0)]


    def character_movement(self, player, lvl, key, dt, item=None, enemy=None):
        """Логика движения персонажа в комнате"""
        if lvl.lvl == 22:
            return
        
        if not player.is_alive():
            return "YOU DIED"

        new_y, new_x = player.y, player.x
        
        # Логика движения — тоже в отдельном классе GameLoop позже!
        if key == ord('w'): new_y -= 1
        elif key == ord('s'): new_y += 1
        elif key == ord('a'): new_x -= 1
        elif key == ord('d'): new_x += 1

        if player.skip_move:
            player.skip_move = False  # Сбрасываем флаг пропуска хода
            player.status = "Вы пропускаете ход из-за эффекта змей-мага!"  # Обновляем статус персонажа
            return

        if lvl.is_passable(new_y, new_x): # ← domain проверяет возможность хода
            lvl.update_entity_position(player, new_y, new_x)
            player.check_time_flask()
            player.steps += 1  # Увеличиваем счетчик шагов персонажа
            player.stat.steps += 1
            player.status = 'Волосы назад                       '  # Обновляем статус персонажа при движении
        elif lvl.map_grid[new_y][new_x] == '▓':
            player.status = 'Тормоз? стена же                '  # Обновляем статус персонажа при столкновении со стеной

        if self.check_coordinates_is_item(new_y, new_x, lvl):
            item = self.get_item_at_coordinates(new_y, new_x, lvl)
            if item:
                if self.pick_up_item(player, player.backpack, item):
                    lvl.update_entity_position(player, new_y, new_x)  # Обновляем позицию игрока после поднятия предмета
                    player.status = f"Вы подобрали предмет '{item.subtype}'!"
                else:
                    lvl.update_entity_position(player, new_y, new_x)

        if self.check_coordinates_is_enemy(new_y, new_x, lvl):
            enemy = self.get_enemy_at_coordinates(new_y, new_x, lvl)
            if enemy:
                player.status = player_attack(player, enemy)
                return
        
        if lvl.map_grid[new_y][new_x] == '∏':  # Если игрок наступил на выход
            player.stat.lvl += 1
            new_lvl = GenerateLvl(player, lvl.lvl+1, chance_spawn_item=lvl.chance_spawn_item-1, chance_spawn_enemy=lvl.chance_spawn_enemy+1)
            dt.make_session() #убрать в уровни
            dt.session_to_json(player, new_lvl)
            return new_lvl

    def get_item_at_coordinates(self, y, x, lvl):
        """Получает предмет по координатам (y, x) на карте уровня"""
        for item in lvl.items:
            if item.y == y and item.x == x:
                return item
        return None

    def check_coordinates_is_item(self, y, x, lvl):
        if lvl.map_grid[y][x] in ['๑', '†', '₪', '☤']:
            return True

    def get_enemy_at_coordinates(self, y, x, lvl):
        """Получает врага по координатам (y, x) на карте уровня"""
        for enemy in lvl.enemy:
            if enemy.y == y and enemy.x == x:
                return enemy
        return None

    def check_coordinates_is_enemy(self, y, x, lvl):
        if lvl.map_grid[y][x] in ['z', 'v', 'O', 's', 'g']:
            return True


    def check_coordinates_is_enemy_or_item(self, y, x, entity):
        """Проверяет совпадение координат игрока и врага или предмета"""
        return entity is not None and y == entity.y and x == entity.x

            
    def pick_up_item(self, player, backpack, item):
        """Логика поднятия предмета персонажем"""
        # if item is not None and player.y == item.y and player.x == item.x:
        if backpack.add_item(item, player):
            item.x, item.y = None, None  # Предмет убирается с пола
            return f"Предмет '{item.subtype}' поднят!, координаты: ({item.x}, {item.y})"  # Предмет был поднят
    
        return False  # Предмет не был поднят
    
    def move_enemy(self, enemy, lvl, player):
        """Логика движения врага в комнате"""
        if enemy is None:
            return
        
        # Простая логика: враг двигается в направлении героя
        dy = player.y - enemy.y
        dx = player.x - enemy.x  

        if abs(dy) == 1 and abs(dx) == 1:
            return  # Враг уже рядом с героем, не двигается

        new_y, new_x = enemy.y, enemy.x
        
        # Враг движется по диагонали, если игрок находится по диагонали
        if dy != 0 and dx != 0:
            new_y += 1 if dy > 0 else -1
            new_x += 1 if dx > 0 else -1
        elif abs(dy) > abs(dx):
            new_y += 1 if dy > 0 else -1
        else:
            new_x += 1 if dx > 0 else -1
        
        if lvl.is_passable(new_y, new_x):
            lvl.update_entity_position(enemy, new_y, new_x)


    def move_ghost(self, enemy, lvl):
        """Логика движения призрака в комнате"""
        if enemy is None:
            return
        
        if 20 > randint(1, 100):
            enemy.show = '.'  # Призрак становится невидимым
        else:
            enemy.show = 'g'  # Призрак становится видимым

        # Постоянно телепортируется по комнате
        while True:
            new_y = randint(enemy.lvl_y + 1, enemy.lvl_y + enemy.room_y - 2)
            new_x = randint(enemy.lvl_x + 1, enemy.lvl_x + enemy.room_x - 2)
            if lvl.is_passable(new_y, new_x):
                lvl.update_entity_position(enemy, new_y, new_x)
                break


    def move_other(self, enemy, lvl):
        """Логика движения других врагов в комнате"""
        if enemy is None:
            return

        match enemy.type:
            case 'Зомби'| 'Вампир':
                directions = self.directions_other
            case 'Огр':
                if enemy.sleep_one_step:
                    enemy.sleep_one_step = False  # Огр пропускает ход после атаки
                    return "Огр спит 1 ход и не наносит урона!       "  # Огр не наносит урон в этот ход
                directions = self.directions_oger
            case 'Змей-маг':
                directions = self.directions_snake

        while True:
            dy, dx = choice(directions)
            new_y = enemy.y + dy
            new_x = enemy.x + dx
            if lvl.is_passable(new_y, new_x):
                lvl.update_entity_position(enemy, new_y, new_x)
                break
    
    def pursuit_distance(self, enemy, player):
        """Проверяет, находится ли враг в зоне преследования героя"""
        if enemy is None:
            return False
        
        distance = max(abs(enemy.y - player.y), abs(enemy.x - player.x))
        return distance <= enemy.hostility

    def attack_zone(self, enemy, player):
        """Проверяет, находится ли враг в зоне атаки героя"""
        if enemy is None:
            return False
        
        distance = abs(enemy.y - player.y) + abs(enemy.x - player.x)
        return distance <= 1  # Враг атакует, если находится в соседней клетке


    def ai_move_enemy(self, enemy, lvl, player):
        """Логика движения врага в комнате с учетом ИИ"""
        if enemy is None or enemy.y is None and enemy.x is None:
            enemy.status = None
            return
        
        if not enemy.is_alive():
            player.backpack.backpack['сокровища'] += enemy.treasure  # Добавляем сокровища врага в рюкзак игрока
            player.stat.treasure += enemy.treasure
            player.stat.kill_mobs += 1
            lvl.map_grid[enemy.y][enemy.x] = '.'  # Убираем труп врага с поля
            enemy.y, enemy.x = None, None  # Враг убит, убираем его с поля
            enemy.status = f"{enemy.type} погибает от ваших рук!"
            return
        
        enemy.status = None
        enemy.persecution = self.pursuit_distance(enemy, player) # Враг начинает преследовать героя, если он в зоне преследования

        if not enemy.persecution:
            match enemy.type:
                case 'Призрак':
                    self.move_ghost(enemy, lvl)
                case _:
                    self.move_other(enemy, lvl)
        
        if enemy.persecution:
            self.move_enemy(enemy, lvl, player)

        if self.attack_zone(enemy, player):
            enemy.status = attack_enemy(enemy, player)
            return
            