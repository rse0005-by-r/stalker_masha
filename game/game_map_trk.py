import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import random
import time
import json
import pickle

# Символьная карта с emoji
map_data = None  # Динамически загружаемая карта
player_position = None  # Координаты игрока (player_x, player_y)
original_artifacts = []  # Позиции оригинальных артефактов (скрытых)
compass_active = False  # Флаг активности компаса
compass_end_time = 0  # Время окончания действия компаса
visible_artifacts = []  # Артефакты, которые сейчас видны
compass_duration = 0  # Длительность текущего компаса
compass_level = 0  # Уровень текущего компаса

# Переменные для прокрутки
view_offset_x = 0  # Смещение по X для отображения
view_offset_y = 0  # Смещение по Y для отображения
view_width = 25    # Количество клеток по ширине для отображения
view_height = 15   # Количество клеток по высоте для отображения

# Система квестов
quests = {
    "masha_quest": {
        "name": "Первый артефакт для Маши",
        "description": "Маша просит найти артефакт Артемида (1 уровень) для её исследований. Она заплатит в 3 раза больше рыночной цены!",
        "npc": "Маша",
        "required_item": "🍄",
        "base_price": 100,  # Базовая цена артефакта
        "reward_multiplier": 3,  # Множитель награды
        "reward": 300,  # 100 * 3 = 300
        "completed": False,
        "active": False,
        "started": False,
        "can_take_again": False,  # Можно ли взять квест повторно
        "unique_quest": True  # Уникальный квест, можно взять только 1 раз
    }
}

# NPC персонажи
npcs = {
    "👩": {
        "name": "Маша",
        "type": "quest_giver",
        "quest": "masha_quest",
        "dialogue": {
            "greeting": "Привет, сталкер! Я Маша, исследователь аномалий.",
            "quest_offer": "Мне срочно нужен артефакт Артемида для важного исследования! Принеси его мне, и я заплачу в 3 раза больше рыночной цены - целых $300!",
            "quest_active": "Ты уже взял мой квест. Найди артефакт Артемида (🍄) и принеси мне! Помни, я плачу $300 вместо обычных $100!",
            "quest_completed": "Спасибо! Этот артефакт очень важен для моих исследований. Вот твоя награда - $300, как и обещала!",
            "quest_already_completed": "Спасибо за помощь! Ты уже выполнил мой квест. Удачи в дальнейших поисках!",
            "no_quest": "Если найдешь интересные артефакты - обращайся! Но больше я не покупаю Артемиду по повышенной цене."
        }
    }
}

# Игровые сущности и описания
ENTITY_TYPES = {
    "☢": "Радиационное облако",
    "⚡": "Электрическая аномалия",
    "•": "Невидимая область",
    "🌳": "Лес",
    "🌧": "Дождевое облако",
    "🏗": "Торговая база",
    "🧘‍♂️": "Спящий сталкер",
    "🦸": "Охотник (мутант)",
    "🧟": "Зомбированный сталкер",
    "💀": "Мертвая зона",
    "🏭": "Энергоблок",
    "🚧": "Завал",
    "💧": "Водоем",
    "🔥": "Пожар",
    "⚓": "Якорь (безопасная зона)",
    "🍄": "Артефакт Артемида (1 уровень)",
    "🔮": "Артефакт Хрустальный шар (2 уровень)",
    "💎": "Артефакт Огненный шар (3 уровень)",
    "🌟": "Артефакт Звездная пыль (4 уровень)",
    "✨": "Артефакт Эфир (5 уровень)",
    "☄️": "Артефакт Комета (легендарный)",
    "👩": "Исследователь Маша (NPC)",
    ".": "Пустая местность"
}

# Опасность объектов и ущерб здоровью
entity_damage = {
    "☢": 15, "⚡": 8, "•": 0, "🌳": 0, "🌧": 3, "🏗": 0,
    "🧘‍♂️": 0, "🦸": 20, "🧟": 10, "💀": 25, "🏭": 5,
    "🚧": 2, "💧": 1, "🔥": 12, "⚓": 0, "🍄": 0, "🔮": 0,
    "💎": 0, "🌟": 0, "✨": 0, "☄️": 5, "👩": 0, ".": 0
}

# Цены на ВСЕ предметы
item_prices = {
    # Артефакты
    "🍄": 100, "🔮": 250, "💎": 500, "🌟": 1000, "✨": 2000, "☄️": 5000,
    
    # Компасы
    "Компас I уровня": 50, "Компас II уровня": 100,
    "Компас III уровня": 200, "Компас IV уровня": 400,
    
    # Медицина
    "Антирэд": 30, "Медпрепарат": 40, "Бинт": 10, "Аптечка": 100,
    
    # Еда и ресурсы
    "Консервы": 20, "Вода": 15, "Радиоактивное мясо": 60, "Тушенка": 25,
    
    # Оружие и броня
    "Пистолет": 200, "Обрез": 150, "АК-74": 500, "Бронежилет": 300, "Шлем": 100,
    
    # Разное
    "Фонарик": 50, "Рация": 120, "Карта Зоны": 80, "Дозиметр": 70
}

# Горячие клавиши
hotkeys = {
    'move_up': 'w', 'move_down': 's', 'move_left': 'a', 'move_right': 'd',
    'interaction': 'e', 'change_zoom_in': '+', 'change_zoom_out': '-',
    'save_game': 'F5', 'load_game': 'F9', 'quit_game': 'q',
    'open_settings': 'o', 'toggle_fullscreen': 'F11',
    'open_inventory': 'i', 'quick_sell': 'p',
    'scroll_up': 'up', 'scroll_down': 'down',
    'scroll_left': 'left', 'scroll_right': 'right',
    'quest_log': 'l',  # Новая: журнал квестов
    'find_masha': 'f'  # Найти Машу
}

# Игровые показатели
player_health = 100
player_level = 1
player_exp = 0
player_money = 150
player_inventory = []
quick_access_slots = [None]*9

# Специальные предметы
special_tools = [
    "Антирэд", "Медпрепарат", "Бинт", "Аптечка",
    "Компас I уровня", "Компас II уровня", 
    "Компас III уровня", "Компас IV уровня",
    "Фонарик", "Рация", "Карта Зоны", "Дозиметр"
]

# Каталог для сохранений
SAVE_DIR = 'saves'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Размеры клеточек
CELL_SIZE = 40

# ========== ФУНКЦИИ СОЗДАНИЯ КАРТЫ ==========

def create_very_small_map_with_npc():
    """Создает ОЧЕНЬ маленькую карту для быстрого поиска"""
    width, height = 30, 20  # Очень маленькая карта!
    map_grid = [["." for _ in range(width)] for _ in range(height)]  # Точки для пустых клеток
    
    # Явные границы карты
    for x in range(width):
        map_grid[0][x] = "🚧"  # Верхняя граница
        map_grid[height-1][x] = "🚧"  # Нижняя граница
    for y in range(height):
        map_grid[y][0] = "🚧"  # Левая граница
        map_grid[y][width-1] = "🚧"  # Правая граница
    
    # Стартовая позиция игрока - в центре
    start_x, start_y = 5, 10
    map_grid[start_y][start_x] = "⚓"
    
    # Маша - прямо рядом!
    masha_x, masha_y = 10, 10
    map_grid[masha_y][masha_x] = "👩"
    
    # Торговая база - недалеко
    trade_x, trade_y = 20, 10
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            nx, ny = trade_x + dx, trade_y + dy
            if 0 <= nx < width and 0 <= ny < height:
                map_grid[ny][nx] = "🏗"
    
    # Несколько деревьев для атмосферы
    trees = [(7, 8), (8, 9), (12, 11), (15, 9), (18, 12)]
    for x, y in trees:
        if 0 <= x < width and 0 <= y < height:
            map_grid[y][x] = "🌳"
    
    # Несколько артефактов (один из них нужный для квеста)
    map_grid[8][15] = "🍄"  # Артемида для квеста Маши!
    map_grid[12][18] = "🔮"  # Хрустальный шар
    map_grid[5][22] = "💎"  # Огненный шар
    
    # Несколько опасных зон (немного, чтобы не мешали)
    map_grid[3][12] = "☢"
    map_grid[15][7] = "⚡"
    map_grid[17][15] = "💀"
    
    # Несколько других объектов для разнообразия
    map_grid[14][5] = "🏭"
    map_grid[6][20] = "💧"
    map_grid[12][8] = "🧘‍♂️"
    
    # Создаем дорожку от старта к Маше для удобства
    # Простая прямая линия
    for i in range(6):
        x = start_x + i
        y = start_y
        if 0 <= x < width and 0 <= y < height and map_grid[y][x] == ".":
            map_grid[y][x] = "•"
    
    for i in range(4):
        x = 10
        y = start_y - i
        if 0 <= x < width and 0 <= y < height and map_grid[y][x] == ".":
            map_grid[y][x] = "•"
    
    return map_grid

# ========== СИСТЕМА КВЕСТОВ ==========

def update_quest_progress():
    """Обновляет прогресс выполнения квестов"""
    global quests, player_inventory, player_money
    
    # Проверяем квест Маши
    if quests["masha_quest"]["active"] and not quests["masha_quest"]["completed"]:
        if "🍄" in player_inventory:
            # Игрок нашел нужный артефакт
            complete_quest("masha_quest")

def start_quest(quest_id):
    """Начинает квест"""
    if quest_id in quests:
        quest = quests[quest_id]
        
        # Проверяем, можно ли взять квест повторно
        if quest.get("unique_quest", False) and quest["completed"]:
            messagebox.showwarning("Квест уже выполнен", 
                                 f"Вы уже выполнили квест '{quest['name']}'!\n"
                                 f"Это уникальный квест, который нельзя взять повторно.")
            return False
        
        if not quest["started"]:
            quest["active"] = True
            quest["started"] = True
            
            # Показываем специальное сообщение для квеста Маши
            if quest_id == "masha_quest":
                messagebox.showinfo("УНИКАЛЬНЫЙ КВЕСТ!", 
                                  f"⚠️ ВНИМАНИЕ: Уникальный квест!\n\n"
                                  f"Квест принят: {quest['name']}\n\n"
                                  f"{quest['description']}\n\n"
                                  f"Особые условия:\n"
                                  f"• Награда: ${quest['reward']} (вместо ${quest['base_price']})\n"
                                  f"• Можно выполнить ТОЛЬКО 1 раз за всю игру!\n"
                                  f"• После сдачи артефакта квест больше не будет доступен")
            else:
                messagebox.showinfo("Новый квест!", 
                                  f"Квест принят: {quest['name']}\n\n"
                                  f"{quest['description']}\n\n"
                                  f"Награда: ${quest['reward']}")
            
            update_display()
            return True
    return False

