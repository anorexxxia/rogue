import os
from domain.enemy import Enemy
from domain.item import Item
from domain.stat import Stat
import json
from domain.generate_lvl import GenerateLvl
from domain.backpack import Backpack
from domain.character import Character
from domain.room import Room


class DataLayer:
    def __init__(self):
        self.data_path = "data"
        self.attempts_path = "data/attempts.json"
        self.session_path = "data/session.json"
        self.session_set = False
        self.configure_directory()
        self.scores = self.records()
        self.stat = None
        self.backpack = None
        self.player = None
        self.rooms = None
        self.items = None
        self.enemy = None
        self.lvl = None
        self.chance_spawn_enemy = None
        self.chance_spawn_item = None
        self.corridors = None
        self.exit_y = None
        self.exit_x = None

#=========================================== BASIC_PART =================================================

    def make_data_dir(self):
        try:
            os.mkdir(self.data_path)
        except FileExistsError:
            pass
        except Exception as e:
            print(f"Ошибка создания родительской директории: {e}")
            raise Exception

    def configure_directory(self):
        try:
            self.make_data_dir()
            self.make_json_attempts()
        except Exception as e:
            raise Exception(f"Ошибка {e} ")

    @staticmethod
    def path_exists(path):
        return os.path.exists(path)

#====================================================================================================


#========================================== ATTEMPT_PART ============================================

    def make_json_attempts(self):
        if not self.path_exists(self.attempts_path):
            with open(self.attempts_path, "w") as f:
                json.dump([], f, indent = 4)

    def records(self):
        if self.path_exists(self.data_path):
            with open(self.attempts_path, "r") as f:
                return json.load(f)[:7]

    def attempt_to_json(self, player_info):
        if self.path_exists(self.attempts_path):
            result = {
                "treasure" : player_info.treasure,
                "lvl": player_info.lvl, 
                "steps" : player_info.steps,
                "kill_mobs": player_info.kill_mobs,
                "skushol": player_info.skushol,
                "vipil": player_info.vipil,
                "prochital" : player_info.prochital,
                "vpital" : player_info.vpital,
                "vtashil" : player_info.vtashil
            }

        if self.path_exists(self.data_path):
            with open(self.attempts_path, "r") as f:
                scores = json.load(f)
                scores.append(result)
                scores.sort(key=lambda x: x["treasure"], reverse=True)
                self.scores = scores[:7]

            with open(self.attempts_path, "w") as f:
                json.dump(scores, f, indent = 4)

#==================================================================================================== 

#==================================== SESSION_MISC_PART =============================================
            
    def make_session(self):
        try:
            if not self.path_exists(self.session_path):
                with open(self.session_path, 'w'):
                    self.session_set = True
            else:
                self.session_set = True
        except Exception as e:
            print(f"Ошибка создания сессии: {e}")
            raise Exception

    def remove_session(self):
        if self.path_exists(self.session_path):
            os.remove(self.session_path)
            self.session_set = False
            return True
        return False

#==================================================================================================== 

#==================================== SESSION_TO_JSON_PART ==========================================

    def session_to_json(self, player: Character, lvl: GenerateLvl):
        if self.session_set:
            lvl_dict = self.lvl_to_json(player, lvl)
            with open(self.session_path, 'w') as f:
                json.dump(lvl_dict, f, indent=2)
        else:
            return False

    def lvl_to_json(self, player: Character, lvl: GenerateLvl):
        result_dict = {}

        for key, value in lvl.__dict__.items():
            if key == 'map_grid':
                continue
            if key == 'enemy' or key == 'items' or key == 'rooms':
                result_dict[key] = self.entities_to_json(value)
            elif key == 'player':
                result_dict[key] = self.player_to_json(player, lvl.player.x, lvl.player.y)
            else:
                result_dict[key] = value

        return result_dict

    def player_to_json(self, player: Character, player_x, player_y):
        result_dict = {}

        for key, value in player.__dict__.items():
            if key == 'backpack':
                result_dict[key] = self.backpack_to_json(player.backpack)
            elif key == 'stat':
                result_dict[key] = player.stat.__dict__
            elif key == 'x':
                result_dict[key] = player_x
            elif key == 'y':
                result_dict[key] = player_y
            elif key == 'current_weapon':
                result_dict[key] = value.__dict__ if value is not None else None
            else:
                result_dict[key] = value

        return result_dict

    def backpack_to_json(self, backp: Backpack):
        result_dict = {'max_count': 9}
        back_items = {'сокровища': backp.backpack['сокровища']}

        for key, value in backp.backpack.items():
            if key == 'сокровища':
                continue
            for item in value:
                back_items.setdefault(key, [])
                back_items[key].append(item.__dict__ if item is not None else None)
                
        result_dict['backpack'] = back_items
        return result_dict
            
    def entities_to_json(self, entities_list: list):
        return [entity.__dict__ for entity in entities_list]

