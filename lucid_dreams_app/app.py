import os
import sqlite3
from flask import Flask, request, send_from_directory, jsonify
from telegram import Bot

app = Flask(__name__)

# Чтение переменных из окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

# Проверка, что TELEGRAM_TOKEN задан
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")

bot = Bot(token=TELEGRAM_TOKEN)

# Инициализация базы данных SQLite
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        diamonds INTEGER DEFAULT 0,
        energy INTEGER DEFAULT 100,
        style TEXT DEFAULT 'nika',
        language TEXT DEFAULT 'Русский'
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        user_id INTEGER,
        item TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )''')
    conn.commit()
    conn.close()

init_db()

# Отдача статических файлов (картинок)
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Главная страница веб-приложения
@app.route('/webapp')
def webapp():
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lucid Dreams Clone</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(180deg, #1a1a2e, #0f0f1a);
                color: white;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
            }
            .container {
                max-width: 100%;
                padding: 20px;
            }
            .tabs {
                display: flex;
                justify-content: space-around;
                position: fixed;
                bottom: 0;
                width: 100%;
                background: #0f0f1a;
                padding: 10px 0;
                border-top: 1px solid #3a3a5e;
                box-shadow: 0 -2px 10px rgba(138, 43, 226, 0.3);
            }
            .tab {
                text-align: center;
                cursor: pointer;
                padding: 10px;
                transition: transform 0.2s;
            }
            .tab:hover {
                transform: scale(1.1);
            }
            .tab img {
                width: 24px;
                height: 24px;
            }
            .section {
                display: none;
                margin-bottom: 60px;
            }
            .section.active {
                display: block;
            }
            .subtabs {
                display: flex;
                justify-content: space-around;
                background: #2a2a4e;
                border-radius: 10px;
                padding: 5px;
                margin-bottom: 10px;
            }
            .subtab {
                flex: 1;
                text-align: center;
                padding: 10px;
                cursor: pointer;
                border-radius: 8px;
                transition: background 0.3s;
            }
            .subtab.active {
                background: #6a5acd;
            }
            .card {
                background: #2a2a4e;
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #4a4a8e;
                box-shadow: 0 0 15px rgba(138, 43, 226, 0.5);
                transition: transform 0.3s;
            }
            .card:hover {
                transform: scale(1.02);
            }
            .card img {
                width: 150px;
                height: 225px;
                border-radius: 10px;
                object-fit: cover;
            }
            .item-card img {
                width: 120px;
                height: 120px;
            }
            .diamond-card img {
                width: 100px;
                height: 100px;
            }
            .button {
                background: linear-gradient(90deg, #8a2be2, #ff00ff);
                color: white;
                padding: 10px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
                font-size: 16px;
                font-weight: 600;
                box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
                transition: transform 0.2s, box-shadow 0.3s;
            }
            .button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 20px rgba(255, 0, 255, 0.8);
            }
            .header {
                text-align: center;
                font-size: 24px;
                font-weight: 600;
                margin: 20px 0;
                text-shadow: 0 0 10px rgba(138, 43, 226, 0.5);
            }
            .currency {
                position: fixed;
                top: 10px;
                right: 10px;
                background: #2a2a4e;
                padding: 5px 10px;
                border-radius: 10px;
                display: flex;
                align-items: center;
                box-shadow: 0 0 15px rgba(138, 43, 226, 0.5);
                cursor: pointer;
                transition: transform 0.2s;
            }
            .currency:hover {
                transform: scale(1.05);
            }
            .currency img {
                width: 24px;
                height: 24px;
                margin-right: 5px;
            }
            .language-option {
                background: #2a2a4e;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 0 10px rgba(138, 43, 226, 0.3);
                transition: background 0.3s;
            }
            .language-option:hover {
                background: #3a3a5e;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="currency" onclick="showSection('store')">
                <img src="/static/images/diamond.png" alt="Diamonds">
                <span id="diamonds">0</span>
                <img src="/static/images/energy.png" alt="Energy" style="margin-left: 10px;">
                <span id="energy">100/100</span>
            </div>

            <!-- Персонажи -->
            <div id="characters" class="section active">
                <div class="header">Персонажи</div>
                <div class="card">
                    <img src="/static/images/nika.png" alt="Nika">
                    <h3>Ника</h3>
                    <p>Робкая мечтательница, которая скрывает страстную натуру за своими изящными нарядами.</p>
                    <button class="button" onclick="setStyle('nika')">Выбрать</button>
                </div>
                <div class="card">
                    <img src="/static/images/teta.png" alt="Teta">
                    <h3>Тета Пресс</h3>
                    <p>Таинственная дива с магнетическим взглядом, готовая покорить любое сердце.</p>
                    <button class="button" onclick="setStyle('teta')">Выбрать</button>
                </div>
                <div class="card">
                    <img src="/static/images/sa.png" alt="Sa">
                    <h3>Са</h3>
                    <p>Смелая и независимая, она всегда готова к новым приключениям.</p>
                    <button class="button" onclick="setStyle('sa')">Выбрать</button>
                </div>
                <div class="card">
                    <img src="/static/images/rik.png" alt="Rik">
                    <h3>Рик</h3>
                    <p>Элегантная и утонченная, её очарование неподвластно времени.</p>
                    <button class="button" onclick="setStyle('rik')">Выбрать</button>
                </div>
            </div>

            <!-- Магазин -->
            <div id="store" class="section">
                <div class="header">Магазин</div>
                <div class="subtabs">
                    <div class="subtab active" onclick="showSubSection('appearance', this)">Внешний вид</div>
                    <div class="subtab" onclick="showSubSection('items', this)">Предметы</div>
                    <div class="subtab" onclick="showSubSection('currency', this)">Валюта</div>
                </div>

                <!-- Внешний вид -->
                <div id="appearance" class="sub-section active">
                    <div class="card">
                        <img src="/static/images/nika.png" alt="Nika">
                        <h3>Ника</h3>
                        <p>Робкая мечтательница, которая скрывает страстную натуру за своими изящными нарядами.</p>
                        <button class="button" onclick="setStyle('nika')">Выбрать</button>
                    </div>
                    <div class="card">
                        <img src="/static/images/teta.png" alt="Teta">
                        <h3>Тета Пресс</h3>
                        <p>Таинственная дива с магнетическим взглядом, готовая покорить любое сердце.</p>
                        <button class="button" onclick="setStyle('teta')">Выбрать</button>
                    </div>
                    <div class="card">
                        <img src="/static/images/sa.png" alt="Sa">
                        <h3>Са</h3>
                        <p>Смелая и независимая, она всегда готова к новым приключениям.</p>
                        <button class="button" onclick="setStyle('sa')">Выбрать</button>
                    </div>
                    <div class="card">
                        <img src="/static/images/rik.png" alt="Rik">
                        <h3>Рик</h3>
                        <p>Элегантная и утонченная, её очарование неподвластно времени.</p>
                        <button class="button" onclick="setStyle('rik')">Выбрать</button>
                    </div>
                </div>

                <!-- Предметы -->
                <div id="items" class="sub-section">
                    <div class="card item-card">
                        <img src="/static/images/pajamas.png" alt="Pajamas">
                        <h3>Милая пижама</h3>
                        <p>50 💎</p>
                        <button class="button" onclick="buyItem('pajamas')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/lingerie.png" alt="Lingerie">
                        <h3>Кружевное белье</h3>
                        <p>75 💎</p>
                        <button class="button" onclick="buyItem('lingerie')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/cat_ears.png" alt="Cat Ears">
                        <h3>Ободок с ушками</h3>
                        <p>30 💎</p>
                        <button class="button" onclick="buyItem('cat_ears')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/vip_pass.png" alt="VIP Pass">
                        <h3>Пропуск VIP</h3>
                        <p>40 💎</p>
                        <button class="button" onclick="buyItem('vip_pass')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/wine_bottle.png" alt="Wine Bottle">
                        <h3>Бутылка вина</h3>
                        <p>12 💎</p>
                        <button class="button" onclick="buyItem('wine_bottle')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/control_charm.png" alt="Control Charm">
                        <h3>Контрольный шарм</h3>
                        <p>20 💎</p>
                        <button class="button" onclick="buyItem('control_charm')">Разблокировать</button>
                    </div>
                    <div class="card item-card">
                        <img src="/static/images/flower_bouquet.png" alt="Flower Bouquet">
                        <h3>Букет цветов</h3>
                        <p>15 💎</p>
                        <button class="button" onclick="buyItem('flower_bouquet')">Разблокировать</button>
                    </div>
                </div>

                <!-- Валюта -->
                <div id="currency" class="sub-section">
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_540.png" alt="Diamonds">
                        <h3>540 💎</h3>
                        <p>$25.00</p>
                        <button class="button" onclick="buyDiamonds(540)">Заработать</button>
                    </div>
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_1360.png" alt="Diamonds">
                        <h3>1360 💎</h3>
                        <p>$55.00</p>
                        <button class="button" onclick="buyDiamonds(1360)">Заработать</button>
                    </div>
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_2720.png" alt="Diamonds">
                        <h3>2720 💎</h3>
                        <p>$100.00</p>
                        <button class="button" onclick="buyDiamonds(2720)">Заработать</button>
                    </div>
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_85.png" alt="Diamonds">
                        <h3>85 💎</h3>
                        <p>$4.40</p>
                        <button class="button" onclick="buyDiamonds(85)">Заработать</button>
                    </div>
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_210.png" alt="Diamonds">
                        <h3>210 💎</h3>
                        <p>$12.00</p>
                        <button class="button" onclick="buyDiamonds(210)">Заработать</button>
                    </div>
                    <div class="card diamond-card">
                        <img src="/static/images/diamonds_5000.png" alt="Diamonds">
                        <h3>5000 💎</h3>
                        <p>$150.00</p>
                        <button class="button" onclick="buyDiamonds(5000)">Заработать</button>
                    </div>
                </div>
            </div>

            <!-- Настройки -->
            <div id="settings" class="section">
                <div class="header">Настройки</div>
                <div class="language-option" onclick="setLanguage('Русский')">
                    <span>Русский</span>
                    <span id="lang-Русский" style="display: none;">✔️</span>
                </div>
                <div class="language-option" onclick="setLanguage('English')">
                    <span>English</span>
                    <span id="lang-English" style="display: none;">✔️</span>
                </div>
                <div class="language-option" onclick="setLanguage('Français')">
                    <span>Français</span>
                    <span id="lang-Français" style="display: none;">✔️</span>
                </div>
                <div class="language-option" onclick="setLanguage('Italiano')">
                    <span>Italiano</span>
                    <span id="lang-Italiano" style="display: none;">✔️</span>
                </div>
                <div class="language-option" onclick="setLanguage('Deutsch')">
                    <span>Deutsch</span>
                    <span id="lang-Deutsch" style="display: none;">✔️</span>
                </div>
                <div class="language-option" onclick="setLanguage('Español')">
                    <span>Español</span>
                    <span id="lang-Español" style="display: none;">✔️</span>
                </div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab" onclick="showSection('characters')"><img src="/static/images/gear.png" alt="Characters"></div>
            <div class="tab" onclick="showSection('store')"><img src="/static/images/store.png" alt="Store"></div>
            <div class="tab" onclick="showSection('settings')"><img src="/static/images/settings.png" alt="Settings"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();

            let userId = tg.initDataUnsafe.user.id;

            // Загрузка данных пользователя
            fetch('/get_user_data?user_id=' + userId)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('diamonds').innerText = data.diamonds;
                    document.getElementById('energy').innerText = data.energy + '/100';
                    document.getElementById('lang-' + data.language).style.display = 'inline';
                });

            function showSection(sectionId) {
                document.querySelectorAll('.section').forEach(section => {
                    section.classList.remove('active');
                });
                document.getElementById(sectionId).classList.add('active');
                if (sectionId === 'store') {
                    showSubSection('appearance', document.querySelector('.subtab'));
                }
            }

            function showSubSection(subSectionId, element) {
                document.querySelectorAll('.sub-section').forEach(section => {
                    section.classList.remove('active');
                });
                document.querySelectorAll('.subtab').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.getElementById(subSectionId).classList.add('active');
                element.classList.add('active');
            }

            function setStyle(style) {
                fetch('/set_style', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, style: style })
                }).then(() => {
                    alert('Стиль изменен!');
                });
            }

            function setLanguage(language) {
                fetch('/set_language', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, language: language })
                }).then(() => {
                    document.querySelectorAll('.language-option span[id^="lang-"]').forEach(span => {
                        span.style.display = 'none';
                    });
                    document.getElementById('lang-' + language).style.display = 'inline';
                });
            }

            function buyItem(item) {
                fetch('/buy_item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, item: item })
                }).then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            document.getElementById('diamonds').innerText = data.diamonds;
                            alert('Предмет куплен!');
                        } else {
                            alert('Недостаточно кристаллов! Перейди в магазин.');
                        }
                    });
            }

            function buyDiamonds(amount) {
                fetch('/buy_diamonds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, amount: amount })
                }).then(response => response.json())
                    .then(data => {
                        document.getElementById('diamonds').innerText = data.diamonds;
                        alert('Кристаллы добавлены!');
                    });
            }
        </script>
    </body>
    </html>
    '''

