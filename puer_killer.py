import telebot, json, os, datetime, schedule, time, threading, random
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '8365097962:AAFeogaH2yndWe05GB947y-tA7yyebhCej8'      
CHAT_ID = 622993612                

bot = telebot.TeleBot(TOKEN)
DATA_FILE = 'king_compass.json'

# === ДАННЫЕ ===
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {
        'xp': 0, 'level': 0,
        'body': 10, 'disc': 10, 'border': 5,
        'anima': 5, 'agression': 5, 'selfworth': 5,
        'day': 0, 'streak': 0, 'done_today': [], 'last_date': None,
        'missed_days': 0, 'extra_done': False, 'extra_task': None
    }

# === БАЗОВЫЕ ЗАДАНИЯ (всегда) ===
base_tasks = ["Пресс","Приседания","Пыль/быт","Книга 10+ стр","«Нет» без объяснений","Дневник 500+ знаков"]

# === ЭКСТРА-ЗАДАНИЯ (30 жёстких) ===
extra_tasks = [
    "8 часов без соцсетей и мессенджеров","Сказать «нет» 5 раз подряд","10 часов полного молчания","100 отжиманий за день",
    "15 000 шагов","Холодный душ 2 минуты","Сторис без фильтров + «я в процессе»","Написать 10 людям, которых боишься",
    "Только еда, которую сам приготовил","3 часа без телефона (выключен)","50 приседаний с весом","Пробежка по полю в любую погоду",
    "Сказать жене правду по больному вопросу","Голосовуха 2 мин о слабостях","День без кофе/сладково","100 отжиманий",
    "2 км бегом","3 страницы от руки","200 приседаний","Спать в 21:30","5 минут планки","48 часов без сладкого",
    "2 час на улице без телефона","10 подтягиваний","50 страниц книги","День без критики","500 скакалок"
]

# === ЕЖЕДНЕВНЫЕ 6 ЗАДАНИЙ (меняются по уровням) ===
def current_tasks():
    if data['level'] < 7:  # Ребёнок → Ученик
        return [  "Пресс по программе",
            "Приседания 30 раз",
            "Пыль/быт 15 минут",
            "Книга 10+ страниц",
            "«Нет» без объяснений (минимум 1 раз)",
            "Дневник 500+ знаков"]
    elif data['level'] < 13:  # Воин
        return ["Пресс по программе",
            "30 бурпи или 100 отжиманий",
            "Холодный душ 2 минуты",
            "Сказать «нет» 3 раза в день без объяснений",
            "2 часа полного молчания",
            "Подъём в 6:00",
            "Дневник: «Что я сегодня подавил в себе?»"]
    elif data['level'] < 20:  # Рыцарь
        return [  "Пресс по программе",
            "Рисование",
            "2 часа без телефона (выключен)",
            "Не спасать никого сегодня",
            "50 агрессивных ударов по подушке с криком",
            "Дневник: «Чего я сегодня избегал?»"]
    elif data['level'] < 27:  # Лорд — Анима
        return ["Пресс по программе",
            "15 минут диалога с Анимой (активное воображение)",
            "Сделать что-то заботливое для себя (ванна, массаж, готовка)",
            "2 часа полного присутствия с женой без телефона",
            "Записать голосовуху 2 мин о своих страхах",
            "Холодный душ 2 минуты",
            "Дневник от лица внутренней женщины"]
    elif data['level'] < 30:  # Герцог — Самость
        return ["Пресс по программе",
            "Создать и выложить контент для других (голосовуха/пост)",
            "30 минут полного одиночества без стимулов",
            "Сделать то, что пугает до дрожи",
            "Помочь одному человеку (по-настоящему)",
            "Подъём в 5:30 + 100 отжиманий",
            "Дневник: «Кто я без масок?»"]
    else:  # КОРОЛЬ
        return ["Задание 1 (ты сам)","Задание 2 (ты сам)","Задание 3 (ты сам)","Задание 4 (ты сам)","Задание 5 (ты сам)","Задание 6 (ты сам)"]