#====================================================================================================

#==================================== JSON_TO_SESSION_PART ==========================================

    def json_to_session(self):
        with open(self.session_path, 'r') as f:
            save = json.load(f)
            self.backpack = save['player']['backpack']['backpack']
            self.stat = save['player']['stat']
            self.player = save['player']
            self.rooms = save['rooms']
            self.items = save['items']
            self.enemy = save['enemy']
            self.lvl = save['lvl']
            self.chance_spawn_enemy = save['chance_spawn_enemy']
            self.chance_spawn_item = save['chance_spawn_item']
            self.corridors = save['corridors']
            self.exit_y = save['exit_y']
            self.exit_x = save['exit_x']


    def json_to_lvl(self, player):
        items = self.json_to_items()
        enemy = self.json_to_enemy()
        rooms = self.json_to_rooms()
        pl = player
        pl_y = pl.y
        pl_x = pl.x
        lvl = GenerateLvl(pl)
        pl.y = pl_y
        pl.x = pl_x
        lvl.lvl = self.lvl
        lvl.chance_spawn_enemy = self.chance_spawn_enemy
        lvl.chance_spawn_item = self.chance_spawn_item
        lvl.items = items
        lvl.enemy = enemy
        lvl.rooms = rooms
        lvl.corridors = self.corridors
        lvl.map_grid = lvl.create_map_grid()

        for it in items:
            lvl.update_entity_position(it, it.y, it.x)
        lvl.map_grid[self.exit_y][self.exit_x] = '∏'

        return lvl

    def json_to_enemy(self):
        enemy_json = self.enemy
        enemy = []

        for en in enemy_json:
            enemy_iter = Enemy()
            enemy_iter.__dict__ = en
            enemy.append(enemy_iter)

        return enemy


    def json_to_items(self):
        items_json = self.items
        items = []

        for item in items_json:
            it = Item()
            it.__dict__ = item
            items.append(it)
        
        return items

    def json_to_rooms(self):
        rooms_json = self.rooms
        rooms = []

        for room in rooms_json:
            r = Room(lvl_y=room['lvl_y'], lvl_x=room['lvl_x'], y=room['y'], x=room['x'])
            r.start_room = room['start_room']
            r.exit_room = room['exit_room']
            rooms.append(r)

        return rooms   


    def json_to_player(self):
        back = self.json_to_backpack()
        st = self.json_to_stat()
        player = self.player
        pl = Character()

        for key in pl.__dict__:
            pl.__dict__[key] = player[key]

        pl.backpack = back
        pl.stat = st
        pl.current_weapon = back.backpack['оружие'][0]

        return pl


    def json_to_stat(self):
        stat = self.stat
        st = Stat()
        
        for key in st.__dict__:
            st.__dict__[key] = stat[key]

        return st


    def json_to_backpack(self):
        back = self.backpack
        backpack = Backpack()

        for key, values in back.items():
            lst = []
            if key == 'сокровища':
                backpack.backpack['сокровища'] = values
                continue

            elif type(values) is list:
                for item in values:
                    if item is not None:
                        it = Item()
                        it.__dict__ = dict()
                        it.__dict__ = item
                        lst.append(it)
                    elif item is None:
                        lst.append(None)

            backpack.backpack[key] = lst

        return backpack

#====================================================================================================