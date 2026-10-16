import curses
from curses import panel


class GameRenderer:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.panels = {}
        self.wins = {}
        self.current_panel = None
        self.score_panel = None
        self.score_win = None

    def status(self, lvl, player, movement):
        self.stdscr.erase() # Очищаем окно статуса перед обновлением
        self.stdscr.addstr(0, 1, f"Статус: {lvl.player.status}")  # Выводим статус персонажа
        for enemy in lvl.enemy:
            movement.ai_move_enemy(enemy, lvl, player)  # Обрабатываем движение врага
            if enemy.status is not None:
                self.stdscr.addstr(2, 1, f"{str(enemy.status)}                 ")  # Выводим результат атаки врага в статус-бар
        self.stdscr.refresh()


    def info_bar(self):
        self.stdscr.border()
        self.stdscr.addstr(0, 5, " Информация ")
        self.stdscr.addstr(2, 2, " ╔═ Оружие и расходники ══════════╗")
        self.stdscr.addstr(3, 2, " ║ Оружие -〖 † 〗, Хот-кей-> 'h' ║")
        self.stdscr.addstr(4, 2, " ║ Еда    -〖 ๑ 〗, Хот-кей-> 'j' ║")
        self.stdscr.addstr(5, 2, " ║ Фляги  -〖 ☤ 〗, Хот-кей-> 'k' ║")
        self.stdscr.addstr(6, 2, " ║ Свитки -〖 ₪ 〗, Хот-кей-> 'e' ║")
        self.stdscr.addstr(7, 2, " ╚════════════════════════════════╝")

        self.stdscr.addstr(9, 2, " ╔═ Монстры ══════════════════════╗")
        self.stdscr.addstr(10, 2," ║ Зомби    -〘 z 〙              ║")
        self.stdscr.addstr(11, 2," ║ Вампир   -〘 v 〙              ║")
        self.stdscr.addstr(12, 2," ║ Призрак  -〘 g 〙              ║")
        self.stdscr.addstr(13, 2," ║ Огр      -〘 O 〙              ║")
        self.stdscr.addstr(14, 2," ║ Змей-маг -〘 s 〙              ║")
        self.stdscr.addstr(15, 2," ╚════════════════════════════════╝")

        self.stdscr.addstr(17, 2, " ВЫХОД С УРОВНЯ - [ ∏ ]")
        self.stdscr.refresh()

    def stat_bar(self, lvl, player):
        self.stdscr.erase()  # Очищаем окно статуса перед обновлением   
        self.stdscr.border()
        self.stdscr.addstr(0, 5, " Статистика персонажа ")
        self.stdscr.addstr(2, 2, f"Здоровье: {lvl.player.health}/{lvl.player.max_health}")
        self.stdscr.addstr(3, 2, f"Сила: {lvl.player.strength}")
        self.stdscr.addstr(4, 2, f"Ловкость: {lvl.player.agility}")
        self.stdscr.addstr(5, 2, f"Шаги: {lvl.player.steps}")
        self.stdscr.addstr(6, 2, f"Уровень: {lvl.lvl}")
        self.stdscr.addstr(9, 2, f"В руке: {player.current_weapon.subtype if player.current_weapon is not None else "пусто"}")
        self.render_backpack(player.backpack)
        self.stdscr.refresh()

    def death_or_win(self, status):
        self.stdscr.clear()
        self.stdscr.border()
        self.stdscr.addstr(20, 50, "   YOU DIED" if status == 'died' else 'НАКОНЕЦ-ТО ВЫБРАЛСЯ')
        self.stdscr.addstr(21, 50, "(ノಠ益ಠ)ノ彡┻━┻" if status == 'died' else '    ᕦ(ò_óˇ)ᕤ')
        self.stdscr.refresh()
        self.stdscr.getch()  # Ждем нажатия клавиши перед выходом
        curses.napms(3000)

    def render_lvl(self, generator, player):
        """Отрисовывает только видимые клетки"""
        # Получаем видимые клетки (передаем y, x)
        visible_cells = self.get_vision_bresenham(player.y, player.x, 8, generator)
        for y in range(len(generator.map_grid)):
            for x in range(len(generator.map_grid[y])):
                if generator.map_grid[y][x] != '▓':
                    self.stdscr.addch(y, x, ' ') 
        # Отрисовываем только видимые клетки
        for y, x in visible_cells:
            try:
                cell_char = generator.map_grid[y][x]

                if cell_char == '.':
                    self.stdscr.addch(y, x, cell_char, curses.color_pair(1) | curses.A_BOLD)
                elif cell_char == '▓':
                    self.stdscr.addch(y, x, cell_char, curses.color_pair(2))
                elif cell_char in ['๑', '†', '₪', '☤']:
                    self.stdscr.addch(y, x, cell_char, curses.color_pair(3) | curses.A_BLINK)
                else:
                    self.stdscr.addch(y, x, cell_char)
                
                # Отрисовываем предметы, если они есть в видимой клетке
                for item in generator.items:
                    if item.y == y and item.x == x:
                        self.render_item(item)  
            except curses.error:
                pass  # Игнорируем ошибки отрисовки за пределами окна
        
        self.stdscr.refresh()

    def get_vision_bresenham(self, py, px, radius, lvl):
        """Улучшенный алгоритм с использованием Брезенхэма"""
        visible = set()
        visible.add((py, px))
        
        # Для каждой точки на границе радиуса
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Пропускаем центр
                if dx == 0 and dy == 0:
                    continue
                
                # Целевая точка на границе радиуса
                target_x = px + dx
                target_y = py + dy
                
                # Нормализуем направление, если нужно достать до границы радиуса
                # (для длинных лучей)
                length = max(abs(dx), abs(dy))
                if length < radius:
                    # Масштабируем до границы радиуса
                    target_x = px + int(dx * radius / max(abs(dx), 1))
                    target_y = py + int(dy * radius / max(abs(dy), 1))
                
                # Получаем все клетки на линии от персонажа до целевой точки
                line = self.get_bresenham_line(px, py, target_x, target_y)
                
                # Идем по линии и останавливаемся у первой стены
                for x, y in line:
                    if not self.is_in_bounds(x, y, lvl):
                        break
                    
                    visible.add((y, x))
                    
                    if self.is_wall(x, y, lvl):
                        break
    
        return visible

    def get_bresenham_line(self, x1, y1, x2, y2):
        """Алгоритм Брезенхэма для получения всех клеток на линии"""
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        step_x = 1 if x2 > x1 else -1
        step_y = 1 if y2 > y1 else -1
        
        x, y = x1, y1
        
        if dx > dy:
            error = dx / 2.0
            for _ in range(dx + 1):
                points.append((x, y))
                x += step_x
                error -= dy
                if error < 0:
                    y += step_y
                    error += dx
        else:
            error = dy / 2.0
            for _ in range(dy + 1):
                points.append((x, y))
                y += step_y
                error -= dx
                if error < 0:
                    x += step_x
                    error += dy
        
        return points

    @staticmethod
    def is_in_bounds(x, y, lvl):
        """Проверка, находится ли клетка (x, y) в пределах карты"""
        return 0 <= x < len(lvl.map_grid[0]) and 0 <= y < len(lvl.map_grid)

    def is_wall(self, x, y, lvl):
        """Проверка, является ли клетка (x, y) стеной"""
        if not self.is_in_bounds(x, y, lvl):
            return True  # За границами считаем стеной
        return lvl.map_grid[y][x] == '▓'

    
    def render_room(self, room):
        """Отрисовывает комнату через curses"""
        for y in range(room.lvl_y, room.lvl_y + room.y):
            for x in range(room.lvl_x, room.lvl_x + room.x):
                try:
                    char = room.get_cell(y, x)
                    self.stdscr.addch(y, x, char)
                except curses.error:
                    pass

    def render_item(self, item):
        """Отрисовывает предмет на его координатах"""
        if item is None:
            return
        if item.x is not None and item.y is not None:
            self.stdscr.addch(item.y, item.x, item.show, curses.color_pair(3) | curses.A_BLINK | curses.A_BOLD)
        # self.stdscr.refresh()
        
    def render_enemy(self, enemy):
        if enemy is None:
            return
        if enemy.x is not None and enemy.y is not None:
            # Выбираем символ для отрисовки в зависимости от типа врага
            self.stdscr.addch(enemy.y, enemy.x, enemy.show) 


    def render_entity(self, entity):
        if entity is None:
            return
        if entity.x is not None and entity.y is not None:
            self.stdscr.addch(entity.y, entity.x, entity.show)
        self.stdscr.refresh()

    def render_backpack(self, backpack):
        """Отрисовывает содержимое рюкзака в правой части экрана"""
        x_offset = 22  # Сдвиг от левого края для рюкзака
        y_offset = 2   # Сдвиг от верхнего края для рюкзака

        self.stdscr.addstr(y_offset, x_offset, "Рюкзак:")
        y_offset += 1
        
        for item_type, items in backpack.backpack.items():
            if item_type == 'сокровища':
                self.stdscr.addstr(y_offset, x_offset, f"{item_type.capitalize()}: {items}")
                y_offset += 1
            else:
                self.stdscr.addstr(y_offset, x_offset, f"{item_type.capitalize()}: {len(items)}")
                y_offset += 1

    def render_status(self, hero):
        """Отрисовывает статус героя (здоровье, уровень и т.д.)"""
        x_offset = 20
        y_offset = 15
        self.stdscr.move(y_offset, x_offset)  # Перемещаем курсор в позицию для статуса
        self.stdscr.clrtoeol()  # Очищаем строку перед отрисовкой статуса
        self.stdscr.addstr(y_offset, x_offset, f"Здоровье: {hero.health}/{hero.max_health}, действие: {hero.status}")
        self.stdscr.refresh()

    def create_backpack_panels(self, backpack):
        """Создает все окна и панели на основе данных рюкзака"""
        
        # Создаем окна
        weapons = self._create_panel_window("оружие", backpack.backpack["оружие"])
        food = self._create_panel_window("еда", backpack.backpack["еда"])
        elex = self._create_panel_window("фляги", backpack.backpack["фляги"])
        scrolls = self._create_panel_window("свитки", backpack.backpack["свитки"])
        
        # Создаем панели curses
        pan_weapon = panel.new_panel(weapons)
        pan_weapon.hide()
        
        pan_food = panel.new_panel(food)
        pan_food.hide()
        
        pan_elex = panel.new_panel(elex)
        pan_elex.hide()
        
        pan_scrolls = panel.new_panel(scrolls)
        pan_scrolls.hide()
        
        # Сохраняем в словари
        self.panels = {
            'оружие': pan_weapon,
            'еда': pan_food,
            'фляги': pan_elex,
            'свитки': pan_scrolls
        }
        
        self.wins = {
            'оружие': weapons,
            'еда': food,
            'фляги': elex,
            'свитки': scrolls
        }
        
        return self.panels, self.wins
    
    def _create_panel_window(self, panel_type, items):
        """Вспомогательный метод для создания окна панели"""
        win = curses.newwin(18, 50, 10, 40)
        win.border()
        win.addstr(0, 1, f" {panel_type.capitalize()} ")
        for i, item in enumerate(items):
            if panel_type == 'оружие' and i == 0:
                win.addstr(i+2, 2, f"{i+1} - {item.subtype if item is not None else item} <")
            else:
                win.addstr(i+2, 2, f"{i+1} - {item.subtype if item is not None else item}           ")
        return win
    
    def refresh_panel_info(self, panel_name, backpack):
        """Обновляет содержимое конкретной панели"""
        win = self.wins[panel_name]
        win.erase()
        win.border()
        win.addstr(0, 1, f" {panel_name.capitalize()} ")
        
        for i, item in enumerate(backpack.backpack[panel_name]):
            if panel_name == 'оружие' and i == 0:
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize() if item is not None else item} [{item.weapons[item.subtype] if item is not None else '-'} DMG] <  ")
            elif panel_name == 'оружие' and i != 0:
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize() if item is not None else item} [{item.weapons[item.subtype] if item is not None else '-'} DMG]   ")
            elif panel_name == 'еда':
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize()} [{item.food[item.subtype]} - HP]    ") 
            elif panel_name == 'свитки' and item.subtype == 'свиток-хп':
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize()} [ МАКС-ЗД {item.scrolls[item.subtype]} ↑ ]    ")
            elif panel_name == 'свитки' and item.subtype == 'свиток силы':
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize()} [ СИЛ {item.scrolls[item.subtype]} ↑ ]    ")
            elif panel_name == 'свитки' and item.subtype == 'свиток ловкости':
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize()} [ ЛВК {item.scrolls[item.subtype]} ↑ ]    ")       
            else:
                win.addstr(i+2, 2, f"{i+1} - {item.subtype.capitalize() if item is not None else item}         ")

    def handle_panel_logic(self, current_panel):

        if self.panels[current_panel].hidden():
            for pan in self.panels.values():
                pan.hide()
            self.panels[current_panel].top()
            self.panels[current_panel].show()

    def handle_key(self, key, backpack, stat_bar, stdscr, stat, records):
        if key == ord('j'):
            current_panel = 'еда'
            if self.panels[current_panel].hidden():
                self.handle_panel_logic(current_panel)
                self.refresh_panel_info(current_panel, backpack)
            else:
                self.panels[current_panel].hide()
                current_panel = None
            stat_bar.refresh()
            stdscr.refresh()
            return current_panel
        elif key == ord('k'):
            current_panel = 'фляги'
            if self.panels[current_panel].hidden():
                self.handle_panel_logic(current_panel)
                self.refresh_panel_info(current_panel,backpack)
            else:
                self.panels[current_panel].hide()
                current_panel = None
            stat_bar.refresh()
            stdscr.refresh()
            return current_panel
        elif key == ord('e'):
            current_panel = 'свитки'
            if self.panels[current_panel].hidden():
                self.handle_panel_logic(current_panel)
                self.refresh_panel_info(current_panel, backpack)
            else:
                self.panels[current_panel].hide()
                current_panel = None
            stat_bar.refresh()
            stdscr.refresh()
            return current_panel
        elif key == ord('h'):
            current_panel = 'оружие'
            if self.panels[current_panel].hidden():
                self.handle_panel_logic(current_panel)
                self.refresh_panel_info(current_panel, backpack)
            else:
                self.panels[current_panel].hide()
                current_panel = None
            stat_bar.refresh()
            stdscr.refresh()
            return current_panel
        elif key == ord('p'):
            current_panel = 'статистика'
            if self.score_panel.hidden():
                self.refresh_score_panel(self.score_win, stat, records)
                self.score_panel.top()
                self.score_panel.show()
            else:
                self.score_win.erase()
                self.score_panel.hide()
                stat_bar.refresh()
            self.score_win.refresh()
            return current_panel
        return None

    def handle_opened_panel(self, current_panel, backpack, key, stat_bar, stdscr, player):
        back = backpack.backpack
        digit = key - 48

        if digit in range(1, len(back[current_panel])+1):
            used_item = backpack.use_item_from_backpack(current_panel, digit)
            player.use_item(used_item)
            self.panels[current_panel].hide()
            self.refresh_panel_info(current_panel, backpack)
        else: 
            self.panels[current_panel].hide()
        stat_bar.refresh()
        stdscr.refresh()
        return None


    def handle_weapon_panel(self, current_panel, backpack, key, stat_bar, player):
        back = backpack.backpack
        digit = key - 49

        if digit in range(len(back[current_panel])):
            backpack.handle_weapons_logic(digit, back, current_panel, player, stat_bar)
            self.panels[current_panel].hide()
            self.refresh_panel_info(current_panel, backpack)
        else: 
            self.panels[current_panel].hide()
        stat_bar.refresh()
        self.stdscr.refresh()
        return None
        
    def create_score_panel(self):
        win = curses.newwin(20, 40, 1, 125)
        panel_stat = panel.new_panel(win)
        panel_stat.hide()
        self.score_panel = panel_stat
        self.score_win = win

    def refresh_score_panel(self, win, stat, records):
        win.border()
        win.addstr(0, 5, " Статистика/лидерборд ")
        win.addstr(2, 1, " ╔════════════════╤═════════════════╗")
        win.addstr(3, 2, f"║ Голда:     {stat.treasure} ")
        win.addstr(3, 19, f"│ ЛВЛ:        {stat.lvl}   ")
        win.addstr(3, 37, "║")
        win.addstr(4, 2, f"║ Шагомер:   {stat.steps}")
        win.addstr(4, 19, f"│ Снес мобов: {stat.kill_mobs}   ")
        win.addstr(4, 37, "║")
        win.addstr(5, 2, f"║ Покушол:   {stat.skushol}")
        win.addstr(5, 19, f"│ Выпил:      {stat.vipil}   ")
        win.addstr(5, 37, "║")
        win.addstr(6, 2, f"║ Прочитал:  {stat.prochital}")
        win.addstr(6, 19, "│ ¯\\_(ツ)_/¯      ║")
        win.addstr(7, 2, f"║ Впитал:    {stat.vpital}")
        win.addstr(7, 19, f"│ Втащил:     {stat.vtashil}   ")
        win.addstr(7, 37, "║")
        win.addstr(8, 1, " ╚════════════════╧═════════════════╝")
        
        win.addstr(10, 3, "ТОП:")
        for i in range(len(records)):
            win.addstr(11 + i, 4, f"{i+1} - Голда: {records[i]['treasure']}, LVL: {records[i]['lvl']}, Снёс: {records[i]['kill_mobs']}")
