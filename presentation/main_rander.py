import curses
from .renderer import GameRenderer
from domain.generate_lvl import GenerateLvl
from domain.movement import Movement
from domain.character import Character
from datalayer.savejson import DataLayer
from random import randint

COLOR_WALL = randint(10, 240) # Константа для рандомных цветов стен

def game_loop(stdscr): 
    curses.curs_set(0)  # Скрываем курсор
    stdscr.border(0)  # Рисуем рамку вокруг окна
    dt = DataLayer() # Сейвы

    start_menu = curses.newwin(44, 124, 1, 1) # Стартовое меню
    start_menu.border(0)

    start_menu.addstr(20, 50, "1) Новая игра")
    if dt.path_exists(dt.session_path):
        start_menu.addstr(22, 50, "2) Загрузить игру")
        dt.session_set = True
        start_menu.addstr(24, 50, "q) Выйти")
    else:
        start_menu.addstr(22, 50, "q) Выйти")

    start_menu.refresh()

    player = Character()  # Создаем персонажа
    lvl = GenerateLvl(player)  # Генерируем уровень с персонажем

    while True: 
        start_key = start_menu.getch()
        if start_key == ord('1'): # new game
            dt.remove_session() 
            break 
        elif start_key == ord('2') and dt.session_set: # resume
            dt.json_to_session()
            player = dt.json_to_player()
            lvl = dt.json_to_lvl(player)
            break
        elif start_key == ord('q'): # quit
            return
    
    lvl_window = curses.newwin(44, 124, 1, 1)  # Создаем новое окно для уровня
    status = curses.newwin(3, 120, 46, 1) # Окно статуса персонажа
    stat_bar = curses.newwin(20, 40, 1, 125) # Окно статистики персонажа
    info_bar = curses.newwin(20, 40, 22, 125) # Окно побочной информации
    
    stat_bar.border(0)
    info_bar.border(0)

    movement = Movement()  # ← domain: создаём логику движения персонажа

    renderer = GameRenderer(lvl_window)  # Инициализируем рендерер с новым окном
    renderer_stat = GameRenderer(stat_bar)  # Инициализируем рендерер для статистики персонажа
    renderer_status = GameRenderer(status) # Инициализация окна со статусом персонажа
    renderer_info_bar = GameRenderer(info_bar) # Инициализация окна с побочной информацией
    renderer.create_backpack_panels(player.backpack) # Рендер панелей инвентаря
    renderer.create_score_panel() # Рендер статистики
    current_panel = None # Текущая панель инвентаря
    depth = lvl.lvl # Глубина уровня

    curses.start_color()                                        #  |
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) #  } Цвета    
    curses.init_pair(2, COLOR_WALL, curses.COLOR_BLACK)         #  |
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)#  |

    start_window = True # Флаг начального окна

    renderer_stat.stat_bar(lvl, player) # Начальные рендеры
    renderer_info_bar.info_bar()
    renderer_status.status(lvl, player, movement)
    
    stdscr.refresh()
    lvl_window.refresh()
    status.refresh()
    stat_bar.refresh()
    info_bar.refresh()

    while True:
        if depth != lvl.lvl:
            lvl_window.erase()
            depth = lvl.lvl

        renderer.render_lvl(lvl, player)  # Отрисовываем уровень
        renderer.render_entity(player) # Отрисовываем Страдальца

        curses.panel.update_panels()
        stdscr.refresh()

        key = lvl_window.getch()  # Получаем нажатую клавишу
        if key == ord('q'):  # Если нажата 'q', выходим из игры и сохраняем результат
            dt.attempt_to_json(player.stat)
            break
        
        if start_window: 
            start_window = False
            stdscr.addstr(10, 10, ' ' * 100)

        if current_panel and current_panel != 'статистика': 
            if current_panel == 'оружие':
                current_panel = renderer.handle_weapon_panel(current_panel, player.backpack, key, stat_bar, player)
            else:
                current_panel = renderer.handle_opened_panel(current_panel, player.backpack, key, stat_bar, stdscr, player)
            stdscr.refresh()
            continue
        
        current_panel = renderer.handle_key(key, player.backpack, stat_bar, stdscr, player.stat, dt.scores)
        if current_panel:
            continue
        
        player_muv = movement.character_movement(player, lvl, key, dt)  # Обрабатываем движение персонажа

        if player_muv == "YOU DIED":
            stdscr.clear()
            stdscr.box()
            stdscr.refresh()
            renderer.death_or_win(status='died')
            dt.attempt_to_json(player.stat)
            dt.remove_session()
            break

        if isinstance(player_muv, GenerateLvl):  # Если игрок перешел на следующий уровень
            lvl = player_muv  # Обновляем уровень на новый
            if lvl.lvl == 22:  # Если достигнут 22 уровень, выводим сообщение о победе
                renderer.death_or_win(status='win')
                dt.attempt_to_json(player.stat)
                break

        renderer_stat.stat_bar(lvl, player)
        renderer_info_bar.info_bar()
        renderer_status.status(lvl, player, movement)