def save():
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def new_day():
    today = datetime.date.today().isoformat()
    if data['last_date'] != today:
        data['done_today'] = []
        data['extra_done'] = False
        data['extra_task'] = random.choice(extra_tasks)
        data['day'] += 1
        data['last_date'] = today
        save()

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add("📊 Статы","✅ Задания","✔ Отметить","⚡ Экстра")
    return m
    

@bot.message_handler(commands=['start'])
def start(m):
    if m.chat.id != CHAT_ID: return
    new_day()
    bot.send_message(CHAT_ID,"⚔️ Компас Короля v6.0",reply_markup=menu())

# === КРАСИВЫЕ СТАТЫ ===
@bot.message_handler(func=lambda m: m.text == "📊 Статы")
def stats(m):
    if m.chat.id != CHAT_ID: return
    new_day()
    lvl = data['level']
    name = ["Ребёнок","Ученик","Воин","Рыцарь","Лорд","Герцог","КОРОЛЬ"][lvl]
    xp_req = [0,600,1800,3600,6000,9000,13000,18000,24000,31000,39000,48000,58000,69000,81000,94000,108000,123000,139000,156000,174000,193000,213000,234000,256000,279000,303000,328000,354000,381000]
    next_xp = xp_req[lvl+1] if lvl < 30 else data['xp'] + 10000
    xp_progress = int((data['xp'] - xp_req[lvl]) / (next_xp - xp_req[lvl]) * 100)
    xp_bar = "🟩" * (xp_progress // 10) + "⬜" * (10 - xp_progress // 10)
    bar = lambda x: "🟩"*(x//10) + "⬜"*(10-x//10)
    bot.send_message(CHAT_ID,f"""
👑 Никита | {name} | Уровень {lvl}/30

⚡ XP: {data['xp']:,} / {next_xp:,}
{xp_bar} {xp_progress}%

❤️  Тело         {bar(data['body'])} {data['body']}/100
🛡️  Дисциплина   {bar(data['disc'])} {data['disc']}/100
🔥 Границы       {bar(data['border'])} {data['border']}/100
💞 Анима         {bar(data['anima'])} {data['anima']}/100
⚔️ Агрессия      {bar(data['agression'])} {data['agression']}/100
🌟 Самоценность  {bar(data['selfworth'])} {data['selfworth']}/100

🏆 Стрик: {data['streak']} | День: {data['day']}
""")

# === ЗАДАНИЯ, ОТМЕТКА, ЭКСТРА, НАКАЗАНИЕ — всё как в предыдущей версии, только с прокачкой навыков ===
# (остальной код из v5.0, только в done добавляем прокачку)

# Пример прокачки в done:
@bot.message_handler(func=lambda m: "—" in m.text)
def done(m):
    if m.chat.id != CHAT_ID: return
    try:
        idx = str(int(m.text.split()[0])-1)
        if idx not in data['done_today']:
            data['done_today'].append(idx)

            # === БАЗОВЫЕ ЗАДАНИЯ (0–5) ===
            if idx == '0':   # Пресс
                data['xp'] += 100
                data['body'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 тело +100ХР",reply_markup=menu())
                
            elif idx == '1': # Приседания
                data['xp'] += 70
                data['body'] += 1
                data['agression'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 тело +1 агрессия +70ХР",reply_markup=menu())


            elif idx == '2': # Пыль/быт
                data['xp'] += 50
                data['disc'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 дисциплина +50ХР",reply_markup=menu())


            elif idx == '3': # Книга
                data['xp'] += 25
                data['disc'] += 1
                data['anima'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 дисциплина +1 анима +50ХР",reply_markup=menu())

            elif idx == '4': # «Нет» без объяснений
                data['xp'] += 200
                data['border'] += 1
                data['selfworth'] += 1
                data['agression'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 границы +1 самоценность +1 агрессия +200ХР",reply_markup=menu())

            elif idx == '5': # Дневник
                data['xp'] += 70
                data['selfworth'] += 1
                data['anima'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 самоценность +1 анима +70ХР",reply_markup=menu())

            # === УРОВЕНЬ 3–6 ===
            elif idx == '6': # Футбол / бокс
                data['xp'] += 200
                data['body'] += 2
                data['agression'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +2 тело +1 агрессия +200ХР",reply_markup=menu())

            elif idx == '7': # 30 бурпи
                data['xp'] += 180
                data['body'] += 1
                data['agression'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 тело +1 агрессия +180ХР",reply_markup=menu())


            elif idx == '8': # Холодный душ
                data['xp'] += 150
                data['body'] += 1
                data['disc'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 тело +1 дисциплина +150ХР",reply_markup=menu())
                

            # === УРОВЕНЬ 7–12 ===
            elif idx == '9':  # Сказать «нет» 3 раза
                data['xp'] += 160
                data['border'] += 1
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 границы +1 самоценность +160ХР",reply_markup=menu())

            elif idx == '10': # 30 мин молчания
                data['xp'] += 140
                data['anima'] += 1
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 анима +1 самоценность +140ХР",reply_markup=menu())

            elif idx == '11': # Подъём 6:00
                data['xp'] += 120
                data['disc'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n  +1 дисциплина +120ХР",reply_markup=menu())

            # === УРОВЕНЬ 13–19 (Дофаминовый детокс) ===
            elif idx == '12': # 8 ч без соцсетей
                data['xp'] += 200
                data['disc'] += 2
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +2 дисциплина +1 самоценность +200ХР",reply_markup=menu())

            elif idx == '13': # Без сахара/кофе
                data['xp'] += 180
                data['body'] += 1
                data['disc'] += 2
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f"✓ Задание выполнено!\n +1 тело +2 дисциплина +1 самоценность +180ХР",reply_markup=menu())

            elif idx == '14': # Не спасать никого
                data['xp'] += 220
                data['border'] += 1
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f" +2 границы +1 агрессия +200ХР",reply_markup=menu())

            # === УРОВЕНЬ 20–26 (Анима) ===
            elif idx == '15': # Диалог с Анимой
                data['xp'] += 250
                data['anima'] += 3
                data['selfworth'] += 1
                bot.send_message(CHAT_ID,f" +3 анима +1 самоценность +250ХР",reply_markup=menu())

            elif idx == '16': # Забота о себе
                data['xp'] += 180
                data['anima'] += 2
                data['selfworth'] += 2
                bot.send_message(CHAT_ID,f" +2 аанима +2 самоценность +350ХР",reply_markup=menu())

            elif idx == '17': # Присутствие с женой
                data['xp'] += 200
                data['anima'] += 2
                bot.send_message(CHAT_ID,f" +2 анима +200ХР",reply_markup=menu())

            # === УРОВЕНЬ 27–29 (Самость) ===
            elif idx == '18': # Создать контент
                data['xp'] += 300
                data['disc'] += 1
                data['selfworth'] += 2
                bot.send_message(CHAT_ID,f" +2 самоценность +1 дисциплина +300ХР",reply_markup=menu())

            elif idx == '19': # 30 мин одиночества
                data['xp'] += 250
                data['anima'] += 1
                data['selfworth'] += 2
                bot.send_message(CHAT_ID,f" +1 анима +2 самоценность +250ХР",reply_markup=menu())

            save()

            # Проверка полного дня
            if len(data['done_today']) == len(current_tasks()):
                data['xp'] += 300
                data['streak'] += 1
                data['day'] += 1
                data['done_today'] = []
                save()
                bot.send_message(CHAT_ID,"🎉 ДЕНЬ ПРОЙДЕН! +300 XP бонус!")

    except Exception as e:
        print(e)

# (остальные функции — tasks, extra, night_check — без изменений)

# === ЗАДАНИЯ ===
@bot.message_handler(func=lambda m: m.text == "✅ Задания")
def show_tasks(m):
    if m.chat.id != CHAT_ID: return
    new_day()
    tasks = f"⚔️ День {data['day']} | Уровень {data['level']}\n\n"
    for i, task in enumerate(current_tasks()):
        mark = "✅" if str(i) in data['done_today'] else "⬜"
        tasks += f"{mark} {task}\n"
    bot.send_message(CHAT_ID,tasks)

# === ОТМЕТИТЬ ===
@bot.message_handler(func=lambda m: m.text == "✔ Отметить")
def choose(m):
    if m.chat.id != CHAT_ID: return
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for i, task in enumerate(current_tasks()):
        if str(i) not in data['done_today']:
            markup.add(KeyboardButton(f"{i+1} — {task}"))
    markup.add(KeyboardButton("🔙 Назад"))
    bot.send_message(CHAT_ID, "Что выполнил?", reply_markup=markup)

# Обработчик done (без изменений, но с фиксом на повтор)
@bot.message_handler(func=lambda m: "—" in m.text)
def done(m):
    if m.chat.id != CHAT_ID: return
    try:
        idx = str(int(m.text.split()[0]) - 1)
        if idx in data['done_today']:
            bot.send_message(CHAT_ID, "Уже выполнено!", reply_markup=menu())
            return
        data['done_today'].append(idx)
        # Твоя прокачка XP и навыков здесь (как в v8.0)
        data['xp'] += 100  # Пример
        save()
        bot.send_message(CHAT_ID, "✓ Выполнено! +100 XP", reply_markup=menu())
    except:
        bot.send_message(CHAT_ID, "Ошибка, жми кнопки из списка", reply_markup=menu())

# === ЭКСТРА-ЗАДАНИЕ ===
@bot.message_handler(func=lambda m: m.text == "⚡ Экстра")
def extra(m):
    if m.chat.id != CHAT_ID: return
    if data['extra_done']:
        bot.send_message(CHAT_ID,"⚡ Экстра уже выполнено сегодня!")
        return
    task = data['extra_task']
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Выполнил экстра")
    markup.add("🔙 Назад")
    bot.send_message(CHAT_ID,f"⚡ ЭКСТРА-ЗАДАНИЕ (+200 XP)\n\n{task}",reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "Выполнил экстра")
def extra_done(m):
    if m.chat.id != CHAT_ID or data['extra_done']: return
    data['extra_done'] = True
    data['xp'] += 200
    data['agression'] += 2
    data['selfworth'] += 3
    data['anima'] += 2
    save()
    bot.send_message(CHAT_ID,"⚡ ЭКСТРА ВЫПОЛНЕНО!\n+200 XP | +2 Агрессия | +3 Самоценность | +2 Анима",reply_markup=menu())
    
# === НАКАЗАНИЕ 22:30 ===
def night_check():
    new_day()
    if len(data['done_today']) < len(current_tasks()):
        data['missed_days'] += 1
        penalty = 100 if data['missed_days']==1 else 200 if data['missed_days']==2 else 400
        data['xp'] = max(0,data['xp']-penalty)
        msg = f"🩸 НАКАЗАНИЕ -{penalty} XP\n"
        if data['missed_days']==1: msg += "30 отжиманий + 30 приседаний + 30 сек душа"
        elif data['missed_days']==2: msg += "40 отжиманий + 40 приседаний + 30 сек душа"
        else: msg += "50 отжиманий + 50 приседаний + 1 минута душа"
        bot.send_message(CHAT_ID,msg)
        if data['streak']>0: data['streak']=0
    else:
        data['missed_days']=0
        data['streak']+=1
        bot.send_message(CHAT_ID,f"✅ День пройден!\nСтрик: {data['streak']} 🔥")
    save()

# === РАСПИСАНИЕ ===
schedule.every().day.at("08:40").do(lambda: bot.send_message(CHAT_ID,"08:40 — Приседания"))
schedule.every().day.at("09:00").do(lambda: bot.send_message(CHAT_ID,"09:00 — Пресс"))
schedule.every().day.at("18:50").do(lambda: bot.send_message(CHAT_ID,"18:50 — Книга"))
schedule.every().day.at("21:00").do(lambda: bot.send_message(CHAT_ID,"21:00 — Дневник"))
schedule.every().day.at("22:30").do(night_check)

threading.Thread(target=lambda: [schedule.run_pending() or time.sleep(30) for _ in iter(int,1)], daemon=True).start()

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# ГЛОБАЛЬНЫЙ «НАЗАД» — работает ВЕЗДЕ
@bot.message_handler(func=lambda message: message.text == "🔙 Назад")
def global_back(message):
    if message.chat.id != CHAT_ID:
        return
    bot.send_message(CHAT_ID, "↩ Вернулся в главное меню", reply_markup=menu())
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

bot.infinity_polling()

