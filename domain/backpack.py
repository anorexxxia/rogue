
class Backpack:
    def __init__(self):
        self.max_count = 9
        self.backpack = {'еда': [], 'фляги': [], 'свитки': [], 'оружие': [None], 'сокровища': 0}

    def add_item(self, item, player):
        if len(self.backpack[item.type]) < self.max_count:
            if item.type == 'оружие' and player.current_weapon is None and self.backpack['оружие'][0] == None:
                player.current_weapon = item
                self.backpack['оружие'][0] = item
                self.backpack['оружие'].append(None)
            else:
                self.backpack[item.type].append(item)
            return True  # Предмет успешно добавлен
        return False  # Рюкзак полон для данного типа предметов

    def use_item_from_backpack(self, item_type, indx): # удаление предмета из рюкзака
        used_item = self.backpack[item_type].pop(indx-1)
        return used_item

    def handle_weapons_logic(self, digit, backpack, current_panel, player, stat_bar):

        if backpack[current_panel][0] == None and digit != 0:
            backpack[current_panel][0] = backpack[current_panel][digit]
            player.current_weapon = backpack[current_panel][digit]
            backpack[current_panel].pop(digit)
            backpack[current_panel].append(None)

        elif digit == 0 and backpack[current_panel][0] != None:
            tmp = backpack[current_panel][0]
            backpack[current_panel].remove(None)
            backpack[current_panel][0] = None
            player.current_weapon = None 
            backpack[current_panel].append(tmp)
               
        elif digit == 0 and backpack[current_panel][0] == None:  
            pass
        
        else:
            tmp = backpack[current_panel][0]
            backpack[current_panel][0] = backpack[current_panel][digit]
            player.current_weapon = backpack[current_panel][digit] 
            backpack[current_panel][digit] = tmp 