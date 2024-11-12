import json
import requests
import random
from os import getenv
from dotenv import load_dotenv

# Токен спрятан в виртуальное окружение
# load_dotenv()
# TOKEN = getenv('TOKEN_BOT')
# if getenv("HEROKU") is None:
#     load_dotenv()

TOKEN = getenv('TOKEN_BOT')
# print("Token:", TOKEN)
URL = f'https://api.telegram.org/bot{TOKEN}/'
# print(URL)

# Списки слов для игры на русском и английском, в перспективе можно подтягивать из файла (в том числе разграничить по темам)
words_en = ['orange', 'lemon', 'coconut', 'pineapple', 'mango', 'peach', 'pomegranate',
            'neighbor', 'evil', 'resident', 'chest', 'sport', 'psychology', 'couch', 'influence',
            'television', 'time', 'food', 'edge', 'care', 'complex',
            'regret', 'epoch', 'translation', 'friend',
            'museum', 'call', 'couch', 'background', 'prince',
            'price', 'union', 'citizen', 'shoulder',
            'interaction', 'matter', 'doctor', 'car',
            'receipt', 'factory', 'dignity', 'guilt', 'club',
            'degree', 'russian', 'snow', 'skin', 'management',
            'channel', 'essence', 'meeting', 'conduct', 'engine',
            'course', 'construction', 'memory', 'system', 'material', 'club',
            'depth', 'complex', 'topic', 'edition', 'state', 'crisis',
            'front', 'limit', 'composition', 'position', 'summer house', 'translation',
            'medicine', 'professor', 'worker', 'witness', 'district',
            'rule', 'processing', 'engineer', 'check', 'bag',
            'detail', 'recognition', 'detail', 'bag', 'case', 'economy',
            'size', 'data', 'word', 'marriage', 'presence', 'peace',
            'dignity', 'country', 'captain', 'expert', 'quality',
            'chairman', 'check', 'industry', 'tax',
            'apartment', 'reason', 'provision', 'program', 'lieutenant']


words_ru = ['апельсин', 'лимон', 'кокос', 'ананас', 'манго', 'персик', 'гранат', 
            'сосед', 'зло', 'житель', 'грудь', 'спорт', 'психология', 'диван', 'влияние',
            'телевизор', 'пора', 'еда', 'край', 'забота', 'комплекс', 
            'сожаление', 'эпоха', 'перевод', 'приятель', 
            'музей', 'звонок', 'диван', 'фон', 'князь', 
            'цена', 'союз', 'гражданин', 'плечо', 
            'взаимодействие', 'дело', 'доктор', 'машина', 
            'получение', 'завод', 'достоинство', 'вина', 'клуб', 
            'степень', 'русский', 'снег', 'кожа', 'начальство', 
            'канал', 'сущность', 'собрание', 'проведение', 'двигатель', 
            'курс', 'конструкция', 'память', 'система', 'материал', 'клуб', 
            'глубина', 'комплекс', 'тема', 'издание', 'государство', 'кризис', 
            'фронт', 'предел', 'сочинение', 'положение', 'дача', 'перевод', 
            'препарат', 'профессор', 'рабочий', 'свидетель', 'округ', 
            'правило', 'обработка', 'инженер', 'проверка', 'сумка', 
            'деталь', 'признание', 'деталь', 'мешок', 'корпус', 'хозяйство', 
            'величина', 'сведение', 'слово', 'брак', 'присутствие', 'покой', 
            'достоинство', 'страна', 'капитан', 'эксперт', 'качество', 
            'председатель', 'проверка', 'промышленность', 'налог', 
            'квартира', 'повод', 'обеспечение', 'программа', 'лейтенант']

# Текущие состояния игр: chat_id -> (слово, открытые буквы, попытки)
games = {}
users = {}
user_language = {}  # Добавляем язык для каждого пользователя
leaderboard = {}

COST_PER_ATTEMPT = 20 # Постоянная стоимость 1 попытки.