# Получение данных пользователя
@app.route('/get_user_data')
def get_user_data():
    user_id = request.args.get('user_id')
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT diamonds, energy, style, language FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, diamonds, energy, style, language) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 0, 100, 'nika', 'Русский'))
        conn.commit()
        user = (0, 100, 'nika', 'Русский')
    conn.close()
    return jsonify({"diamonds": user[0], "energy": user[1], "style": user[2], "language": user[3]})

# Установка стиля персонажа
@app.route('/set_style', methods=['POST'])
def set_style():
    data = request.get_json()
    user_id = data['user_id']
    style = data['style']
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET style = ? WHERE user_id = ?", (style, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# Установка языка
@app.route('/set_language', methods=['POST'])
def set_language():
    data = request.get_json()
    user_id = data['user_id']
    language = data['language']
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# Покупка предмета
@app.route('/buy_item', methods=['POST'])
def buy_item():
    data = request.get_json()
    user_id = data['user_id']
    item = data['item']
    prices = {'pajamas': 50, 'lingerie': 75, 'cat_ears': 30, 'vip_pass': 40, 'wine_bottle': 12, 'control_charm': 20, 'flower_bouquet': 15}
    price = prices.get(item, 0)

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT diamonds FROM users WHERE user_id = ?", (user_id,))
    diamonds = c.fetchone()[0]

    if diamonds >= price:
        c.execute("UPDATE users SET diamonds = diamonds - ? WHERE user_id = ?", (price, user_id))
        c.execute("INSERT INTO purchases (user_id, item) VALUES (?, ?)", (user_id, item))
        conn.commit()
        c.execute("SELECT diamonds FROM users WHERE user_id = ?", (user_id,))
        new_diamonds = c.fetchone()[0]
        conn.close()
        return jsonify({"success": True, "diamonds": new_diamonds})
    else:
        conn.close()
        return jsonify({"success": False})

# Покупка кристаллов (пока без реальных платежей)
@app.route('/buy_diamonds', methods=['POST'])
def buy_diamonds():
    data = request.get_json()
    user_id = data['user_id']
    amount = data['amount']
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET diamonds = diamonds + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    c.execute("SELECT diamonds FROM users WHERE user_id = ?", (user_id,))
    new_diamonds = c.fetchone()[0]
    conn.close()
    return jsonify({"success": True, "diamonds": new_diamonds})

# Вебхук для Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    chat_id = update['message']['chat']['id'] if 'message' in update else None
    if chat_id:
        keyboard = {
            "inline_keyboard": [[{"text": "Открыть приложение", "web_app": {"url": WEBAPP_URL}}]]
        }
        bot.send_message(chat_id=chat_id, text="Добро пожаловать! Открой приложение!", reply_markup=keyboard)
    return 'OK'

def set_webhook():
    webhook_url = f"{WEBAPP_URL.replace('/webapp', '')}/{TELEGRAM_TOKEN}"
    bot.set_webhook(url=webhook_url)

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
