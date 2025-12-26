import sqlite3
import threading
import time
import json
from datetime import datetime

# Стандартные библиотеки
import requests
import urllib.parse

# Вставьте ваш токен здесь
TOKEN = '8579894302:AAF7OulzWAsT2i_XYI90FB0lRm-CltK1SNw'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}'

# Блокировка для потокобезопасности SQLite
db_lock = threading.Lock()

# База данных для избранного
class SimpleDatabase:
    def __init__(self):
        with db_lock:
            self.conn = sqlite3.connect('nolan_favorites.db', check_same_thread=False)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites 
                (user_id INTEGER, film_id TEXT, PRIMARY KEY (user_id, film_id))
            ''')
            self.conn.commit()
    
    def toggle_favorite(self, user_id, film_id):
        with db_lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM favorites WHERE user_id=? AND film_id=?", 
                          (user_id, film_id))
            if cursor.fetchone():
                cursor.execute("DELETE FROM favorites WHERE user_id=? AND film_id=?", 
                              (user_id, film_id))
                action = "removed"
            else:
                cursor.execute("INSERT INTO favorites VALUES (?, ?)", 
                              (user_id, film_id))
                action = "added"
            self.conn.commit()
            return action
    
    def get_favorites(self, user_id):
        with db_lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT film_id FROM favorites WHERE user_id=?", (user_id,))
            return [row[0] for row in cursor.fetchall()]

db = SimpleDatabase()

FILMS = {
    'inception': {
        'name': 'Начало (Inception)',
        'year': 2010,
        'genre': 'Научная фантастика, триллер',
        'duration': '148 мин',
        'rating': '8.8/10 IMDb',
        'desc': 'Криминальный триллер о проникновении в подсознание. Главный герой Дом Кобб — вор, который занимается кражей идей через сны.',
        'cast': 'Леонардо ДиКаприо, Джозеф Гордон-Левитт, Эллен Пейдж',
        'awards': '4 премии Оскар'
    },
    'interstellar': {
        'name': 'Интерстеллар (Interstellar)',
        'year': 2014,
        'genre': 'Научная фантастика, драма',
        'duration': '169 мин',
        'rating': '8.6/10 IMDb',
        'desc': 'Эпическая научно-фантастическая драма о путешествии через червоточину в поисках нового дома для человечества.',
        'cast': 'Мэттью Макконахи, Энн Хэтэуэй, Джессика Честейн',
        'awards': 'Оскар за лучшие визуальные эффекты'
    },
    'dark_knight': {
        'name': 'Темный рыцарь (The Dark Knight)',
        'year': 2008,
        'genre': 'Боевик, криминал, драма',
        'duration': '152 мин',
        'rating': '9.0/10 IMDb',
        'desc': 'Вторая часть трилогии о Бэтмене. Бэтмен сталкивается с Джокером — анархистом, стремящимся погрузить Готэм в хаос.',
        'cast': 'Кристиан Бэйл, Хит Леджер, Аарон Экхарт',
        'awards': '2 премии Оскар'
    },
    'prestige': {
        'name': 'Престиж (The Prestige)',
        'year': 2006,
        'genre': 'Драма, триллер, мистика',
        'duration': '130 мин',
        'rating': '8.5/10 IMDb',
        'desc': 'История соперничества двух иллюзионистов в викторианском Лондоне, которое приводит к трагическим последствиям.',
        'cast': 'Хью Джекман, Кристиан Бэйл, Майкл Кейн',
        'awards': 'Номинация на Оскар'
    },
    'dunkirk': {
        'name': 'Дюнкерк (Dunkirk)',
        'year': 2017,
        'genre': 'Военный, драма, история',
        'duration': '106 мин',
        'rating': '7.8/10 IMDb',
        'desc': 'Военная драма об эвакуации британских и союзных войск из Дюнкерка в 1940 году.',
        'cast': 'Финн Уайтхед, Том Харди, Килиан Мерфи',
        'awards': '3 премии Оскар'
    }
}

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f'https://api.telegram.org/bot{token}'
        self.offset = 0
        
    def send_message(self, chat_id, text, reply_markup=None):
        url = f'{self.base_url}/sendMessage'
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
            
        response = requests.post(url, json=data)
        return response.json()
    
    def edit_message_text(self, chat_id, message_id, text, reply_markup=None):
        url = f'{self.base_url}/editMessageText'
        data = {
            'chat_id': chat_id,
            'message_id': message_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        
        if reply_markup:
            data['reply_markup'] = json.dumps(reply_markup)
            
        response = requests.post(url, json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id, text=None):
        url = f'{self.base_url}/answerCallbackQuery'
        data = {
            'callback_query_id': callback_query_id
        }
        if text:
            data['text'] = text
            
        response = requests.post(url, json=data)
        return response.json()
    
    def get_updates(self):
        url = f'{self.base_url}/getUpdates'
        params = {'offset': self.offset, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json().get('result', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка получения обновлений: {e}")
        return []
    
    def process_updates(self, updates):
        for update in updates:
            self.offset = update['update_id'] + 1
            
            if 'message' in update:
                self.handle_message(update['message'])
            elif 'callback_query' in update:
                self.handle_callback_query(update['callback_query'])
    
    def handle_message(self, message):
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from'].get('first_name', 'Пользователь')
        
        if 'text' in message:
            text = message['text']
            
            if text == '/start' or text == '/start@your_bot_name':
                self.send_start(chat_id, user_name)
            elif text == '/help':
                self.send_help(chat_id)
            elif text == '/films':
                self.show_films(chat_id)
            elif text == '/fav':
                self.show_favorites(chat_id, user_id)
            elif text == '🎥 Список фильмов':
                self.show_films(chat_id)
            elif text == '⭐ Мое избранное':
                self.show_favorites(chat_id, user_id)
            elif text == '❓ Помощь':
                self.send_help(chat_id)
            else:
                self.send_message(chat_id, "Используйте команды или кнопки.")
    
    def handle_callback_query(self, callback_query):
        callback_id = callback_query['id']
        user_id = callback_query['from']['id']
        data = callback_query['data']
        message = callback_query['message']
        chat_id = message['chat']['id']
        message_id = message['message_id']
        
        try:
            if data.startswith("info_"):
                film_id = data.split("_")[1]
                self.show_film_info(chat_id, message_id, film_id, user_id)
            elif data.startswith("fav_"):
                film_id = data.split("_")[1]
                self.toggle_favorite(callback_id, chat_id, message_id, film_id, user_id)
            elif data == "back_to_list":
                self.back_to_list(chat_id, message_id)
        except Exception as e:
            print(f"Ошибка обработки callback: {e}")
            self.answer_callback_query(callback_id, "Ошибка при обработке")
    
    def send_start(self, chat_id, user_name):
        text = f"🎬 Привет, {user_name}!\n\nЭто бот с информацией о фильмах Кристофера Нолана.\n\nКоманды:\n/films - список фильмов\n/fav - избранное\n/help - помощь"
        
        reply_markup = {
            'keyboard': [
                [{'text': '🎥 Список фильмов'}, {'text': '⭐ Мое избранное'}],
                [{'text': '❓ Помощь'}]
            ],
            'resize_keyboard': True,
            'one_time_keyboard': False
        }
        
        self.send_message(chat_id, text, reply_markup)
    
    def send_help(self, chat_id):
        text = "🎥 Фильмы Кристофера Нолана\n\n"
        text += "Доступные команды:\n\n"
        text += "/start - начать работу\n"
        text += "/films - показать все фильмы\n"
        text += "/fav - показать избранные фильмы\n"
        text += "/help - эта справка\n\n"
        text += "Или используйте кнопки внизу экрана.\n\n"
        text += "Кристофер Нолан — британский режиссёр, известный сложными сюжетами и нелинейным повествованием."
        
        self.send_message(chat_id, text)
    
    def show_films(self, chat_id):
        keyboard = []
        for film_id, film in FILMS.items():
            keyboard.append([{
                'text': f"🎬 {film['name']} ({film['year']})",
                'callback_data': f"info_{film_id}"
            }])
        
        reply_markup = {
            'inline_keyboard': keyboard
        }
        
        self.send_message(chat_id, "🎥 Выберите фильм Кристофера Нолана:", reply_markup)
    
    def show_favorites(self, chat_id, user_id):
        favorites = db.get_favorites(user_id)
        
        if not favorites:
            self.send_message(chat_id, "⭐ У вас нет избранных фильмов.")
            return
        
        text = "⭐ Ваши избранные фильмы:\n"
        for film_id in favorites:
            film = FILMS.get(film_id)
            if film:
                text += f"\n🎬 {film['name']} ({film['year']})"
        
        self.send_message(chat_id, text)
    
    def show_film_info(self, chat_id, message_id, film_id, user_id):
        film = FILMS.get(film_id)
        if not film:
            self.edit_message_text(chat_id, message_id, "Фильм не найден")
            return
        
        favorites = db.get_favorites(user_id)
        
        text = f"🎬 <b>{film['name']}</b>\n"
        text += f"📅 Год: {film['year']}\n"
        text += f"🎭 Жанр: {film['genre']}\n"
        text += f"⏱ Длительность: {film['duration']}\n"
        text += f"⭐ Рейтинг: {film['rating']}\n"
        text += f"🏆 Награды: {film['awards']}\n"
        text += f"👥 Актерский состав:\n{film['cast']}\n\n"
        text += f"📝 Описание:\n{film['desc']}"
        
        keyboard = []
        
        if film_id in favorites:
            keyboard.append([{
                'text': "❌ Убрать из избранного",
                'callback_data': f"fav_{film_id}"
            }])
        else:
            keyboard.append([{
                'text': "⭐ Добавить в избранное",
                'callback_data': f"fav_{film_id}"
            }])
        
        keyboard.append([{
            'text': "🔙 Назад к списку",
            'callback_data': "back_to_list"
        }])
        
        reply_markup = {
            'inline_keyboard': keyboard
        }
        
        self.edit_message_text(chat_id, message_id, text, reply_markup)
    
    def toggle_favorite(self, callback_id, chat_id, message_id, film_id, user_id):
        try:
            action = db.toggle_favorite(user_id, film_id)
            film = FILMS.get(film_id)
            film_name = film['name'] if film else "Фильм"
            
            if action == "added":
                self.answer_callback_query(callback_id, f"⭐ {film_name} добавлен в избранное")
            else:
                self.answer_callback_query(callback_id, f"❌ {film_name} удален из избранного")
            
            self.show_film_info(chat_id, message_id, film_id, user_id)
        except Exception as e:
            print(f"Ошибка в toggle_favorite: {e}")
            self.answer_callback_query(callback_id, "Ошибка при обновлении избранного")
    
    def back_to_list(self, chat_id, message_id):
        keyboard = []
        for film_id, film in FILMS.items():
            keyboard.append([{
                'text': f"🎬 {film['name']} ({film['year']})",
                'callback_data': f"info_{film_id}"
            }])
        
        reply_markup = {
            'inline_keyboard': keyboard
        }
        
        self.edit_message_text(
            chat_id,
            message_id,
            "🎥 Выберите фильм Кристофера Нолана:",
            reply_markup
        )
    
    def run(self):
        print("🎬 Бот с фильмами Кристофера Нолана запущен. Нажмите Ctrl+C для остановки.")
        
        while True:
            try:
                updates = self.get_updates()
                if updates:
                    self.process_updates(updates)
                time.sleep(0.5)
            except KeyboardInterrupt:
                print("\n📴 Бот остановлен")
                break
            except Exception as e:
                print(f"Ошибка в основном цикле: {e}")
                time.sleep(5)

# Запуск бота
if __name__ == "__main__":
    bot = TelegramBot(TOKEN)
    bot.run()