# Сообщения бота на двух языках
messages = {
    'en': {
        'start_game': "Let's start the game!",
        'stop_game': "Game stopped.",
        'invite': 'Please enter the username of the second player:',
        'help': "This is a Hangman game bot. Press 'Start Game' to begin. Guess the word by letters.",
        'switch_language': 'Switch Language',
        'start_button': 'Start Game',
        'stop_button': 'Stop Game',
        'invite_button': 'Invite Player',
        'help_button': 'Help',
        'buy_attempts_succes': 'One attempt has been added.',
        'buy_attempts_error': 'Not enough points :(',
        'buy_attempts': 'Buy Additional Attempts',
        'incorrect_guess': 'Incorrect! Remaining attempts: {}',
        'win': 'You win!',
        'lose': 'Game over! The word was: {}',
        'remaining_attempts': 'Remaining attempts: {}',
        'enter_word': 'Enter the word.',
        'unknown_command': 'Please use buttons for commands.',
        'not_started': 'You have not started the game.',
        'leaderboard_header': 'Leaderboard:\n',
        'leaderboard_button': 'Leaderboard',
        'current_score': 'Your current score: ',
    },
    'ru': {
        'start_game': 'Начинаем игру!',
        'stop_game': 'Игра остановлена.',
        'invite': 'Введите ник игрока для приглашения:',
        'help': 'Это бот для игры в "Виселицу". Нажмите "Начать игру" чтобы начать. Угадывайте слово по буквам.',
        'switch_language': 'Сменить язык',
        'start_button': 'Начать игру',
        'stop_button': 'Остановить игру',
        'invite_button': 'Пригласить игрока',
        'help_button': 'Помощь',
        'buy_attempts_succes': 'Добавлена одна попытка.',
        'buy_attempts_error': 'Недостаточно баллов :(',
        'buy_attempts': 'Купить дополнительные попытки',
        'incorrect_guess': 'Неверно! Осталось попыток: {}',
        'win': 'Вы выиграли!',
        'lose': 'Игра окончена! Загаданное слово было: {}',
        'remaining_attempts': 'Осталось попыток: {}',
        'enter_word': 'Указать целое слово.',
        'unknown_command': 'Пожалуйста, используйте кнопки для команд.',
        'not_started': 'Вы еще не запускали игру.',
        'leaderboard_header': 'Таблица лидеров:\n',
        'leaderboard_button': 'Таблица лидеров',
        'current_score': 'Текущий счет: ',
    }
}

# Функция для обновления таблицы лидеров
def update_leaderboard():
    # Сортируем пользователей по баллам в порядке убывания
    global leaderboard
    leaderboard = dict(sorted(users.items(), key=lambda item: item[1], reverse=True))

# Функция для отправки таблицы лидеров
def show_leaderboard(chat_id):
    lang = user_language.get(chat_id, 'en')
    update_leaderboard()
    
    # Создаем строку для вывода
    leaderboard_text = messages[lang]['leaderboard_header']
    
    for idx, (user_id, score) in enumerate(leaderboard.items(), 1):
        leaderboard_text += f"\n{idx}. {user_id} - {score} points"
    
    send_message(chat_id, leaderboard_text, reply_markup=create_menu_keyboard(chat_id))

# Функция для получения обновлений
def get_updates(offset=None):
    response = requests.get(URL + 'getUpdates', params={'offset': offset})
    return response.json().get('result', [])

# Функция для отправки сообщения
def send_message(chat_id, text, reply_markup=None):
    data = {'chat_id': chat_id, 'text': text}
    if reply_markup:
        data['reply_markup'] = reply_markup
    requests.post(URL + 'sendMessage', json=data)

# Главное меню с кнопками команд и кнопкой смены языка
def create_menu_keyboard(chat_id):
    lang = user_language.get(chat_id, 'en')
    keyboard = [
        [{'text': messages[lang]['start_button']}],
        [{'text': messages[lang]['stop_button']}],
        # [{'text': messages[lang]['invite_button']}],
        [{'text': messages[lang]['leaderboard_button']}],  # Новая кнопка для таблицы лидеров
        [{'text': messages[lang]['switch_language']}],
        [{'text': messages[lang]['help_button']}],
    ]

    return json.dumps({
        'keyboard': keyboard,
        'resize_keyboard': True,
        'one_time_keyboard': False
    })

# Клавиатура с буквами для игры и кнопкой "введите слово" внизу
def create_letter_keyboard(language):
    if language == 'en':
        keys = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    else:
        keys = [chr(i) for i in range(ord('а'), ord('я') + 1)]
    
    keyboard = [[{'text': key} for key in keys[i:i+8]] for i in range(0, len(keys), 8)]
    enter_word_button = [{'text': messages[language]['enter_word']}]
    keyboard.append(enter_word_button)
    
    # Добавляем кнопку для выхода в основное меню
    keyboard.append([{'text': messages[language]['buy_attempts']}])
    keyboard.append([{'text': messages[language]['stop_button']}])


    return json.dumps({
        'keyboard': keyboard,
        'resize_keyboard': True,
        'one_time_keyboard': False
    })


# Начать игру
def start_game(chat_id):
    lang = user_language.get(chat_id, 'en')
    word_list = words_en if lang == 'en' else words_ru
    word = random.choice(word_list)
    games[chat_id] = [word, ['_' if c.isalpha() else c for c in word], 5, lang]
    send_message(chat_id, messages[lang]['start_game'] + ' ' + ' '.join(games[chat_id][1]), reply_markup=create_letter_keyboard(lang))

# Остановить игру
def stop_game(chat_id, language):
    # print(chat_id)
    if chat_id in games:
        lang = games[chat_id][3]
        send_message(chat_id, messages[lang]['stop_game'], reply_markup=create_menu_keyboard(chat_id))
        del games[chat_id]
    else:
        send_message(chat_id, messages[language]['not_started'], reply_markup=create_menu_keyboard(chat_id))