def complete_quest(quest_id):
    """Завершает квест и выдает награду"""
    global player_money, player_inventory, quests
    
    if quest_id in quests:
        quest = quests[quest_id]
        
        # Проверяем, выполнен ли уже квест
        if quest["completed"]:
            messagebox.showinfo("Квест уже выполнен", 
                              f"Вы уже выполнили этот квест ранее!")
            return False
        
        if quest["active"] and not quest["completed"]:
            # Проверяем, есть ли нужный предмет
            if quest["required_item"] in player_inventory:
                # Удаляем предмет из инвентаря
                player_inventory.remove(quest["required_item"])
                
                # Выдаем награду
                reward = quest["reward"]
                player_money += reward
                
                # Отмечаем квест как выполненный
                quest["completed"] = True
                quest["active"] = False
                
                # Для уникальных квестов - помечаем как невозможные для повторного взятия
                if quest.get("unique_quest", False):
                    quest["can_take_again"] = False
                
                # Получаем информацию о NPC
                npc_name = quest["npc"]
                npc_info = None
                for npc_emoji, npc_data in npcs.items():
                    if npc_data["name"] == npc_name:
                        npc_info = npc_data
                        break
                
                # Показываем сообщение о завершении
                if npc_info:
                    messagebox.showinfo("Квест выполнен!", 
                                      f"{npc_info['dialogue']['quest_completed']}\n\n"
                                      f"Получено: ${reward}\n"
                                      f"Текущий баланс: ${player_money}")
                else:
                    messagebox.showinfo("Квест выполнен!", 
                                      f"Квест '{quest['name']}' завершен!\n\n"
                                      f"Получено: ${reward}\n"
                                      f"Текущий баланс: ${player_money}")
                
                # Даем небольшой опыт за выполнение квеста
                global player_exp
                player_exp += 50
                check_level_up()
                
                update_display()
                return True
    
    return False

