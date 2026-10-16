import random

def attack_enemy(enemy, player):
    hit_chance = enemy.agility / (enemy.agility + player.agility)

    if random.random() < hit_chance:
        player.stat.vpital += 1

        match enemy.type:
            case 'Вампир':
                damage = vampire_damage_calculation(enemy, player)
            case 'Огр':
                damage = ogre_damage_calculation(enemy, player)
            case 'Змей-маг':
                damage = snake_magic_calculation(enemy, player)
            case _:
                damage = enemy.strength
                player.take_damage(damage)

        if type(damage) is int:
            return f"{enemy.type} нанёс {damage} урона!"
        else:
            return damage
    else:
        return f"{enemy.type} не попал по вам."
    

def player_attack(player, enemy):
    hit_chance = player.agility / (player.agility + enemy.agility)

    if random.random() < hit_chance:
        player.stat.vtashil += 1
        
        if enemy.type == 'Вампир' and enemy.first_hit:
            enemy.first_hit = False  # Сбрасываем флаг после первого удара
            return "Вы нанесли первый удар по вампиру, но он 100% увернулся, лакер"
        
        if player.current_weapon is not None:
            damage = player.strength + player.current_weapon.damage
        else:
            damage = player.strength

        enemy.take_damage(damage)

        return f"Вы нанесли {damage} урона!"
    else:
        return "Вы промахнулись!"
    
def vampire_damage_calculation(enemy, player):
    vampirism = int(player.max_health * random.uniform(0.01, 0.05))  # Вампир наносит 1-5% от максимального здоровья цели
    player.max_health -= vampirism  # Уменьшаем максимальное здоровье цели
    damage = enemy.strength
    player.take_damage(damage) # Наносим основной урон
    return vampirism + damage  # Возвращаем общее количество здоровья, которое вампир "высасывает"

def ogre_damage_calculation(enemy, player):
    if enemy.sleep_one_step:
        enemy.sleep_one_step = False  # Огр пропускает ход после атаки
        return "Огр спит 1 ход и не наносит урона!       "  # Огр не наносит урон в этот ход
    else:        
        enemy.sleep_one_step = True  # Огр будет спать в следующий ход
        damage = enemy.strength
        player.take_damage(damage)  
    return damage

def snake_magic_calculation(enemy, player):
    # Змей-маг наносит урон и может наложить эффект
    damage = enemy.strength
    player.take_damage(damage)

    if random.random() < 0.3:  # 30% шанс наложить эффект
        player.skip_move = True  # Герой пропускает следующий ход
        return f"Змей-маг нанес {damage} урона и наложил паралич! Вы пропустите следующий ход!"
    else:
        return damage