# Логика игры
def game_logic(chat_id, text):
    if chat_id in games:
        word, known_letters, attempts_left, lang = games[chat_id]
        
        # Если игрок ввел слово
        if text.lower() == messages[lang]['enter_word'].lower():
            send_message(chat_id, messages[lang]['enter_word'], reply_markup=json.dumps({'remove_keyboard': True}))
            return
        
        # Если игрок вводит целое слово
        if len(text) > 1:
            if text.lower() == word.lower():
                # Если игрок угадал слово
                score = 50 * attempts_left
                update_score(chat_id, score)  # Добавляем баллы
                update_leaderboard()  # Обновляем рейтинг
                send_message(chat_id, f"{messages[lang]['win']} {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_menu_keyboard(chat_id))
                del games[chat_id]
            else:
                attempts_left -= 1
                games[chat_id][2] = attempts_left
                if attempts_left > 0:
                    send_message(chat_id, messages[lang]['incorrect_guess'].format(attempts_left), reply_markup=create_letter_keyboard(lang))
                else:
                    update_score(chat_id, -50)  # Вычитаем 50 баллов
                    update_leaderboard()  # Обновляем рейтинг
                    send_message(chat_id, f"{messages[lang]['lose'].format(word)} {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_menu_keyboard(chat_id))
                    del games[chat_id]

        elif text.lower() in word.lower() and text.lower() not in known_letters:
            # Если игрок угадал букву
            for idx, char in enumerate(word):
                if char.lower() == text.lower():
                    known_letters[idx] = char
            if '_' not in known_letters:
                score = 50 * attempts_left
                update_score(chat_id, score)  # Добавляем баллы
                update_leaderboard()  # Обновляем рейтинг
                send_message(chat_id, f"{messages[lang]['win']} {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_menu_keyboard(chat_id))
                del games[chat_id]
            else:
                send_message(chat_id, ' '.join(known_letters), reply_markup=create_letter_keyboard(lang))
        else:
            # Если неправильная буква
            attempts_left -= 1
            if attempts_left > 0:
                games[chat_id][2] = attempts_left
                send_message(chat_id, messages[lang]['incorrect_guess'].format(attempts_left), reply_markup=create_letter_keyboard(lang))
            else:
                update_score(chat_id, -50)  # Вычитаем 50 баллов
                update_leaderboard()  # Обновляем рейтинг
                send_message(chat_id, f"{messages[lang]['lose'].format(word)} {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_menu_keyboard(chat_id))
                del games[chat_id]

# Обновление баллов
def update_score(chat_id, score_change):
    if chat_id not in users:
        users[chat_id] = 0
    users[chat_id] += score_change

# Покупка дополнительных попыток
def buy_attempts(chat_id):
    lang = user_language.get(chat_id, 'en')
    
    # Проверяем, достаточно ли баллов для покупки
    if users.get(chat_id, 0) >= COST_PER_ATTEMPT:  # 20 баллов
        users[chat_id] -= COST_PER_ATTEMPT  # Вычитаем 20 баллов за одну попытку
        games[chat_id][2] += 1  # Добавляем одну попытку

        # Сообщаем пользователю об успешной покупке и оставшихся попытках
        send_message(chat_id, f"{messages[lang]['buy_attempts_succes']} {messages[lang]['remaining_attempts'].format(games[chat_id][2])}. {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_letter_keyboard(lang))
    else:
        # Если недостаточно баллов, уведомляем пользователя
        send_message(chat_id, f"{messages[lang]['buy_attempts_error']} {messages[lang]['current_score']} {users[chat_id]}", reply_markup=create_menu_keyboard(chat_id))
        
# Переключение языка
def switch_language(chat_id):
    current_language = user_language.get(chat_id, 'en')
    new_language = 'ru' if current_language == 'en' else 'en'
    user_language[chat_id] = new_language
    send_message(chat_id, f"Language switched to {'English' if new_language == 'en' else 'Русский'}", reply_markup=create_menu_keyboard(chat_id))

# Основной процесс (отслеживает нажатие кнопок)
def process_message(update):
    chat_id = update['message']['chat']['id']
    text = update['message']['text']
    lang = user_language.get(chat_id, 'en')
    
    if text == messages[lang]['start_button']:
        start_game(chat_id)
    elif text == messages[lang]['stop_button']:
        stop_game(chat_id, lang)
    elif text == messages[lang]['leaderboard_button']:  # Новая команда
        show_leaderboard(chat_id)
    elif text == messages[lang]['invite_button']:
        send_message(chat_id, messages[lang]['invite'], reply_markup=json.dumps({'remove_keyboard': True}))
    elif text == messages[lang]['help_button']:
        send_message(chat_id, messages[lang]['help'], reply_markup=create_menu_keyboard(chat_id))
    elif text == messages[lang]['switch_language']:
        switch_language(chat_id)
    elif text == messages[lang]['buy_attempts']:
        buy_attempts(chat_id)
    elif chat_id in games:
        game_logic(chat_id, text)
    else:
        # Отправляем сообщение на языке пользователя
        send_message(chat_id, messages[lang]['unknown_command'], reply_markup=create_menu_keyboard(chat_id))

# Основной цикл
def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if updates:
            for update in updates:
                last_update_id = update['update_id'] + 1
                if 'message' in update:
                    process_message(update)

if __name__ == '__main__':
    main()