def show_quest_log():
    """Показывает журнал квестов"""
    quest_window = tk.Toplevel(root)
    quest_window.title("Журнал квестов")
    quest_window.geometry("500x400")
    quest_window.configure(bg="#2C2C2C")
    
    # Заголовок
    title_label = tk.Label(quest_window, text="ЖУРНАЛ КВЕСТОВ", 
                          font=("Arial", 16, "bold"), 
                          bg="#2C2C2C", fg="white")
    title_label.pack(pady=10)
    
    # Фрейм для квестов с прокруткой
    quests_frame = tk.Frame(quest_window, bg="#2C2C2C")
    quests_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Canvas и Scrollbar для прокрутки
    canvas = tk.Canvas(quests_frame, bg="#2C2C2C", highlightthickness=0)
    scrollbar = tk.Scrollbar(quests_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#2C2C2C")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Отображаем квесты
    active_quests = 0
    completed_quests = 0
    
    for quest_id, quest in quests.items():
        quest_frame = tk.Frame(scrollable_frame, bg="#3C3C3C", relief="raised", bd=2)
        quest_frame.pack(fill="x", pady=5, padx=5)
        
        # Статус квеста
        status_text = ""
        status_color = ""
        
        if quest["completed"]:
            status_text = "✅ ВЫПОЛНЕН"
            status_color = "#4CAF50"
            completed_quests += 1
        elif quest["active"]:
            status_text = "🎯 АКТИВЕН"
            status_color = "#FF9800"
            active_quests += 1
        else:
            status_text = "⏳ НЕ НАЧАТ"
            status_color = "#9E9E9E"
        
        # Заголовок квеста
        header_frame = tk.Frame(quest_frame, bg="#3C3C3C")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(header_frame, text=quest["name"], 
                font=("TkDefaultFont", 12, "bold"),
                bg="#3C3C3C", fg="white").pack(side="left")
        
        # Иконка уникальности для уникальных квестов
        if quest.get("unique_quest", False):
            tk.Label(header_frame, text="⭐ УНИКАЛЬНЫЙ",
                    font=("TkDefaultFont", 8, "bold"),
                    bg="#3C3C3C", fg="#FFD700").pack(side="left", padx=5)
        
        tk.Label(header_frame, text=status_text,
                font=("TkDefaultFont", 10, "bold"),
                bg="#3C3C3C", fg=status_color).pack(side="right")
        
        # Описание квеста
        desc_frame = tk.Frame(quest_frame, bg="#3C3C3C")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(desc_frame, text=quest["description"],
                font=("TkDefaultFont", 9),
                bg="#3C3C3C", fg="#CCCCCC", wraplength=400,
                justify="left").pack(anchor="w")
        
        # Детали квеста
        details_frame = tk.Frame(quest_frame, bg="#3C3C3C")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        if quest["active"] and not quest["completed"]:
            # Требуемый предмет
            item_emoji = quest["required_item"]
            item_name = ENTITY_TYPES.get(item_emoji, "Неизвестный предмет")
            
            tk.Label(details_frame, text=f"Нужно найти: {item_emoji} {item_name}",
                    font=("TkDefaultFont", 9),
                    bg="#3C3C3C", fg="#FFD700").pack(anchor="w")
            
            # Проверка наличия предмета
            if quest["required_item"] in player_inventory:
                tk.Label(details_frame, text="✅ Предмет есть в инвентаре!",
                        font=("TkDefaultFont", 9, "bold"),
                        bg="#3C3C3C", fg="#4CAF50").pack(anchor="w")
        
        # Награда (особо выделяем для уникальных квестов)
        reward_frame = tk.Frame(quest_frame, bg="#3C3C3C")
        reward_frame.pack(fill="x", padx=10, pady=5)
        
        if quest.get("unique_quest", False) and "base_price" in quest:
            reward_text = f"Награда: ${quest['reward']} (обычная цена: ${quest['base_price']})"
            reward_color = "#FFD700"  # Золотой для уникальных наград
        else:
            reward_text = f"Награда: ${quest['reward']}"
            reward_color = "#4CAF50"
        
        tk.Label(reward_frame, text=reward_text,
                font=("TkDefaultFont", 9, "bold"),
                bg="#3C3C3C", fg=reward_color).pack(anchor="w")
        
        # NPC, выдавший квест
        npc_frame = tk.Frame(quest_frame, bg="#3C3C3C")
        npc_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        tk.Label(npc_frame, text=f"От: {quest['npc']}",
                font=("TkDefaultFont", 8),
                bg="#3C3C3C", fg="#AAAAAA").pack(anchor="w")
        
        # Информация о повторах для уникальных квестов
        if quest.get("unique_quest", False):
            unique_frame = tk.Frame(quest_frame, bg="#3C3C3C")
            unique_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            if quest["completed"]:
                unique_text = "❌ Этот уникальный квест больше недоступен"
                unique_color = "#FF5555"
            else:
                unique_text = "⚠️ Можно выполнить только 1 раз!"
                unique_color = "#FF9800"
            
            tk.Label(unique_frame, text=unique_text,
                    font=("TkDefaultFont", 8, "italic"),
                    bg="#3C3C3C", fg=unique_color).pack(anchor="w")
    
    # Статистика квестов
    stats_frame = tk.Frame(quest_window, bg="#2C2C2C")
    stats_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Label(stats_frame, 
            text=f"Активные: {active_quests} | Выполненные: {completed_quests} | Всего: {len(quests)}",
            font=("TkDefaultFont", 10),
            bg="#2C2C2C", fg="#CCCCCC").pack()
    
    # Кнопка закрытия
    tk.Button(quest_window, text="Закрыть", command=quest_window.destroy,
             bg="#F44336", fg="white", font=("TkDefaultFont", 10)).pack(pady=10)

def interact_with_npc(npc_emoji):
    """Взаимодействие с NPC"""
    if npc_emoji in npcs:
        npc = npcs[npc_emoji]
        
        # Создаем окно диалога
        dialog_window = tk.Toplevel(root)
        dialog_window.title(f"Диалог с {npc['name']}")
        dialog_window.geometry("500x400")
        dialog_window.configure(bg="#2C2C2C")
        
        # Заголовок
        title_frame = tk.Frame(dialog_window, bg="#2C2C2C")
        title_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(title_frame, text=npc_emoji, 
                font=("TkDefaultFont", 24),
                bg="#2C2C2C", fg="white").pack(side="left", padx=10)
        
        tk.Label(title_frame, text=npc["name"], 
                font=("Arial", 16, "bold"),
                bg="#2C2C2C", fg="white").pack(side="left")
        
        # Область диалога
        dialog_frame = tk.Frame(dialog_window, bg="#3C3C3C", relief="sunken", bd=2)
        dialog_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        dialog_text = tk.Text(dialog_frame, height=10, width=50,
                            bg="#3C3C3C", fg="white",
                            font=("TkDefaultFont", 10),
                            wrap="word", state="disabled")
        dialog_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Кнопки действий
        buttons_frame = tk.Frame(dialog_window, bg="#2C2C2C")
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        def add_dialog(text):
            dialog_text.config(state="normal")
            dialog_text.insert("end", text + "\n\n")
            dialog_text.see("end")
            dialog_text.config(state="disabled")
        
        # Начинаем диалог
        add_dialog(f"{npc['name']}: {npc['dialogue']['greeting']}")
        
        # Проверяем квесты для этого NPC
        if "quest" in npc:
            quest_id = npc["quest"]
            quest = quests[quest_id]
            
            if quest["completed"]:
                # Квест уже выполнен
                add_dialog(f"{npc['name']}: {npc['dialogue']['quest_already_completed']}")
                
                # Кнопка закрытия
                tk.Button(buttons_frame, text="Закрыть", 
                         command=dialog_window.destroy,
                         bg="#F44336", fg="white",
                         font=("TkDefaultFont", 10)).pack()
                
            elif quest["active"]:
                # Квест активен
                add_dialog(f"{npc['name']}: {npc['dialogue']['quest_active']}")
                
                # Проверяем, есть ли нужный предмет
                if quest["required_item"] in player_inventory:
                    def complete_quest_action():
                        if complete_quest(quest_id):
                            add_dialog(f"{npc['name']}: {npc['dialogue']['quest_completed']}\n\n"
                                     f"Вы получили ${quest['reward']}!")
                            complete_button.config(state="disabled")
                    
                    # Кнопка завершения квеста
                    complete_button = tk.Button(buttons_frame, text="Сдать артефакт", 
                                              command=complete_quest_action,
                                              bg="#4CAF50", fg="white",
                                              font=("TkDefaultFont", 10, "bold"))
                    complete_button.pack(side="left", padx=5)
                
                # Кнопка закрытия
                tk.Button(buttons_frame, text="Закрыть", 
                         command=dialog_window.destroy,
                         bg="#F44336", fg="white",
                         font=("TkDefaultFont", 10)).pack(side="left", padx=5)
                
            else:
                # Квест еще не взят
                add_dialog(f"{npc['name']}: {npc['dialogue']['quest_offer']}")
                
                def accept_quest_action():
                    if start_quest(quest_id):
                        add_dialog(f"Вы: Хорошо, я помогу тебе!\n\n"
                                 f"{npc['name']}: Отлично! Жду артефакт Артемида (🍄).")
                        accept_button.config(state="disabled")
                        decline_button.config(state="disabled")
                
                # Кнопка принятия квеста
                accept_button = tk.Button(buttons_frame, text="Принять квест", 
                                        command=accept_quest_action,
                                        bg="#2196F3", fg="white",
                                        font=("TkDefaultFont", 10, "bold"))
                accept_button.pack(side="left", padx=5)
                
                # Кнопка отказа
                def decline_quest_action():
                    add_dialog(f"Вы: Извини, сейчас не могу.\n\n"
                             f"{npc['name']}: {npc['dialogue']['no_quest']}")
                    accept_button.config(state="disabled")
                    decline_button.config(state="disabled")
                
                decline_button = tk.Button(buttons_frame, text="Отказаться", 
                                         command=decline_quest_action,
                                         bg="#FF9800", fg="white",
                                         font=("TkDefaultFont", 10))
                decline_button.pack(side="left", padx=5)
                
                # Кнопка закрытия
                tk.Button(buttons_frame, text="Закрыть", 
                         command=dialog_window.destroy,
                         bg="#F44336", fg="white",
                         font=("TkDefaultFont", 10)).pack(side="left", padx=5)
        else:
            # У NPC нет квестов
            add_dialog(f"{npc['name']}: {npc['dialogue']['no_quest']}")
            
            # Кнопка закрытия
            tk.Button(buttons_frame, text="Закрыть", 
                     command=dialog_window.destroy,
                     bg="#F44336", fg="white",
                     font=("TkDefaultFont", 10)).pack()
        
        # Делаем окно модальным
        dialog_window.transient(root)
        dialog_window.grab_set()
        
        return True
    
    return False

# ========== ФУНКЦИИ ПОИСКА МАШИ ==========

def find_and_show_masha():
    """Находит и показывает позицию Маши"""
    if not map_data:
        return
    
    masha_pos = None
    for y in range(len(map_data)):
        for x in range(len(map_data[y])):
            if map_data[y][x] == "👩":
                masha_pos = (x, y)
                break
        if masha_pos:
            break
    
    if masha_pos:
        messagebox.showinfo("Позиция Маши", 
                          f"🎯 Маша найдена!\n\n"
                          f"Координаты: X={masha_pos[0]}, Y={masha_pos[1]}\n\n"
                          f"Совет: Используйте мини-карту (M) для навигации!")
        
        # Прокручиваем карту к Маше
        global view_offset_x, view_offset_y
        view_offset_x = max(0, min(masha_pos[0] - view_width // 2, len(map_data[0]) - view_width))
        view_offset_y = max(0, min(masha_pos[1] - view_height // 2, len(map_data) - view_height))
        update_display()
    else:
        messagebox.showwarning("Маша не найдена", 
                             "Маша не найдена на карте. Попробуйте начать новую игру.")

# ========== ФУНКЦИИ СОХРАНЕНИЯ ==========

def save_game(slot=1):
    """Сохраняет игру в указанный слот"""
    save_data = {
        'map_data': map_data,
        'player_position': player_position,
        'original_artifacts': original_artifacts,
        'player_health': player_health,
        'player_level': player_level,
        'player_exp': player_exp,
        'player_money': player_money,
        'player_inventory': player_inventory,
        'quick_access_slots': quick_access_slots,
        'compass_active': compass_active,
        'visible_artifacts': visible_artifacts,
        'quests': quests,  # Сохраняем квесты
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    save_path = os.path.join(SAVE_DIR, f'save_slot_{slot}.sav')
    
    try:
        with open(save_path, 'wb') as f:
            pickle.dump(save_data, f)
        messagebox.showinfo("Сохранение", f"Игра сохранена в слоте {slot}!")
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сохранить игру: {e}")
        return False

def load_game(slot=1):
    """Загружает игру из указанного слота"""
    global map_data, player_position, original_artifacts, player_health
    global player_level, player_exp, player_money, player_inventory
    global quick_access_slots, compass_active, visible_artifacts, quests
    
    save_path = os.path.join(SAVE_DIR, f'save_slot_{slot}.sav')
    
    if not os.path.exists(save_path):
        messagebox.showwarning("Ошибка", f"Сохранение в слоте {slot} не найдено!")
        return False
    
    try:
        with open(save_path, 'rb') as f:
            save_data = pickle.load(f)
        
        # Восстанавливаем состояние игры
        map_data = save_data['map_data']
        player_position = save_data['player_position']
        original_artifacts = save_data['original_artifacts']
        player_health = save_data['player_health']
        player_level = save_data['player_level']
        player_exp = save_data['player_exp']
        player_money = save_data['player_money']
        player_inventory = save_data['player_inventory']
        quick_access_slots = save_data['quick_access_slots']
        compass_active = save_data['compass_active']
        visible_artifacts = save_data['visible_artifacts']
        
        # Восстанавливаем квесты (если есть в сохранении)
        if 'quests' in save_data:
            quests = save_data['quests']
        
        # Центрируем камеру на игроке
        center_camera_on_player()
        
        # Обновляем отображение
        update_display()
        
        messagebox.showinfo("Загрузка", f"Игра загружена из слота {slot}!\nСохранено: {save_data.get('timestamp', 'Неизвестно')}")
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить игру: {e}")
        return False

def save_map_to_file():
    """Сохраняет текущую карту в файл"""
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        initialdir=SAVE_DIR,
        title="Сохранить карту как"
    )
    
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for row in map_data:
                    f.write(''.join(row) + '\n')
            messagebox.showinfo("Сохранение", f"Карта сохранена в:\n{file_path}")
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить карту: {e}")
            return False
    return False

def load_map_from_file():
    """Загружает карту из файла"""
    global map_data, player_position, original_artifacts
    
    file_path = filedialog.askopenfilename(
        filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
        initialdir=SAVE_DIR,
        title="Загрузить карту"
    )
    
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                loaded_map = [[char for char in line.strip()] for line in lines]
            
            if loaded_map:
                map_data = loaded_map
                # Ищем безопасную стартовую позицию
                for y in range(len(map_data)):
                    for x in range(len(map_data[y])):
                        if map_data[y][x] == '⚓':
                            player_position = (x, y)
                            break
                    if player_position:
                        break
                
                if not player_position:
                    player_position = (0, 0)
                
                # Скрываем артефакты на новой карте
                hide_artifacts()
                
                # Центрируем камеру на игроке
                center_camera_on_player()
                
                update_display()
                
                messagebox.showinfo("Загрузка", f"Карта загружена из:\n{file_path}")
                return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить карту: {e}")
    return False

def show_save_load_menu():
    """Показывает меню сохранения/загрузки"""
    save_menu = tk.Toplevel(root)
    save_menu.title("Сохранение/Загрузка")
    save_menu.geometry("300x400")
    save_menu.configure(bg="#2C2C2C")
    
    tk.Label(save_menu, text="Управление сохранениями", 
            font=("Arial", 14, "bold"), bg="#2C2C2C", fg="white").pack(pady=10)
    
    # Слоты сохранения
    for slot in range(1, 6):
        slot_frame = tk.Frame(save_menu, bg="#2C2C2C")
        slot_frame.pack(fill="x", padx=20, pady=5)
        
        slot_label = f"Слот {slot}"
        slot_file = os.path.join(SAVE_DIR, f"save_slot_{slot}.sav")
        
        if os.path.exists(slot_file):
            try:
                with open(slot_file, 'rb') as f:
                    save_data = pickle.load(f)
                    timestamp = save_data.get('timestamp', 'Неизвестно')
                    slot_label = f"Слот {slot}: {timestamp}"
            except:
                pass
        
        tk.Label(slot_frame, text=slot_label, bg="#2C2C2C", fg="#AAAAAA",
                font=("TkDefaultFont", 9)).pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(slot_frame, bg="#2C2C2C")
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="Сохранить", command=lambda s=slot: [save_game(s), save_menu.destroy()],
                 bg="#4CAF50", fg="white", font=("TkDefaultFont", 8)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Загрузить", command=lambda s=slot: [load_game(s), save_menu.destroy()],
                 bg="#2196F3", fg="white", font=("TkDefaultFont", 8)).pack(side=tk.LEFT, padx=2)
    
    tk.Label(save_menu, text="Управление картами", 
            font=("Arial", 12, "bold"), bg="#2C2C2C", fg="white").pack(pady=10)
    
    map_frame = tk.Frame(save_menu, bg="#2C2C2C")
    map_frame.pack(pady=10)
    
    tk.Button(map_frame, text="Сохранить карту", command=save_map_to_file,
             bg="#9C27B0", fg="white", font=("TkDefaultFont", 10)).pack(pady=5)
    
    tk.Button(map_frame, text="Загрузить карту", command=load_map_from_file,
             bg="#FF9800", fg="white", font=("TkDefaultFont", 10)).pack(pady=5)
    
    tk.Button(save_menu, text="Закрыть", command=save_menu.destroy,
             bg="#F44336", fg="white", font=("TkDefaultFont", 10)).pack(pady=20)

# ========== ФУНКЦИИ ПРОКРУТКИ ==========

def center_camera_on_player():
    """Центрирует камеру на игроке"""
    global view_offset_x, view_offset_y
    
    if map_data and player_position:
        px, py = player_position
        
        # Центрируем камеру так, чтобы игрок был в центре видимой области
        view_offset_x = max(0, min(px - view_width // 2, len(map_data[0]) - view_width))
        view_offset_y = max(0, min(py - view_height // 2, len(map_data) - view_height))

def scroll_camera(dx, dy):
    """Прокручивает камеру на указанное смещение"""
    global view_offset_x, view_offset_y
    
    if map_data:
        # Вычисляем новые координаты камеры
        new_offset_x = max(0, min(view_offset_x + dx, len(map_data[0]) - view_width))
        new_offset_y = max(0, min(view_offset_y + dy, len(map_data) - view_height))
        
        # Проверяем, изменилась ли позиция камеры
        if new_offset_x != view_offset_x or new_offset_y != view_offset_y:
            view_offset_x = new_offset_x
            view_offset_y = new_offset_y
            update_display()
            return True
    return False

def auto_scroll_to_player():
    """Автоматически прокручивает камеру к игроку, если он близко к краю"""
    if not map_data or not player_position:
        return False
    
    px, py = player_position
    
    # Определяем границы "буферной зоны" (25% от размеров видимой области)
    buffer_x = view_width // 4
    buffer_y = view_height // 4
    
    # Флаги для определения необходимости прокрутки
    need_scroll = False
    scroll_dx, scroll_dy = 0, 0
    
    # Проверяем левую границу
    if px - view_offset_x < buffer_x and view_offset_x > 0:
        scroll_dx = -1
        need_scroll = True
    
    # Проверяем правую границу
    elif px - view_offset_x > view_width - buffer_x and view_offset_x < len(map_data[0]) - view_width:
        scroll_dx = 1
        need_scroll = True
    
    # Проверяем верхнюю границу
    if py - view_offset_y < buffer_y and view_offset_y > 0:
        scroll_dy = -1
        need_scroll = True
    
    # Проверяем нижнюю границу
    elif py - view_offset_y > view_height - buffer_y and view_offset_y < len(map_data) - view_height:
        scroll_dy = 1
        need_scroll = True
    
    if need_scroll:
        scroll_camera(scroll_dx, scroll_dy)
        return True
    
    return False

def get_visible_map_area():
    """Возвращает видимую область карты"""
    if not map_data:
        return []
    
    visible_area = []
    start_y = view_offset_y
    end_y = min(view_offset_y + view_height, len(map_data))
    start_x = view_offset_x
    end_x = min(view_offset_x + view_width, len(map_data[0]))
    
    for y in range(start_y, end_y):
        row = []
        for x in range(start_x, end_x):
            if y < len(map_data) and x < len(map_data[y]):
                row.append(map_data[y][x])
            else:
                row.append(' ')
        visible_area.append(row)
    
    return visible_area

def show_minimap():
    """Показывает мини-карту в отдельном окне"""
    if not map_data:
        return
    
    minimap_window = tk.Toplevel(root)
    minimap_window.title("Мини-карта")
    minimap_window.geometry("400x400")
    minimap_window.configure(bg="black")
    
    # Создаем Canvas для мини-карты
    minimap_canvas = tk.Canvas(minimap_window, bg="black", highlightthickness=0)
    minimap_canvas.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Размер клетки для мини-карты
    minimap_cell_size = min(400 // len(map_data[0]), 400 // len(map_data), 12)
    
    # Рисуем всю карту
    for y in range(len(map_data)):
        for x in range(len(map_data[y])):
            cell_value = map_data[y][x]
            
            # Цвет для мини-карты (упрощенный)
            if cell_value == "☢": color = "green"
            elif cell_value == "⚡": color = "yellow"
            elif cell_value == "🌳": color = "darkgreen"
            elif cell_value == "🏗": color = "brown"
            elif cell_value == "🦸": color = "red"
            elif cell_value == "🏭": color = "gray"
            elif cell_value == "⚓": color = "lightgreen"
            elif cell_value == "•": color = "darkgray"
            elif cell_value in ["🍄", "🔮", "💎", "🌟", "✨", "☄️"]: color = "purple"
            elif cell_value == "👩": color = "pink"  # NPC Маша
            elif cell_value == ".": color = "#333333"  # Пустая земля
            elif cell_value == "🚧": color = "#555555"  # Завал/граница
            else: color = "black"
            
            minimap_canvas.create_rectangle(
                x * minimap_cell_size, y * minimap_cell_size,
                (x + 1) * minimap_cell_size, (y + 1) * minimap_cell_size,
                fill=color, outline=""
            )
    
    # Рисуем игрока на мини-карте
    px, py = player_position
    minimap_canvas.create_rectangle(
        px * minimap_cell_size, py * minimap_cell_size,
        (px + 1) * minimap_cell_size, (py + 1) * minimap_cell_size,
        fill="cyan", outline="white"
    )
    
    # Рисуем видимую область
    view_rect_x1 = view_offset_x * minimap_cell_size
    view_rect_y1 = view_offset_y * minimap_cell_size
    view_rect_x2 = min((view_offset_x + view_width) * minimap_cell_size, len(map_data[0]) * minimap_cell_size)
    view_rect_y2 = min((view_offset_y + view_height) * minimap_cell_size, len(map_data) * minimap_cell_size)
    
    minimap_canvas.create_rectangle(
        view_rect_x1, view_rect_y1,
        view_rect_x2, view_rect_y2,
        outline="yellow", width=2
    )
    
    # Добавляем подписи ключевых точек
    key_positions = [
        (5, 10, "⚓", "Вы (старт)"),
        (10, 10, "👩", "Маша"),
        (20, 10, "🏗", "Торговля"),
        (15, 8, "🍄", "Артефакт"),
    ]
    
    for x, y, symbol, name in key_positions:
        if 0 <= x < len(map_data[0]) and 0 <= y < len(map_data):
            minimap_canvas.create_text(
                x * minimap_cell_size + minimap_cell_size//2,
                y * minimap_cell_size + minimap_cell_size//2,
                text=symbol,
                font=("TkDefaultFont", minimap_cell_size//2),
                fill="white"
            )
            minimap_canvas.create_text(
                x * minimap_cell_size + minimap_cell_size//2,
                y * minimap_cell_size + minimap_cell_size + 5,
                text=name,
                font=("TkDefaultFont", 7),
                fill="white"
            )
    
    tk.Button(minimap_window, text="Закрыть", command=minimap_window.destroy,
             bg="#F44336", fg="white", font=("TkDefaultFont", 10)).pack(pady=10)

# ========== ОСНОВНЫЕ ФУНКЦИИ ИГРЫ ==========

def hide_artifacts():
    global map_data, original_artifacts
    original_artifacts = []
    
    artifact_emojis = ["🍄", "🔮", "💎", "🌟", "✨", "☄️"]
    
    for y in range(len(map_data)):
        for x in range(len(map_data[y])):
            cell = map_data[y][x]
            if cell in artifact_emojis:
                original_artifacts.append({
                    'pos': (x, y),
                    'type': cell,
                    'hidden': True,
                    'collected': False,
                    'level': artifact_emojis.index(cell) + 1
                })
                map_data[y][x] = "•"

def reveal_artifacts_temporarily(duration, level):
    global compass_active, compass_end_time, visible_artifacts, compass_duration, compass_level
    compass_active = True
    compass_end_time = time.time() + duration
    compass_duration = duration
    compass_level = level
    visible_artifacts = []
    
    for artifact in original_artifacts:
        if artifact['hidden'] and not artifact['collected'] and artifact['level'] <= level:
            x, y = artifact['pos']
            artifact_type = artifact['type']
            visible_artifacts.append((x, y, artifact_type, artifact['level']))
            map_data[y][x] = artifact_type
    
    update_display()
    root.after(int(duration * 1000), hide_revealed_artifacts)

def hide_revealed_artifacts():
    global compass_active, visible_artifacts
    compass_active = False
    
    for artifact in original_artifacts:
        if artifact['hidden'] and not artifact['collected']:
            x, y = artifact['pos']
            map_data[y][x] = "•"
    
    visible_artifacts = []
    update_display()

def draw_game_map():
    """Рисует видимую область игровой карты"""
    game_canvas.delete("all")
    
    if not map_data:
        return
    
    # Получаем видимую область карты
    visible_area = get_visible_map_area()
    
    if not visible_area:
        return
    
    # Рисуем видимую область
    for y in range(len(visible_area)):
        for x in range(len(visible_area[y])):
            cell_value = visible_area[y][x]
            
            # Абсолютные координаты на карте
            abs_x = view_offset_x + x
            abs_y = view_offset_y + y
            
            # Определяем цвет фона
            bg_color = None
            
            if cell_value == "☢": bg_color = "#00FF00"
            elif cell_value == "⚡": bg_color = "#FFFF00"
            elif cell_value == "•": bg_color = "#444444"
            elif cell_value == "🌳": bg_color = "#228B22"
            elif cell_value == "🌧": bg_color = "#4682B4"
            elif cell_value == "🏗": bg_color = "#8B4513"
            elif cell_value == "🦸": bg_color = "#FF0000"
            elif cell_value == "🧟": bg_color = "#8B0000"
            elif cell_value == "💀": bg_color = "#000000"
            elif cell_value == "🏭": bg_color = "#696969"
            elif cell_value == "🚧": bg_color = "#A9A9A9"
            elif cell_value == "💧": bg_color = "#1E90FF"
            elif cell_value == "🔥": bg_color = "#FF4500"
            elif cell_value == "⚓": bg_color = "#32CD32"
            elif cell_value in ["🍄", "🔮", "💎", "🌟", "✨", "☄️"]: bg_color = "#4B0082"
            elif cell_value == "👩": bg_color = "#FF69B4"  # Розовый для Маши
            elif cell_value == ".": bg_color = "#2A2A2A"  # Темно-серый для пустой земли
            
            # Рисуем фон
            if bg_color:
                game_canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=bg_color, outline=""
                )
            
            # Цвет текста
            fill_color = "white" if cell_value in ["☢", "⚡", "•", "💀", "🏭", ".", "🚧"] else "black"
            
            # Для видимых артефактов делаем золотой цвет
            if compass_active and cell_value in ["🍄", "🔮", "💎", "🌟", "✨", "☄️"]:
                fill_color = "#FFD700"
                # Добавляем свечение
                game_canvas.create_oval(
                    x * CELL_SIZE + 5, y * CELL_SIZE + 5,
                    (x + 1) * CELL_SIZE - 5, (y + 1) * CELL_SIZE - 5,
                    outline="#FFD700", width=2
                )
            
            # Для NPC Маши добавляем особый эффект
            if cell_value == "👩":
                fill_color = "#FFFFFF"
                # Добавляем сияние вокруг NPC
                game_canvas.create_oval(
                    x * CELL_SIZE + 2, y * CELL_SIZE + 2,
                    (x + 1) * CELL_SIZE - 2, (y + 1) * CELL_SIZE - 2,
                    outline="#FF69B4", width=3
                )
            
            # Рисуем символ клетки
            game_canvas.create_text(
                (x + 0.5) * CELL_SIZE, (y + 0.5) * CELL_SIZE,
                text=cell_value,
                font=("TkDefaultFont", CELL_SIZE // 2),
                fill=fill_color,
                justify="center"
            )
    
    # Рисуем игрока, если он в видимой области
    display_player()
    
    # Рисуем индикатор позиции камеры
    draw_camera_indicator()

def draw_camera_indicator():
    """Рисует индикатор позиции камеры на карте"""
    if not map_data:
        return
    
    # Показываем координаты камеры в углу
    coord_text = f"Позиция: [{view_offset_x},{view_offset_y}]"
    game_canvas.create_text(10, 20, text=coord_text, 
                          font=("TkDefaultFont", 10), 
                          fill="white", anchor="nw")
    
    # Показываем размер карты
    map_size_text = f"Карта: {len(map_data[0])}x{len(map_data)}"
    game_canvas.create_text(10, 40, text=map_size_text, 
                          font=("TkDefaultFont", 10), 
                          fill="white", anchor="nw")
    
    # Показываем подсказку про Машу
    masha_hint = "Маша находится примерно на (10, 10) - нажми F для поиска"
    game_canvas.create_text(10, 60, text=masha_hint,
                          font=("TkDefaultFont", 9),
                          fill="#FFD700", anchor="nw")

def display_player():
    """Рисует игрока на игровом холсте, если он в видимой области"""
    if not player_position:
        return
    
    px, py = player_position
    
    # Проверяем, находится ли игрок в видимой области
    if (view_offset_x <= px < view_offset_x + view_width and 
        view_offset_y <= py < view_offset_y + view_height):
        
        # Относительные координаты для отображения
        rel_x = px - view_offset_x
        rel_y = py - view_offset_y
        
        game_canvas.create_text((rel_x + 0.5) * CELL_SIZE, (rel_y + 0.5) * CELL_SIZE, 
                               text="⬆", 
                               font=("TkDefaultFont", CELL_SIZE // 2, "bold"), 
                               fill="cyan")
        game_canvas.create_text((rel_x + 0.5) * CELL_SIZE + 2, (rel_y + 0.5) * CELL_SIZE + 2, 
                               text="⬆", 
                               font=("TkDefaultFont", CELL_SIZE // 2, "bold"), 
                               fill="darkblue")

def update_info_panel():
    """Обновляет верхнюю информационную панель"""
    # Очищаем панель
    for widget in info_frame.winfo_children():
        widget.destroy()
    
    # Основная статистика
    stats_frame = tk.Frame(info_frame, bg="#1a1a1a", height=40)
    stats_frame.pack(fill="x", pady=5)
    
    # Здоровье
    health_color = "#FF5555" if player_health < 30 else "#55FF55" if player_health > 70 else "#FFFF55"
    health_label = tk.Label(stats_frame, text=f"♥ {player_health}/100", 
                          font=("TkDefaultFont", 12, "bold"), 
                          fg=health_color, bg="#1a1a1a")
    health_label.pack(side=tk.LEFT, padx=20)
    
    # Уровень
    level_label = tk.Label(stats_frame, text=f"⭐ Ур. {player_level}", 
                          font=("TkDefaultFont", 12, "bold"), 
                          fg="#FFD700", bg="#1a1a1a")
    level_label.pack(side=tk.LEFT, padx=20)
    
    # Деньги
    money_label = tk.Label(stats_frame, text=f"💰 ${player_money}", 
                          font=("TkDefaultFont", 12, "bold"), 
                          fg="#55FF55", bg="#1a1a1a")
    money_label.pack(side=tk.LEFT, padx=20)
    
    # Опыт
    exp_needed = player_level * 100
    exp_percent = (player_exp / exp_needed) * 100 if exp_needed > 0 else 0
    exp_label = tk.Label(stats_frame, text=f"📊 Опыт: {player_exp}/{exp_needed} ({exp_percent:.0f}%)", 
                        font=("TkDefaultFont", 10), 
                        fg="#AAAAAA", bg="#1a1a1a")
    exp_label.pack(side=tk.LEFT, padx=20)
    
    # Координаты игрока
    if player_position:
        coord_label = tk.Label(stats_frame, text=f"📍 [{player_position[0]},{player_position[1]}]", 
                             font=("TkDefaultFont", 10), 
                             fg="#AAAAAA", bg="#1a1a1a")
        coord_label.pack(side=tk.LEFT, padx=20)
    
    # Статус компаса
    if compass_active:
        time_left = max(0, int(compass_end_time - time.time()))
        level_text = ["I", "II", "III", "IV"][compass_level-1] if 1 <= compass_level <= 4 else str(compass_level)
        compass_label = tk.Label(stats_frame, text=f"🔍 Компас {level_text}: {time_left}с", 
                                font=("TkDefaultFont", 10, "bold"), 
                                fg="#00FFFF", bg="#1a1a1a")
        compass_label.pack(side=tk.RIGHT, padx=20)
    
    # Кнопка поиска Маши
    find_masha_btn = tk.Button(stats_frame, text="🔍 Найти Машу (F)", command=find_and_show_masha,
                             bg="#FF69B4", fg="white", font=("TkDefaultFont", 9, "bold"))
    find_masha_btn.pack(side=tk.RIGHT, padx=10)
    
    # Кнопка мини-карты
    minimap_btn = tk.Button(stats_frame, text="🗺 Мини-карта (M)", command=show_minimap,
                          bg="#2196F3", fg="white", font=("TkDefaultFont", 9))
    minimap_btn.pack(side=tk.RIGHT, padx=10)
    
    # Кнопка журнала квестов
    quest_log_btn = tk.Button(stats_frame, text="📜 Квесты (L)", command=show_quest_log,
                            bg="#9C27B0", fg="white", font=("TkDefaultFont", 9))
    quest_log_btn.pack(side=tk.RIGHT, padx=10)
    
    # Индикатор активных квестов
    active_quests_count = sum(1 for quest in quests.values() if quest["active"] and not quest["completed"])
    if active_quests_count > 0:
        quest_indicator = tk.Label(stats_frame, text=f"🎯 Активных квестов: {active_quests_count}", 
                                 font=("TkDefaultFont", 9, "bold"), 
                                 fg="#FF9800", bg="#1a1a1a")
        quest_indicator.pack(side=tk.RIGHT, padx=10)

def update_hotbar():
    """Обновляет hotbar под игровым полем"""
    # Очищаем hotbar
    for widget in hotbar_frame.winfo_children():
        widget.destroy()
    
    # Заголовок hotbar
    hotbar_label = tk.Label(hotbar_frame, text="БЫСТРЫЕ СЛОТЫ (1-9)", 
                          font=("TkDefaultFont", 10, "bold"), 
                          fg="white", bg="#2C2C2C")
    hotbar_label.pack(pady=5)
    
    # Фрейм для слотов
    slots_frame = tk.Frame(hotbar_frame, bg="#2C2C2C")
    slots_frame.pack(pady=10)
    
    # Создаем слоты
    for i, item in enumerate(quick_access_slots):
        slot_frame = tk.Frame(slots_frame, bg="#555555", relief="raised", bd=2, width=60, height=60)
        slot_frame.pack(side=tk.LEFT, padx=5)
        slot_frame.pack_propagate(False)  # Фиксируем размер
        
        # Номер слота
        slot_number = tk.Label(slot_frame, text=str(i+1), 
                             font=("TkDefaultFont", 8, "bold"), 
                             fg="yellow", bg="#555555")
        slot_number.pack(anchor="nw", padx=2, pady=2)
        
        # Предмет в слоте
        if item:
            # Разный цвет для разных типов предметов
            if "Компас" in item:
                item_color = "#00FFFF"
                item_symbol = "🧭"
            elif any(med in item for med in ["Антирэд", "Медпрепарат", "Аптечка", "Бинт"]):
                item_color = "#00FF00"
                item_symbol = "💊"
            elif "Радиоактивное мясо" in item:
                item_color = "#FF5555"
                item_symbol = "🍖"
            elif any(weapon in item for weapon in ["Пистолет", "Обрез", "АК-74"]):
                item_color = "#FFAA00"
                item_symbol = "🔫"
            else:
                item_color = "#FFFFFF"
                item_symbol = "📦"
            
            # Отображаем символ и название (первые 6 символов)
            display_name = item[:6] + "..." if len(item) > 6 else item
            
            item_symbol_label = tk.Label(slot_frame, text=item_symbol, 
                                       font=("TkDefaultFont", 14),
                                       fg=item_color, bg="#555555")
            item_symbol_label.pack(pady=2)
            
            item_name_label = tk.Label(slot_frame, text=display_name, 
                                     font=("TkDefaultFont", 7),
                                     fg=item_color, bg="#555555")
            item_name_label.pack()
        else:
            # Пустой слот
            empty_label = tk.Label(slot_frame, text="Пусто", 
                                 font=("TkDefaultFont", 8),
                                 fg="#AAAAAA", bg="#555555")
            empty_label.pack(expand=True)
        
        # Подсказка при наведении
        if item:
            def make_tooltip(item_text=item, slot_num=i+1):
                def show_tooltip(event=None):
                    tooltip = tk.Toplevel(root)
                    tooltip.wm_overrideredirect(True)
                    tooltip.wm_geometry(f"+{root.winfo_pointerx()+10}+{root.winfo_pointery()+10}")
                    
                    label = tk.Label(tooltip, text=f"Слот {slot_num}: {item_text}", 
                                   bg="yellow", fg="black", font=("TkDefaultFont", 8))
                    label.pack()
                    
                    def hide_tooltip():
                        tooltip.destroy()
                    
                    tooltip.after(2000, hide_tooltip)
                
                return show_tooltip
            
            slot_frame.bind("<Enter>", make_tooltip())

def update_display():
    """Обновляет все элементы интерфейса"""
    draw_game_map()
    update_info_panel()
    update_hotbar()

def use_antired():
    global player_inventory
    if "Антирэд" in player_inventory:
        player_inventory.remove("Антирэд")
        messagebox.showinfo("Антирэд", "Вы использовали Антирэд. Защита от радиации повышена!")
        update_display()
        return True
    return False

def use_medicine():
    global player_inventory, player_health
    medicine_items = ["Медпрепарат", "Аптечка", "Бинт"]
    
    for med_item in medicine_items:
        if med_item in player_inventory:
            player_inventory.remove(med_item)
            if med_item == "Аптечка":
                heal_amount = 50
            elif med_item == "Медпрепарат":
                heal_amount = 30
            else:
                heal_amount = 15
            
            player_health = min(100, player_health + heal_amount)
            messagebox.showinfo(med_item, f"Здоровье восстановлено на {heal_amount}! Текущее здоровье: {player_health}")
            update_display()
            return True
    
    messagebox.showwarning("Нет медикаментов", "У вас нет медикаментов для лечения!")
    return False

def use_compass(compass_name):
    if compass_name not in player_inventory:
        messagebox.showwarning("Нет компаса", f"У вас нет {compass_name}!")
        return False
    
    compass_info = {
        "Компас I уровня": {"level": 1, "duration": 3, "cost": 50},
        "Компас II уровня": {"level": 2, "duration": 5, "cost": 100},
        "Компас III уровня": {"level": 3, "duration": 8, "cost": 200},
        "Компас IV уровня": {"level": 4, "duration": 12, "cost": 400}
    }
    
    info = compass_info.get(compass_name)
    if not info:
        messagebox.showwarning("Ошибка", "Неизвестный тип компаса!")
        return False
    
    player_inventory.remove(compass_name)
    reveal_artifacts_temporarily(info["duration"], info["level"])
    
    messagebox.showinfo("Компас активирован", 
                       f"Компас {compass_name} показывает артефакты до {info['level']} уровня на {info['duration']} секунд!")
    update_display()
    return True

def check_for_visible_artifact_at_position(x, y):
    if not compass_active:
        return None
    
    for ax, ay, atype, alevel in visible_artifacts:
        if ax == x and ay == y and alevel <= compass_level:
            return atype
    
    return None

def interact_with_entity(entity_type):
    x, y = player_position
    
    # Взаимодействие с NPC
    if entity_type in npcs:
        interact_with_npc(entity_type)
        return
    
    # Взаимодействие с артефактами
    if compass_active:
        artifact_type = check_for_visible_artifact_at_position(x, y)
        if artifact_type:
            player_inventory.append(artifact_type)
            artifact_level = 0
            for artifact in original_artifacts:
                if artifact['pos'] == (x, y):
                    artifact_level = artifact['level']
                    break
            
            messagebox.showinfo("Находка!", 
                              f"Вы собрали артефакт {artifact_type} ({artifact_level} уровня)!")
            
            # Обновляем прогресс квестов
            update_quest_progress()
            
            for artifact in original_artifacts:
                if artifact['pos'] == (x, y):
                    artifact['collected'] = True
                    artifact['hidden'] = True
                    break
            
            visible_artifacts[:] = [(ax, ay, atype, alevel) for ax, ay, atype, alevel in visible_artifacts 
                                  if not (ax == x and ay == y)]
            
            map_data[y][x] = "."
            update_display()
            return
    
    # Обычное взаимодействие с другими объектами
    if entity_type == "🏗":
        trade_window()
    elif entity_type == "🦸" or entity_type == "🧟":
        fight_monster(entity_type)
    elif entity_type == "🧘‍♂️":
        if random.random() < 0.3:
            random_item = random.choice(["Консервы", "Вода", "Бинт"])
            player_inventory.append(random_item)
            messagebox.showinfo("Спящий сталкер", 
                              f"Спящий сталкер поделился с вами {random_item}!")
        else:
            messagebox.showinfo("Спящий сталкер", "Спящий сталкер мирно похрапывает...")
    elif entity_type == "☢":
        messagebox.showwarning("Радиация!", "Опасно! Вы в радиоактивной зоне!")
    elif entity_type == "⚡":
        messagebox.showwarning("Аномалия!", "Осторожно! Электрическая аномалия!")
    elif entity_type == "💀":
        messagebox.showwarning("Мертвая зона!", "СМЕРТЕЛЬНО ОПАСНО! Немедленно уходите!")
    elif entity_type == "🏭":
        messagebox.showinfo("Энергоблок", "Вы у энергоблока. Здесь высокий радиационный фон.")
    elif entity_type == "⚓":
        messagebox.showinfo("Безопасная зона", "Вы в относительно безопасном месте.")
    elif entity_type == "•":
        if compass_active:
            artifact_type = check_for_visible_artifact_at_position(x, y)
            if artifact_type:
                player_inventory.append(artifact_type)
                messagebox.showinfo("Находка!", f"Вы собрали артефакт {artifact_type}!")
                
                # Обновляем прогресс квестов
                update_quest_progress()
                
                for artifact in original_artifacts:
                    if artifact['pos'] == (x, y):
                        artifact['collected'] = True
                        artifact['hidden'] = True
                        break
                
                visible_artifacts[:] = [(ax, ay, atype, alevel) for ax, ay, atype, alevel in visible_artifacts 
                                      if not (ax == x and ay == y)]
                
                map_data[y][x] = "."
                update_display()
            else:
                messagebox.showinfo("Осмотр", "Здесь был артефакт, но его уже собрали.")
        else:
            messagebox.showinfo("Осмотр", "Здесь что-то есть, но вы не видите что именно...")
    elif entity_type == ".":
        messagebox.showinfo("Пустая местность", "Ничего интересного здесь нет.")
    elif entity_type == "🚧":
        messagebox.showinfo("Завал", "Здесь завал. Нужно обойти.")

def trade_window():
    trade_root = tk.Toplevel(root)
    trade_root.title("Торговая база")
    trade_root.geometry("500x600")
    
    notebook = tk.ttk.Notebook(trade_root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    buy_frame = tk.Frame(notebook)
    notebook.add(buy_frame, text='Купить')
    
    global player_money
    lbl_money = tk.Label(buy_frame, text=f"Баланс: ${player_money}", 
                        font=("TkDefaultFont", 14, "bold"), fg="green")
    lbl_money.pack(pady=10)
    
    buy_listbox = tk.Listbox(buy_frame, height=15, font=("TkDefaultFont", 10))
    scrollbar = tk.Scrollbar(buy_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    buy_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    scrollbar.config(command=buy_listbox.yview)
    buy_listbox.config(yscrollcommand=scrollbar.set)
    
    for item, price in item_prices.items():
        buy_listbox.insert(tk.END, f"{item} - ${price}")
    
    def buy_item():
        global player_money
        if buy_listbox.curselection():
            selected_text = buy_listbox.get(buy_listbox.curselection()[0])
            item_name = selected_text.split(' - $')[0]
            price = int(selected_text.split(' - $')[1])
            
            if player_money >= price:
                player_inventory.append(item_name)
                player_money -= price
                lbl_money.config(text=f"Баланс: ${player_money}")
                messagebox.showinfo("Покупка", f"Вы купили {item_name} за ${price}!")
                update_display()
            else:
                messagebox.showwarning("Недостаточно денег", 
                                      f"Не хватает ${price - player_money}!")
        else:
            messagebox.showwarning("Ошибка", "Выберите товар для покупки!")
    
    tk.Button(buy_frame, text="Купить выбранное", command=buy_item, 
             bg="lightgreen", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    sell_frame = tk.Frame(notebook)
    notebook.add(sell_frame, text='Продать')
    
    sell_listbox = tk.Listbox(sell_frame, height=15, font=("TkDefaultFont", 10))
    scrollbar2 = tk.Scrollbar(sell_frame)
    scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
    sell_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    scrollbar2.config(command=sell_listbox.yview)
    sell_listbox.config(yscrollcommand=scrollbar2.set)
    
    def update_sell_list():
        sell_listbox.delete(0, tk.END)
        if not player_inventory:
            sell_listbox.insert(tk.END, "Инвентарь пуст")
        else:
            item_counts = {}
            for item in player_inventory:
                item_counts[item] = item_counts.get(item, 0) + 1
            
            for item, count in item_counts.items():
                price = item_prices.get(item, 10)
                total_price = price * count
                sell_listbox.insert(tk.END, f"{item} x{count} - ${total_price} (${price} за шт.)")
    
    update_sell_list()
    
    def sell_item():
        global player_money
        if sell_listbox.curselection():
            selected_text = sell_listbox.get(sell_listbox.curselection()[0])
            
            if "Инвентарь пуст" in selected_text:
                return
            
            item_part = selected_text.split(' x')[0]
            count_part = selected_text.split(' x')[1].split(' - $')[0]
            count = int(count_part)
            
            price_text = selected_text.split('($')[1].split(' за шт.)')[0]
            price_per_item = int(price_text.replace('$', ''))
            
            total_price = price_per_item * count
            player_inventory[:] = [item for item in player_inventory if item != item_part]
            
            player_money += total_price
            lbl_money.config(text=f"Баланс: ${player_money}")
            update_sell_list()
            update_display()
            messagebox.showinfo("Продажа", 
                              f"Вы продали {item_part} x{count} за ${total_price}!")
        else:
            messagebox.showwarning("Ошибка", "Выберите предмет для продажи!")
    
    tk.Button(sell_frame, text="Продать выбранное", command=sell_item,
             bg="lightcoral", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
    
    def sell_all():
        global player_money
        if not player_inventory:
            messagebox.showinfo("Продажа", "Инвентарь пуст!")
            return
        
        total_income = 0
        items_sold = {}
        
        for item in player_inventory:
            price = item_prices.get(item, 10)
            total_income += price
            items_sold[item] = items_sold.get(item, 0) + 1
        
        player_inventory.clear()
        player_money += total_income
        lbl_money.config(text=f"Баланс: ${player_money}")
        update_sell_list()
        update_display()
        
        report = "Продано:\n"
        for item, count in items_sold.items():
            price = item_prices.get(item, 10)
            report += f"{item} x{count} = ${price * count}\n"
        report += f"\nВсего: ${total_income}"
        
        messagebox.showinfo("Продажа всего", report)
    
    tk.Button(sell_frame, text="Продать ВСЁ", command=sell_all,
             bg="red", fg="white", font=("TkDefaultFont", 10, "bold")).pack(pady=5)
    
    tk.Button(trade_root, text="Закрыть", command=trade_root.destroy,
             bg="gray", fg="white", font=("TkDefaultFont", 10)).pack(pady=10)

def fight_monster(monster_type):
    monster_strength = {"🦸": 3, "🧟": 1}[monster_type]
    win_chance = min(0.9, 0.5 + (player_level * 0.1))
    
    if random.random() < win_chance:
        loot = random.choice(["Радиоактивное мясо", "Обрез", "Бронежилет", "Консервы", "Вода"])
        player_inventory.append(loot)
        messagebox.showinfo("Победа!", 
                          f"Вы победили {monster_type}! Получено: {loot}")
        player_exp += monster_strength * 10
        check_level_up()
    else:
        damage = entity_damage[monster_type]
        player_health -= damage
        messagebox.showwarning("Поражение", 
                             f"Вы проиграли битву! Получено урона: {damage}")
        if player_health <= 0:
            messagebox.showinfo("Game Over", "Вы погибли в бою!")
            root.quit()
    
    update_display()

def check_level_up():
    global player_level, player_exp
    exp_needed = player_level * 100
    
    if player_exp >= exp_needed:
        player_level += 1
        player_exp = 0
        player_health = min(100, player_health + 20)
        messagebox.showinfo("Повышение уровня!", 
                          f"Поздравляем! Вы достигли {player_level} уровня!\nЗдоровье восстановлено.")
        update_display()

def take_damage(entity_type):
    global player_health
    damage = entity_damage.get(entity_type, 0)
    
    if entity_type == "☢" and use_antired():
        damage = max(1, damage // 2)
    
    player_health -= damage
    if player_health <= 0:
        messagebox.showinfo("Game Over", "Вы погибли!")
        root.quit()
    else:
        update_display()

def open_inventory():
    inventory_root = tk.Toplevel(root)
    inventory_root.title("Инвентарь")
    inventory_root.geometry("400x500")
    
    frame = tk.Frame(inventory_root, bg="#2C2C2C")
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    tk.Label(frame, text="ИНВЕНТАРЬ", font=("Arial", 16, "bold"), 
            bg="#2C2C2C", fg="white").pack(pady=10)
    
    listbox = tk.Listbox(frame, height=20, font=("TkDefaultFont", 10), 
                        bg="#444444", fg="white", selectbackground="#666666")
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    scrollbar.config(command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    
    if not player_inventory:
        listbox.insert(tk.END, "Инвентарь пуст")
    else:
        item_counts = {}
        for item in player_inventory:
            item_counts[item] = item_counts.get(item, 0) + 1
        
        for item, count in item_counts.items():
            price = item_prices.get(item, "?")
            listbox.insert(tk.END, f"{item} x{count} (${price} за шт.)")
    
    btn_frame = tk.Frame(frame, bg="#2C2C2C")
    btn_frame.pack(pady=10)
    
    def assign_to_slot():
        if listbox.curselection() and listbox.get(listbox.curselection()[0]) != "Инвентарь пуст":
            selected_text = listbox.get(listbox.curselection()[0])
            item_name = selected_text.split(' x')[0]
            
            slot_window = tk.Toplevel(inventory_root)
            slot_window.title("Назначить на слот")
            slot_window.geometry("250x350")
            slot_window.configure(bg="#2C2C2C")
            
            tk.Label(slot_window, text="Выберите слот:", font=("TkDefaultFont", 12, "bold"),
                    bg="#2C2C2C", fg="white").pack(pady=10)
            
            slot_var = tk.IntVar(value=0)
            slot_frame = tk.Frame(slot_window, bg="#2C2C2C")
            slot_frame.pack()
            
            for i in range(9):
                slot_text = f"Слот {i+1}: {quick_access_slots[i] if quick_access_slots[i] else 'Пусто'}"
                tk.Radiobutton(slot_frame, text=slot_text, variable=slot_var, value=i,
                              bg="#2C2C2C", fg="white", selectcolor="#444444",
                              font=("TkDefaultFont", 9)).pack(anchor="w", padx=20, pady=2)
            
            def confirm_slot():
                quick_access_slots[slot_var.get()] = item_name
                messagebox.showinfo("Успех", f"Предмет {item_name} назначен на слот {slot_var.get()+1}")
                slot_window.destroy()
                update_display()
            
            tk.Button(slot_window, text="Назначить", command=confirm_slot,
                     bg="#4CAF50", fg="white", font=("TkDefaultFont", 10, "bold")).pack(pady=10)
        else:
            messagebox.showwarning("Ошибка", "Выберите предмет из инвентаря")
    
    def use_item():
        if listbox.curselection() and listbox.get(listbox.curselection()[0]) != "Инвентарь пуст":
            selected_text = listbox.get(listbox.curselection()[0])
            item_name = selected_text.split(' x')[0]
            
            if "Компас" in item_name:
                use_compass(item_name)
            elif item_name in ["Антирэд", "Медпрепарат", "Аптечка", "Бинт"]:
                if "Антирэд" in item_name:
                    use_antired()
                else:
                    use_medicine()
            else:
                messagebox.showinfo("Предмет", f"Использован предмет: {item_name}")
        else:
            messagebox.showwarning("Ошибка", "Выберите предмет для использования")
    
    tk.Button(btn_frame, text="Назначить на слот", command=assign_to_slot,
             bg="#2196F3", fg="white", font=("TkDefaultFont", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(btn_frame, text="Использовать", command=use_item,
             bg="#4CAF50", fg="white", font=("TkDefaultFont", 10)).pack(side=tk.LEFT, padx=5)
    
    tk.Button(btn_frame, text="Закрыть", command=inventory_root.destroy,
             bg="#F44336", fg="white", font=("TkDefaultFont", 10)).pack(side=tk.LEFT, padx=5)

def use_selected_item(index):
    item = quick_access_slots[index]
    if item:
        if "Компас" in item:
            use_compass(item)
        elif item in ["Антирэд", "Медпрепарат", "Аптечка", "Бинт"]:
            if item == "Антирэд":
                use_antired()
            else:
                use_medicine()
        else:
            messagebox.showinfo("Предмет", f"Использован предмет: {item}")
    else:
        messagebox.showinfo("Слот пуст", "Этот слот быстрого доступа пуст")

def on_click(event):
    # Проверяем, что клик был в области игрового холста
    if event.widget == game_canvas:
        x, y = event.x, event.y
        
        # Преобразуем координаты клика в координаты на карте
        map_x = view_offset_x + (x // CELL_SIZE)
        map_y = view_offset_y + (y // CELL_SIZE)
        
        # Проверяем, что координаты в пределах карты
        if 0 <= map_y < len(map_data) and 0 <= map_x < len(map_data[map_y]):
            symbol = map_data[map_y][map_x]
            if symbol in ENTITY_TYPES:
                messagebox.showinfo("Объект", f"{ENTITY_TYPES[symbol]}\nКоординаты: [{map_x},{map_y}]")
            elif symbol == "•":
                if compass_active:
                    messagebox.showinfo("Тайное место", "Здесь скрыт артефакт!")
                else:
                    messagebox.showinfo("Тайное место", "Здесь что-то скрыто...")

def process_keypress(event):
    global player_position
    
    if event.keysym == 'F11':
        root.attributes('-fullscreen', not root.attributes('-fullscreen'))
        return
    elif event.keysym == 'F5':  # Сохранить игру
        save_game()
        return
    elif event.keysym == 'F9':  # Загрузить игру
        load_game()
        return
    elif event.keysym == 'i':
        open_inventory()
        return
    elif event.keysym == 'o':
        settings_window()
        return
    elif event.keysym == 'p':
        trade_window()
        return
    elif event.keysym == 'm':  # Мини-карта
        show_minimap()
        return
    elif event.keysym == 'l':  # Журнал квестов
        show_quest_log()
        return
    elif event.keysym == 'f':  # Найти Машу
        find_and_show_masha()
        return
    
    # Прокрутка карты стрелками
    if event.keysym == 'Up':
        scroll_camera(0, -1)
        return
    elif event.keysym == 'Down':
        scroll_camera(0, 1)
        return
    elif event.keysym == 'Left':
        scroll_camera(-1, 0)
        return
    elif event.keysym == 'Right':
        scroll_camera(1, 0)
        return
    
    key = event.char.lower() if event.char else ''
    
    new_pos = None
    if key == hotkeys['move_up']:
        new_pos = (player_position[0], max(player_position[1]-1, 0))
    elif key == hotkeys['move_down']:
        new_pos = (player_position[0], min(player_position[1]+1, len(map_data)-1))
    elif key == hotkeys['move_left']:
        new_pos = (max(player_position[0]-1, 0), player_position[1])
    elif key == hotkeys['move_right']:
        new_pos = (min(player_position[0]+1, len(map_data[0])-1), player_position[1])
    elif key == hotkeys['interaction']:
        x, y = player_position
        if 0 <= y < len(map_data) and 0 <= x < len(map_data[y]):
            current_symbol = map_data[y][x]
            interact_with_entity(current_symbol)
        return
    elif key.isdigit() and 1 <= int(key) <= 9:
        index = int(key) - 1
        use_selected_item(index)
        return
    
    if new_pos is not None:
        current_symbol = map_data[new_pos[1]][new_pos[0]]
        player_position = new_pos
        
        # Автоматическая прокрутка камеры к игроку
        auto_scroll_to_player()
        
        if entity_damage.get(current_symbol, 0) > 0:
            take_damage(current_symbol)
        
        if compass_active:
            artifact_type = check_for_visible_artifact_at_position(new_pos[0], new_pos[1])
            if artifact_type:
                player_inventory.append(artifact_type)
                
                # Обновляем прогресс квестов
                update_quest_progress()
                
                for artifact in original_artifacts:
                    if artifact['pos'] == (new_pos[0], new_pos[1]):
                        messagebox.showinfo("Находка!", 
                                          f"Вы нашли артефакт {artifact_type} ({artifact['level']} уровня)!")
                        artifact['collected'] = True
                        artifact['hidden'] = True
                        break
                
                visible_artifacts[:] = [(ax, ay, atype, alevel) for ax, ay, atype, alevel in visible_artifacts 
                                      if not (ax == new_pos[0] and ay == new_pos[1])]
                
                map_data[new_pos[1]][new_pos[0]] = "."
        
        update_display()

def settings_window():
    settings_root = tk.Toplevel(root)
    settings_root.title("Настройки")
    settings_root.geometry("300x500")
    settings_root.configure(bg="#2C2C2C")
    
    tk.Label(settings_root, text="Настройки игры", 
            font=("Arial", 14, "bold"), bg="#2C2C2C", fg="white").pack(pady=10)
    
    # Кнопки сохранения/загрузки
    save_load_frame = tk.Frame(settings_root, bg="#2C2C2C")
    save_load_frame.pack(pady=10)
    
    tk.Button(save_load_frame, text="Сохранить игру (F5)", command=lambda: save_game(),
             bg="#4CAF50", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(save_load_frame, text="Загрузить игру (F9)", command=lambda: load_game(),
             bg="#2196F3", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(save_load_frame, text="Управление сохранениями", command=show_save_load_menu,
             bg="#9C27B0", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    # Сохранение/загрузка карт
    map_frame = tk.Frame(settings_root, bg="#2C2C2C")
    map_frame.pack(pady=10)
    
    tk.Button(map_frame, text="Сохранить карту", command=save_map_to_file,
             bg="#FF9800", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(map_frame, text="Загрузить карту", command=load_map_from_file,
             bg="#FF5722", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    # Карта
    map_tools_frame = tk.Frame(settings_root, bg="#2C2C2C")
    map_tools_frame.pack(pady=10)
    
    tk.Button(map_tools_frame, text="Показать мини-карту (M)", command=show_minimap,
             bg="#2196F3", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(map_tools_frame, text="Центрировать на игроке", command=center_camera_on_player,
             bg="#4CAF50", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(map_tools_frame, text="Найти Машу (F)", command=find_and_show_masha,
             bg="#FF69B4", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    # Квесты
    quests_frame = tk.Frame(settings_root, bg="#2C2C2C")
    quests_frame.pack(pady=10)
    
    tk.Button(quests_frame, text="Журнал квестов (L)", command=show_quest_log,
             bg="#9C27B0", fg="white", font=("TkDefaultFont", 10)).pack(pady=5, fill="x")
    
    tk.Button(settings_root, text="Закрыть", command=settings_root.destroy,
             bg="#F44336", fg="white", font=("TkDefaultFont", 10)).pack(pady=20)

# ========== СОЗДАНИЕ ГЛАВНОГО ОКНА ==========

root = tk.Tk()
root.title("STALKER: Чернобыль - Квест Маши (Маленькая карта)")
root.geometry("1200x900")
root.configure(bg="black")

# Импортируем ttk
from tkinter import ttk

# Структура окна
info_frame = tk.Frame(root, bg="#1a1a1a", height=60)
info_frame.pack(fill="x", side="top")
info_frame.pack_propagate(False)

# Основное игровое поле
main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Холст для игры
game_canvas = tk.Canvas(main_frame, bg="black", highlightthickness=0)
game_canvas.pack(fill="both", expand=True)

# Hotbar внизу
hotbar_frame = tk.Frame(root, bg="#2C2C2C", height=120)
hotbar_frame.pack(fill="x", side="bottom")
hotbar_frame.pack_propagate(False)

# Привязка событий
game_canvas.bind("<Button-1>", on_click)
root.bind("<KeyPress>", process_keypress)

# Меню с функциями сохранения и квестов
menu_bar = tk.Menu(root, bg="#2C2C2C", fg="white")

file_menu = tk.Menu(menu_bar, tearoff=0, bg="#2C2C2C", fg="white")
file_menu.add_command(label="Новая игра", command=lambda: [messagebox.showinfo("Новая игра", "Начнем заново!"), root.quit()])
file_menu.add_command(label="Сохранить игру (F5)", command=lambda: save_game())
file_menu.add_command(label="Загрузить игру (F9)", command=lambda: load_game())
file_menu.add_command(label="Управление сохранениями", command=show_save_load_menu)
file_menu.add_separator()
file_menu.add_command(label="Сохранить карту", command=save_map_to_file)
file_menu.add_command(label="Загрузить карту", command=load_map_from_file)
file_menu.add_separator()
file_menu.add_command(label="Выход", command=root.quit)
menu_bar.add_cascade(label="Файл", menu=file_menu)

game_menu = tk.Menu(menu_bar, tearoff=0, bg="#2C2C2C", fg="white")
game_menu.add_command(label="Инвентарь (I)", command=open_inventory)
game_menu.add_command(label="Торговля (P)", command=trade_window)
game_menu.add_separator()
game_menu.add_command(label="Найти Машу (F)", command=find_and_show_masha)
game_menu.add_command(label="Мини-карта (M)", command=show_minimap)
game_menu.add_command(label="Журнал квестов (L)", command=show_quest_log)
game_menu.add_command(label="Центрировать камеру", command=center_camera_on_player)
menu_bar.add_cascade(label="Игра", menu=game_menu)

help_menu = tk.Menu(menu_bar, tearoff=0, bg="#2C2C2C", fg="white")
help_menu.add_command(label="Управление", 
                     command=lambda: messagebox.showinfo("Управление",
                     "Горячие клавиши:\n"
                     "F5 - Сохранить игру\n"
                     "F9 - Загрузить игру\n"
                     "WASD - Движение игрока\n"
                     "Стрелки - Прокрутка карты\n"
                     "E - Взаимодействие с объектами/NPC\n"
                     "F - Найти Машу\n"
                     "1-9 - Слоты быстрого доступа\n"
                     "I - Инвентарь\n"
                     "P - Торговля\n"
                     "M - Мини-карта\n"
                     "L - Журнал квестов\n"
                     "F11 - Полный экран\n\n"
                     "Карта специально маленькая!\n"
                     "Ключевые координаты:\n"
                     "- Старт: (5, 10)\n"
                     "- Маша: (10, 10)\n"
                     "- Торговля: (20, 10)\n"
                     "- Артефакт: (15, 8)\n\n"
                     "Квест: найдите Машу и принесите ей артефакт Артемида (🍄)!\n"
                     "⚠️ Этот квест можно выполнить ТОЛЬКО 1 раз!"))
menu_bar.add_cascade(label="Помощь", menu=help_menu)

settings_menu = tk.Menu(menu_bar, tearoff=0, bg="#2C2C2C", fg="white")
settings_menu.add_command(label="Настройки игры", command=settings_window)
menu_bar.add_cascade(label="Настройки", menu=settings_menu)

root.config(menu=menu_bar)

# Создаем маленькую карту с NPC и инициализируем игру
if map_data is None:
    map_data = create_very_small_map_with_npc()
    player_position = (5, 10)  # Старт на безопасной зоне
    hide_artifacts()
    center_camera_on_player()

# Начальные предметы
player_inventory.extend(["Медпрепарат", "Компас I уровня", "Антирэд", "Консервы", "Вода"])
quick_access_slots[0] = "Медпрепарат"
quick_access_slots[1] = "Антирэд"
quick_access_slots[2] = "Компас I уровня"

# Первоначальное обновление отображения
update_display()

# Информация при старте
messagebox.showinfo("Добро пожаловать!", 
                   "Добро пожаловать в STALKER: Чернобыль!\n\n"
                   "⚡ ВЕРСИЯ С МАЛЕНЬКОЙ КАРТОЙ ⚡\n\n"
                   "🎯 ЦЕЛЬ ИГРЫ:\n"
                   "1. Найдите Машу (👩) - нажмите F для поиска\n"
                   "2. Возьмите у неё уникальный квест\n"
                   "3. Найдите артефакт Артемида (🍄)\n"
                   "4. Принесите артефакт Маше за $300 (в 3 раза больше!)\n\n"
                   "📌 КЛЮЧЕВЫЕ КООРДИНАТЫ:\n"
                   "• Вы начинаете: (5, 10) ⚓\n"
                   "• Маша: (10, 10) 👩\n"
                   "• Торговая база: (20, 10) 🏗\n"
                   "• Артефакт Артемида: примерно (15, 8) 🍄\n\n"
                   "Удачи в поисках! Этот квест можно выполнить только 1 раз!")

root.mainloop()
