import telebot
from telebot import types
import json
import os
import re
from datetime import datetime, date, timedelta

TOKEN = "8515155487:AAFnxhuO-7Pa_b0TTmVmCswvXYRRJufvxm4"
bot = telebot.TeleBot(TOKEN)

# Файлы для данных
USER_FILE = "users.json"
HEALTH_FILE = "health.json"

# Загрузка и сохранение
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# База рецептов
recipes_db = {
    "завтрак": [
        {"name": "Овсянка с фруктами", "calories": 250, "time": "10 мин", "ingredients": ["овсянка", "банан", "ягоды", "мед"]},
        {"name": "Омлет с овощами", "calories": 300, "time": "15 мин", "ingredients": ["яйца", "помидоры", "перец", "зелень"]},
        {"name": "Смузи-боул", "calories": 280, "time": "5 мин", "ingredients": ["банан", "шпинат", "йогурт", "семена чиа"]}
    ],
    "обед": [
        {"name": "Куриный салат", "calories": 350, "time": "20 мин", "ingredients": ["курица", "салат", "помидоры", "огурцы", "масло"]},
        {"name": "Гречка с овощами", "calories": 280, "time": "25 мин", "ingredients": ["гречка", "морковь", "лук", "грибы"]},
        {"name": "Суп-пюре из брокколи", "calories": 200, "time": "30 мин", "ingredients": ["брокколи", "картофель", "лук", "сливки"]}
    ],
    "ужин": [
        {"name": "Запеченная рыба", "calories": 220, "time": "30 мин", "ingredients": ["рыба", "лимон", "специи", "овощи"]},
        {"name": "Творожная запеканка", "calories": 200, "time": "40 мин", "ingredients": ["творог", "яйца", "изюм", "ваниль"]},
        {"name": "Овощное рагу", "calories": 180, "time": "35 мин", "ingredients": ["кабачки", "баклажаны", "перцы", "томаты"]}
    ],
    "перекус": [
        {"name": "Яблоко с арахисовой пастой", "calories": 150, "time": "2 мин", "ingredients": ["яблоко", "арахисовая паста"]},
        {"name": "Йогурт с орехами", "calories": 200, "time": "2 мин", "ingredients": ["греческий йогурт", "орехи", "мед"]},
        {"name": "Протеиновые батончики", "calories": 180, "time": "15 мин", "ingredients": ["овсянка", "протеин", "финики", "орехи"]}
    ]
}

# ==================== ГЛАВНОЕ МЕНЮ ====================
@bot.message_handler(commands=['start', 'help'])
def start_bot(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("📋 Мой профиль", "💪 Здоровье")
    keyboard.row("🍽 Рецепты", "📊 Статистика")
    keyboard.row("🆘 Помощь")
    
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в бот 'Здоровый образ жизни'!\n\n"
        "Я помогу вам:\n"
        "• Следить за здоровьем\n"
        "• Отслеживать питание\n"
        "• Готовить полезные блюда\n\n"
        "Выберите раздел:",
        reply_markup=keyboard
    )

# ==================== РЕГИСТРАЦИЯ ====================
@bot.message_handler(commands=['reg'])
def start_registration(message):
    bot.send_message(message.chat.id, "Как вас зовут?")
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    if user_id not in users:
        users[user_id] = {}
    
    users[user_id]['name'] = message.text
    save_data(USER_FILE, users)
    
    bot.send_message(message.chat.id, "Сколько вам лет?")
    bot.register_next_step_handler(message, save_age)

