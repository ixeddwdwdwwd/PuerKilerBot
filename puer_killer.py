import telebot, json, os, time, datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = '8365097962:AAFeogaH2yndWe05GB947y-tA7yyebhCej8'

bot = telebot.TeleBot(TOKEN)

# ----------------- ДАННЫЕ -----------------
DATA_FILE = 'data.json'
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {
        'xp': 0, 'level': 0, 'body': 8, 'disc': 5, 'border': 3,
        'day': 0, 'streak': 0, 'done_today': [], 'last_date': None
    }

tasks = ["Пресс","Приседания","Пыль/быт","Книга 10+ стр","«Нет» без объяснений"]

# Уровни: XP нужно для перехода (можно менять)
LEVEL_XP = [
    0, 500, 1100, 1800, 2600, 3500, 4500, 5600, 6800, 8100,   # 1–10
    9500, 11000, 12600, 14300, 16100, 18000, 20000, 22100, 24300, 26600,  # 11–20
    29000, 31500, 34100, 36800, 39600, 42500, 45500, 48600, 51800, 55100  # 21–30
]

def get_needed_xp(level):
    return LEVEL_XP[level] if level < len(LEVEL_XP) else LEVEL_XP[-1] + (level-30)*4000

def save():
    data['last_date'] = datetime.date.today().isoformat()
    with open(DATA_FILE,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

# ----------------- МЕНЮ -----------------
def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    m.add("📊 Статы","✅ Задания","✔ Отметить","❌ Наказание")
    return m

# ----------------- ПРОВЕРКА ДНЯ -----------------
def is_new_day():
    today = datetime.date.today().isoformat()
    if data['last_date'] != today:
        data['done_today'] = []
        data['day'] += 1
        save()
        return True
    return False

# ----------------- СТАРТ -----------------
@bot.message_handler(commands=['start'])
def start(m):
    is_new_day()
    bot.send_message(m.chat.id,
        "🔥 Смерть Вечного Мальчика — пошла!\n"
        "Ты — Никита. Цель — уровень 30 = КОРОЛЬ\n"
        "Один день = одна пачка заданий", reply_markup=menu())

# ----------------- СТАТЫ -----------------
@bot.message_handler(func=lambda m: m.text == "📊 Статы")
def stats(m):
    is_new_day()
    bar = lambda x: "█"*(min(x//10,10)) + "░"*(10-min(x//10,10))
    need = get_needed_xp(data['level']+1)
    bot.send_message(m.chat.id, f"""
👤 Никита | Уровень {data['level']} → {data['level']+1}
💛 XP: {data['xp']} / {need}

📊 Тело       {bar(data['body'])} {data['body']}/100
📊 Дисциплина {bar(data['disc'])} {data['disc']}/100
📊 Границы    {bar(data['border'])} {data['border']}/100

🔥 Стрик: {data['streak']} дней | День игры: {data['day']}
🏆 До Короля осталось: {30 - data['level']} уровней
    """)

# ----------------- ЗАДАНИЯ -----------------
@bot.message_handler(func=lambda m: m.text == "✅ Задания")
def tasks_list(m):
    is_new_day()
    t = f"🔥 День {data['day']} — {datetime.date.today()}\n\n"
    for i,task in enumerate(tasks):
        mark = "✓" if str(i) in data['done_today'] else "⬜"
        t += f"{mark} {i+1}. {task}\n"
    bot.send_message(m.chat.id,t)

# ----------------- ОТМЕТИТЬ -----------------
@bot.message_handler(func=lambda m: m.text == "✔ Отметить")
def choose(m):
    is_new_day()
    if len(data['done_today']) == 5:
        bot.send_message(m.chat.id,"✅ Сегодня ты уже всё сделал! Отдыхай, воин.")
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    for i,task in enumerate(tasks):
        if str(i) not in data['done_today']:
            markup.add(KeyboardButton(f"{i+1} — {task}"))
    markup.add(KeyboardButton("🔙 Меню"))
    bot.send_message(m.chat.id,"Что выполнил?",reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and "—" in m.text)
def done(m):
    try:
        idx = str(int(m.text.split()[0]) - 1)
        if len(data['done_today']) == 5:
            bot.send_message(m.chat.id,"Ты уже прошёл день!",reply_markup=menu())
            return
        if idx not in data['done_today']:
            data['done_today'].append(idx)
            if idx in ['0','1']: data['body'] += 8
            if idx in ['2','3']: data['disc'] += 10
            if idx == '4': data['border'] += 15
            data['xp'] += 100 if idx=='4' else 50
            save()

            if len(data['done_today']) == 5:
                data['xp'] += 200  # бонус за день
                data['streak'] += 1
                old_level = data['level']
                data['level'] = next((i for i, v in enumerate(LEVEL_XP) if data['xp'] < v), len(LEVEL_XP)-1)
                save()
                if data['level'] >= 30:
                    bot.send_message(m.chat.id,
                        "🎉🎉🎉 ТЫ СТАЛ КОРОЛЁМ! 🎉🎉🎉\n"
                        "Puer aeternus мёртв. Ты — мужчина.\n"
                        "Фанфары!", reply_markup=menu())
                    bot.send_voice(m.chat.id, open('fanfare.ogg', 'rb'))  # можно добавить файл
                elif data['level'] > old_level:
                    bot.send_message(m.chat.id,f"🌟 УРОВЕНЬ {data['level']} ДОСТИГНУТ! 🌟\n+200 XP бонус!",reply_markup=menu())
                else:
                    bot.send_message(m.chat.id,"🎉 День пройден! Завтра новый бой!",reply_markup=menu())
            else:
                bot.send_message(m.chat.id,f"✓ {tasks[int(idx)]} — сделано!",reply_markup=menu())
    except:
        pass

@bot.message_handler(func=lambda m: m.text == "❌ Наказание")
def punish(m):
    bot.send_message(m.chat.id,"🩸 50 отжиманий + 5 мин холодного душа + спать 22:00")

@bot.message_handler(func=lambda m: m.text == "🔙 Меню")
def back(m):
    bot.send_message(m.chat.id,"Меню",reply_markup=menu())

bot.infinity_polling()