def save_age(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    if message.text.isdigit():
        users[user_id]['age'] = int(message.text)
        save_data(USER_FILE, users)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.row("Похудение", "Поддержание формы")
        keyboard.row("Набор массы", "Здоровое питание")
        
        bot.send_message(message.chat.id, "Какая ваша цель?", reply_markup=keyboard)
        bot.register_next_step_handler(message, save_goal)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите возраст цифрами:")
        bot.register_next_step_handler(message, save_age)

def save_goal(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    users[user_id]['goal'] = message.text
    save_data(USER_FILE, users)
    
    bot.send_message(message.chat.id, "Какой ваш рост в см?")
    bot.register_next_step_handler(message, save_height)

def save_height(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    if message.text.isdigit():
        users[user_id]['height'] = int(message.text)
        save_data(USER_FILE, users)
        
        bot.send_message(message.chat.id, "Какой ваш вес в кг?")
        bot.register_next_step_handler(message, save_weight)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите рост цифрами:")
        bot.register_next_step_handler(message, save_height)

def save_weight(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    try:
        weight = float(message.text.replace(',', '.'))
        users[user_id]['weight'] = weight
        users[user_id]['reg_date'] = str(date.today())
        
        # Расчет ИМТ
        if 'height' in users[user_id]:
            height_m = users[user_id]['height'] / 100
            bmi = weight / (height_m ** 2)
            users[user_id]['bmi'] = round(bmi, 1)
            
            if bmi < 18.5:
                bmi_status = "недостаточный вес"
            elif 18.5 <= bmi < 25:
                bmi_status = "нормальный вес"
            elif 25 <= bmi < 30:
                bmi_status = "избыточный вес"
            else:
                bmi_status = "ожирение"
            users[user_id]['bmi_status'] = bmi_status
        
        save_data(USER_FILE, users)
        
        response = f"✅ Регистрация завершена!\n\n"
        response += f"Имя: {users[user_id].get('name', 'не указано')}\n"
        response += f"Возраст: {users[user_id].get('age', 'не указан')}\n"
        response += f"Цель: {users[user_id].get('goal', 'не указана')}\n"
        response += f"Рост: {users[user_id].get('height', 'не указан')} см\n"
        response += f"Вес: {users[user_id].get('weight', 'не указан')} кг\n"
        
        if 'bmi' in users[user_id]:
            response += f"ИМТ: {users[user_id]['bmi']} ({users[user_id]['bmi_status']})\n"
        
        bot.send_message(message.chat.id, response)
        
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите вес цифрами (например: 68.5):")
        bot.register_next_step_handler(message, save_weight)

# ==================== ОБРАБОТКА ВСЕХ СООБЩЕНИЙ ====================
@bot.message_handler(content_types=['text'])
def handle_all_messages(message):
    text = message.text.lower().strip()
    
    # Проверка "назад"
    if any(word in text for word in ["назад", "выйти", "вернуться", "🔙", "на главную"]):
        start_bot(message)
        return
    
    # Проверка категорий рецептов
    if text in ["завтрак", "обед", "ужин", "перекус", "диетические", "быстрые"]:
        show_recipes_category(message)
        return
    
    # Проверка подменю здоровья
    if text in ["💧 вода", "вода", "💧"]:
        log_water(message)
        return
    elif text in ["⚖️ вес", "вес", "⚖️"]:
        log_weight(message)
        return
    elif text in ["📅 сон", "сон", "📅"]:
        log_sleep(message)
        return
    elif text in ["🏃 активность", "активность", "🏃"]:
        log_activity(message)
        return
    
    # Основные команды
    if any(word in text for word in ["профиль", "мой профиль", "📋"]):
        show_profile(message)
    elif any(word in text for word in ["здоровье", "здоров", "💪"]):
        health_menu(message)
    elif any(word in text for word in ["рецепт", "рецепты", "🍽", "еда", "кухня"]):
        recipes_menu(message)
    elif any(word in text for word in ["статистик", "статистика", "📊", "отчет"]):
        show_statistics(message)
    elif any(word in text for word in ["помощь", "🆘", "справка", "help"]):
        show_help(message)
    elif any(word in text for word in ["привет", "начать", "старт", "hello"]):
        start_bot(message)
    else:
        bot.send_message(message.chat.id, "Не понял команду. Напишите 'помощь' или используйте кнопки.")

# ==================== ПРОФИЛЬ ====================
def show_profile(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    
    if user_id in users:
        user = users[user_id]
        response = "📋 ВАШ ПРОФИЛЬ\n\n"
        response += f"Имя: {user.get('name', 'не указано')}\n"
        response += f"Возраст: {user.get('age', 'не указан')}\n"
        response += f"Цель: {user.get('goal', 'не указана')}\n"
        response += f"Рост: {user.get('height', 'не указан')} см\n"
        response += f"Вес: {user.get('weight', 'не указан')} кг\n"
        
        if 'bmi' in user:
            response += f"ИМТ: {user['bmi']} ({user.get('bmi_status', '')})\n"
        
        if 'reg_date' in user:
            response += f"\nДата регистрации: {user['reg_date']}"
    else:
        response = "Профиль не найден. Используйте /reg для регистрации."
    
    bot.send_message(message.chat.id, response)

# ==================== ЗДОРОВЬЕ ====================
def health_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("💧 Вода", "⚖️ Вес")
    keyboard.row("📅 Сон", "🏃 Активность")
    keyboard.row("🔙 Назад")
    
    bot.send_message(
        message.chat.id,
        "💪 РАЗДЕЛ ЗДОРОВЬЯ\n\n"
        "Что хотите зафиксировать?",
        reply_markup=keyboard
    )

# --- ВОДА ---
def log_water(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("200 мл", "300 мл", "500 мл")
    keyboard.row("750 мл", "1 литр", "1.5 литра")
    keyboard.row("Другое количество", "🔙 Назад")
    
    bot.send_message(
        message.chat.id,
        "💧 СКОЛЬКО ВОДЫ ВЫ ВЫПИЛИ?\n\n"
        "Выберите из списка или введите своё количество:",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, save_water)

def save_water(message):
    text = message.text.lower().strip()
    
    # Проверка "назад" в середине диалога
    if any(word in text for word in ["назад", "🔙", "отмена", "cancel"]):
        health_menu(message)
        return
    
    try:
        # Определяем количество
        amount = 0
        
        if text == "другое количество":
            bot.send_message(message.chat.id, "Введите количество в мл (например: 250):")
            bot.register_next_step_handler(message, save_custom_water)
            return
        elif "200" in text:
            amount = 200
        elif "300" in text:
            amount = 300
        elif "500" in text:
            amount = 500
        elif "750" in text:
            amount = 750
        elif any(word in text for word in ["1 литр", "1л", "1л.", "1000", "1 лит", "1литр"]):
            amount = 1000
        elif any(word in text for word in ["1.5", "1,5", "1.5 литра", "1500"]):
            amount = 1500
        else:
            # Пробуем извлечь число из текста
            nums = re.findall(r'\d+', text)
            if nums:
                amount = int(nums[0])
            else:
                bot.send_message(message.chat.id, "Не понял количество. Введите цифрами (например: 250):")
                bot.register_next_step_handler(message, save_water)
                return
        
        user_id = str(message.from_user.id)
        today = str(date.today())
        health_data = load_data(HEALTH_FILE)
        
        if today not in health_data:
            health_data[today] = {}
        if user_id not in health_data[today]:
            health_data[today][user_id] = {
                "water": 0, 
                "weight_logs": [],
                "sleep": None,
                "activity": None
            }
        
        health_data[today][user_id]["water"] = health_data[today][user_id].get("water", 0) + amount
        save_data(HEALTH_FILE, health_data)
        
        total = health_data[today][user_id]["water"]
        
        # Рекомендация по воде (30 мл на 1 кг веса)
        users = load_data(USER_FILE)
        recommended = 2000  # стандартная норма
        
        if user_id in users and 'weight' in users[user_id]:
            recommended = users[user_id]['weight'] * 30
        
        progress = min((total / recommended) * 100, 100)
        
        response = f"✅ Записано: {amount} мл\n"
        response += f"📊 Всего сегодня: {total} мл\n"
        response += f"🎯 Прогресс: {progress:.0f}% от нормы ({recommended:.0f} мл)"
        
        bot.send_message(message.chat.id, response)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}\nПопробуйте еще раз.")
        log_water(message)

def save_custom_water(message):
    text = message.text.strip()
    
    if any(word in text.lower() for word in ["назад", "🔙", "отмена"]):
        log_water(message)
        return
    
    try:
        amount = int(text)
        if amount <= 0 or amount > 5000:
            bot.send_message(message.chat.id, "Введите разумное количество (1-5000 мл):")
            bot.register_next_step_handler(message, save_custom_water)
            return
        
        # Создаем фейковое сообщение с нужным текстом
        message.text = f"{amount} мл"
        save_water(message)
        
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите количество цифрами:")
        bot.register_next_step_handler(message, save_custom_water)

# --- ВЕС ---
def log_weight(message):
    bot.send_message(
        message.chat.id,
        "⚖️ ВВЕДИТЕ ВАШ ТЕКУЩИЙ ВЕС В КГ:\n"
        "(например: 68.5 или 70)\n\n"
        "Или напишите 'назад' для возврата",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, save_weight_log)

def save_weight_log(message):
    text = message.text.lower().strip()
    
    if any(word in text for word in ["назад", "🔙", "отмена"]):
        health_menu(message)
        return
    
    try:
        weight = float(text.replace(',', '.'))
        
        if weight < 20 or weight > 300:
            bot.send_message(message.chat.id, "Введите реалистичный вес (20-300 кг):")
            bot.register_next_step_handler(message, save_weight_log)
            return
            
        user_id = str(message.from_user.id)
        today = str(date.today())
        health_data = load_data(HEALTH_FILE)
        
        if today not in health_data:
            health_data[today] = {}
        if user_id not in health_data[today]:
            health_data[today][user_id] = {
                "water": 0, 
                "weight_logs": [],
                "sleep": None,
                "activity": None
            }
        
        health_data[today][user_id]["weight_logs"].append({
            "date": today,
            "weight": weight,
            "time": datetime.now().strftime("%H:%M")
        })
        
        # Обновляем основной вес в профиле
        users = load_data(USER_FILE)
        if user_id in users:
            old_weight = users[user_id].get('weight', weight)
            users[user_id]['weight'] = weight
            
            # Расчет изменения
            difference = weight - old_weight
            if difference > 0:
                diff_text = f"+{difference:.1f} кг"
            elif difference < 0:
                diff_text = f"{difference:.1f} кг"
            else:
                diff_text = "без изменений"
            
            save_data(USER_FILE, users)
            
            response = f"✅ Вес сохранен: {weight} кг\n"
            response += f"📈 Изменение: {diff_text}"
        else:
            response = f"✅ Вес сохранен: {weight} кг"
        
        save_data(HEALTH_FILE, health_data)
        bot.send_message(message.chat.id, response)
        
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите вес цифрами (например: 68.5):")
        bot.register_next_step_handler(message, save_weight_log)

# --- СОН ---
def log_sleep(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("4-5 часов", "6-7 часов", "8-9 часов")
    keyboard.row("Меньше 4 часов", "Больше 9 часов")
    keyboard.row("🔙 Назад")
    
    bot.send_message(
        message.chat.id,
        "📅 СКОЛЬКО ВЫ СПАЛИ СЕГОДНЯ НОЧЬЮ?\n\n"
        "Выберите из вариантов:",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, save_sleep)

def save_sleep(message):
    text = message.text.lower().strip()
    
    if any(word in text for word in ["назад", "🔙", "отмена"]):
        health_menu(message)
        return
    
    # Определяем количество сна
    sleep_hours = None
    
    if "4-5" in text or "4 5" in text:
        sleep_hours = "4-5 часов"
        sleep_quality = "мало"
    elif "6-7" in text or "6 7" in text:
        sleep_hours = "6-7 часов"
        sleep_quality = "нормально"
    elif "8-9" in text or "8 9" in text:
        sleep_hours = "8-9 часов"
        sleep_quality = "отлично"
    elif "меньше" in text or "<4" in text:
        sleep_hours = "менее 4 часов"
        sleep_quality = "очень мало"
    elif "больше" in text or ">9" in text:
        sleep_hours = "более 9 часов"
        sleep_quality = "много"
    else:
        # Пробуем извлечь число
        nums = re.findall(r'\d+', text)
        if nums:
            hours = int(nums[0])
            if hours < 4:
                sleep_hours = f"{hours} часа"
                sleep_quality = "очень мало"
            elif 4 <= hours <= 5:
                sleep_hours = f"{hours} часов"
                sleep_quality = "мало"
            elif 6 <= hours <= 7:
                sleep_hours = f"{hours} часов"
                sleep_quality = "нормально"
            elif 8 <= hours <= 9:
                sleep_hours = f"{hours} часов"
                sleep_quality = "отлично"
            else:
                sleep_hours = f"{hours} часов"
                sleep_quality = "много"
        else:
            bot.send_message(message.chat.id, "Не понял. Выберите вариант из списка или укажите количество часов:")
            bot.register_next_step_handler(message, save_sleep)
            return
    
    user_id = str(message.from_user.id)
    today = str(date.today())
    health_data = load_data(HEALTH_FILE)
    
    if today not in health_data:
        health_data[today] = {}
    if user_id not in health_data[today]:
        health_data[today][user_id] = {
            "water": 0, 
            "weight_logs": [],
            "sleep": None,
            "activity": None
        }
    
    health_data[today][user_id]["sleep"] = {
        "hours": sleep_hours,
        "quality": sleep_quality,
        "date": today
    }
    
    save_data(HEALTH_FILE, health_data)
    
    response = f"✅ Сон записан!\n\n"
    response += f"Продолжительность: {sleep_hours}\n"
    response += f"Качество: {sleep_quality}"
    
    # Добавляем рекомендацию
    if sleep_quality in ["очень мало", "мало"]:
        response += "\n\n💡 Совет: Старайтесь спать 7-8 часов для лучшего самочувствия!"
    elif sleep_quality == "отлично":
        response += "\n\n🎉 Отлично! Продолжайте в том же духе!"
    
    bot.send_message(message.chat.id, response)

# --- АКТИВНОСТЬ ---
def log_activity(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Низкая", "Средняя", "Высокая")
    keyboard.row("Тренировка", "Прогулка")
    keyboard.row("🔙 Назад")
    
    bot.send_message(
        message.chat.id,
        "🏃 КАКОВА ВАША АКТИВНОСТЬ СЕГОДНЯ?\n\n"
        "Выберите уровень или тип активности:",
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, save_activity)

def save_activity(message):
    text = message.text.lower().strip()
    
    if any(word in text for word in ["назад", "🔙", "отмена"]):
        health_menu(message)
        return
    
    activity_text = message.text
    activity_level = ""
    
    if "низк" in text:
        activity_level = "низкая"
    elif "средн" in text:
        activity_level = "средняя"
    elif "высок" in text:
        activity_level = "высокая"
    elif "тренировк" in text:
        activity_level = "тренировка"
    elif "прогулк" in text or "ходьб" in text:
        activity_level = "прогулка"
    else:
        activity_level = text
    
    user_id = str(message.from_user.id)
    today = str(date.today())
    health_data = load_data(HEALTH_FILE)
    
    if today not in health_data:
        health_data[today] = {}
    if user_id not in health_data[today]:
        health_data[today][user_id] = {
            "water": 0, 
            "weight_logs": [],
            "sleep": None,
            "activity": None
        }
    
    health_data[today][user_id]["activity"] = {
        "type": activity_level,
        "date": today
    }
    
    save_data(HEALTH_FILE, health_data)
    
    response = f"✅ Активность записана!\n\n"
    response += f"Тип: {activity_text}\n"
    
    if activity_level in ["низкая", "средняя"]:
        response += "\n💡 Совет: Попробуйте добавить 30-минутную прогулку!"
    elif activity_level in ["высокая", "тренировка"]:
        response += "\n🎉 Отлично! Не забывайте про отдых и восстановление!"
    
    bot.send_message(message.chat.id, response)

# ==================== РЕЦЕПТЫ ====================
def recipes_menu(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("Завтрак", "Обед", "Ужин")
    keyboard.row("Перекус", "Диетические", "Быстрые")
    keyboard.row("🔙 Назад")
    
    bot.send_message(
        message.chat.id,
        "🍽 КУЛИНАРНЫЙ РАЗДЕЛ\n\n"
        "Выберите категорию рецептов:",
        reply_markup=keyboard
    )

def show_recipes_category(message):
    text = message.text.lower().strip()
    
    if any(word in text for word in ["назад", "🔙", "отмена"]):
        recipes_menu(message)
        return
    
    if text in recipes_db:
        recipes_list = recipes_db[text]
        response = f"📋 РЕЦЕПТЫ: {message.text.upper()}\n\n"
        
        for i, recipe in enumerate(recipes_list, 1):
            response += f"{i}. {recipe['name']}\n"
            response += f"   🔥 {recipe['calories']} ккал | ⏱ {recipe['time']}\n"
            response += f"   🥕 {', '.join(recipe['ingredients'][:3])}"
            if len(recipe['ingredients']) > 3:
                response += "..."
            response += "\n\n"
        
        bot.send_message(message.chat.id, response)
    elif text == "диетические":
        low_cal_recipes = []
        for cat in recipes_db:
            for recipe in recipes_db[cat]:
                if recipe['calories'] < 250:
                    low_cal_recipes.append(f"{recipe['name']} ({recipe['calories']} ккал)")
        
        response = "🥗 ДИЕТИЧЕСКИЕ РЕЦЕПТЫ (<250 ккал)\n\n"
        for i, recipe in enumerate(low_cal_recipes[:6], 1):
            response += f"{i}. {recipe}\n"
        bot.send_message(message.chat.id, response)
    elif text == "быстрые":
        fast_recipes = []
        for cat in recipes_db:
            for recipe in recipes_db[cat]:
                time_str = recipe['time'].replace(' мин', '')
                if time_str.isdigit() and int(time_str) <= 15:
                    fast_recipes.append(f"{recipe['name']} - {recipe['time']}")
        
        response = "⚡ БЫСТРЫЕ РЕЦЕПТЫ (до 15 мин)\n\n"
        for i, recipe in enumerate(fast_recipes[:6], 1):
            response += f"{i}. {recipe}\n"
        bot.send_message(message.chat.id, response)

# ==================== СТАТИСТИКА ====================
def show_statistics(message):
    user_id = str(message.from_user.id)
    users = load_data(USER_FILE)
    health_data = load_data(HEALTH_FILE)
    today = str(date.today())
    
    response = "📊 ВАША СТАТИСТИКА\n\n"
    
    if user_id in users:
        user = users[user_id]
        response += f"👤 ПРОФИЛЬ:\n"
        response += f"   Имя: {user.get('name', 'не указано')}\n"
        response += f"   Цель: {user.get('goal', 'не указана')}\n"
        
        if 'bmi' in user:
            response += f"   ИМТ: {user['bmi']} ({user.get('bmi_status', '')})\n"
    
    if today in health_data and user_id in health_data[today]:
        today_data = health_data[today][user_id]
        response += f"\n📅 СЕГОДНЯ ({today}):\n"
        response += f"   💧 Вода: {today_data.get('water', 0)} мл\n"
        
        if 'weight_logs' in today_data and today_data['weight_logs']:
            last_weight = today_data['weight_logs'][-1]['weight']
            response += f"   ⚖️ Вес: {last_weight} кг\n"
        
        if 'sleep' in today_data and today_data['sleep']:
            response += f"   📅 Сон: {today_data['sleep'].get('hours', 'не указано')} ({today_data['sleep'].get('quality', '')})\n"
        
        if 'activity' in today_data and today_data['activity']:
            response += f"   🏃 Активность: {today_data['activity'].get('type', 'не указана')}\n"
    
    # Общие данные за неделю
    week_water = 0
    week_days = 0
    week_sleep_days = 0
    week_activity_days = 0
    
    for date_key in list(health_data.keys())[-7:]:  # Последние 7 дней
        if user_id in health_data[date_key]:
            week_water += health_data[date_key][user_id].get('water', 0)
            week_days += 1
            
            if health_data[date_key][user_id].get('sleep'):
                week_sleep_days += 1
            if health_data[date_key][user_id].get('activity'):
                week_activity_days += 1
    
    if week_days > 0:
        avg_water = week_water / week_days
        response += f"\n📈 ЗА ПОСЛЕДНЮЮ НЕДЕЛЮ:\n"
        response += f"   💧 Средняя вода в день: {avg_water:.0f} мл\n"
        response += f"   📅 Дней с записями: {week_days}\n"
        response += f"   😴 Дней со сном: {week_sleep_days}\n"
        response += f"   🏃 Дней с активностью: {week_activity_days}\n"
    
    bot.send_message(message.chat.id, response)

# ==================== ПОМОЩЬ ====================
def show_help(message):
    help_text = """
🆘 ПОМОЩЬ ПО БОТУ

ОСНОВНЫЕ КОМАНДЫ:
/start - Главное меню
/reg - Регистрация профиля
/help - Эта справка

РАЗДЕЛЫ БОТА:
📋 Мой профиль - Ваши данные и цели
💪 Здоровье - Трекер воды, веса, сна, активности
🍽 Рецепты - Полезные рецепты по категориям
📊 Статистика - Ваш прогресс и результаты

КАК РАБОТАЕТ "НАЗАД":
• Напишите "назад", "выйти" или "🔙"
• Или нажмите кнопку "🔙 Назад"
• В любое время вернётесь в предыдущее меню

ДОСТУПНЫЕ КОМАНДЫ:
• "вода" - записать выпитую воду
• "вес" - записать текущий вес
• "сон" - записать продолжительность сна
• "активность" - записать физическую активность
• "рецепты" - показать кулинарный раздел
• "статистика" - показать ваш прогресс

СОВЕТЫ:
1. Сначала зарегистрируйтесь командой /reg
2. Ежедневно отмечайте воду, сон и активность
3. Раз в неделю фиксируйте вес
4. Используйте рецепты для здорового питания

Для консультации с диетологом обратитесь к специалисту!
"""
    bot.send_message(message.chat.id, help_text)

# ==================== ЗАПУСК БОТА ====================
if __name__ == "__main__":
    print("=" * 50)
    print("БОТ 'ЗДОРОВЫЙ ОБРАЗ ЖИЗНИ' ЗАПУЩЕН")
    print("=" * 50)
    print("Ожидание сообщений...")
    print("Для выхода нажмите Ctrl+C")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Перезапуск через 5 секунд...")
        import time
        time.sleep(5)
        bot.polling(none_stop=True, interval=0)