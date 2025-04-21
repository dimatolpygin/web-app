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
        <meta name="theme-color" content="#000000">
        <title>Lucid Dreams Clone</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&family=Montserrat:wght@700&display=swap');
            body {
                font-family: 'Poppins', sans-serif;
                background: linear-gradient(180deg, #000000, #1a1a1a);
                background-color: #000000;
                color: white;
                margin: 0;
                padding: 0;
                overflow-x: hidden;
                position: relative;
            }
            .stars {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: transparent;
                z-index: -1;
            }
            .stars .celestial {
                position: absolute;
                width: 3px;
                height: 3px;
                background: white;
                border-radius: 50%;
                box-shadow: 0 0 8px rgba(255, 165, 0, 0.5);
                animation: twinkle 3s infinite;
            }
            .stars .celestial:nth-child(1) { top: 10%; left: 15%; }
            .stars .celestial:nth-child(2) { top: 50%; left: 30%; animation-delay: 1s; }
            .stars .celestial:nth-child(3) { top: 70%; left: 90%; animation-delay: 1.5s; }
            @keyframes twinkle {
                0%, 100% { opacity: 0.5; transform: scale(1); }
                50% { opacity: 1; transform: scale(1.2); }
            }
            .container {
                max-width: 100%;
                padding: 10px;
            }
            .tabs {
                display: flex;
                justify-content: center;
                gap: 15px;
                position: fixed;
                bottom: 0;
                width: calc(100% - 60px);
                margin: 20px;
                background: rgba(255, 165, 0, 0.7);
                padding: 0;
                border-radius: 50px;
                box-shadow: 0 0 15px rgba(255, 165, 0, 0.6);
            }
            .tab {
                text-align: center;
                cursor: pointer;
                padding: 15px;
                transition: transform 0.2s;
            }
            .tab:hover {
                transform: scale(1.1);
            }
            .tab img {
                width: 36px;
                height: 36px;
                filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5));
            }
            .section {
                display: none;
                margin-bottom: 100px;
            }
            .section.active {
                display: block;
            }
            .subtabs {
                display: flex;
                justify-content: space-around;
                background: rgba(0, 0, 0, 0.5);
                border-radius: 10px;
                padding: 5px;
                margin-bottom: 10px;
                box-shadow: 0 0 10px rgba(255, 165, 0, 0.3);
            }
            .subtab {
                flex: 1;
                text-align: center;
                padding: 10px;
                cursor: pointer;
                border-radius: 8px;
                transition: background 0.3s, transform 0.2s;
                font-weight: 600;
                color: white;
            }
            .subtab:hover {
                transform: scale(1.05);
            }
            .subtab.active {
                background: #FFA500;
                box-shadow: 0 0 10px rgba(255, 165, 0, 0.5);
                color: black;
            }
            .sub-section {
                display: none;
            }
            .sub-section.active {
                display: block;
            }
            .card-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                grid-template-rows: repeat(2, auto);
                gap: 2px;
                justify-items: center;
            }
            .card {
                background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7) 70%, #FFA500 30%);
                border-radius: 15px;
                padding: 8px;
                border: 1px solid rgba(255, 165, 0, 0.2);
                box-shadow: 0 0 20px rgba(255, 165, 0, 0.6);
                transition: transform 0.3s, box-shadow 0.3s;
                text-align: center;
                position: relative;
                max-width: 160px;
            }
            .character-card {
                overflow: visible;
            }
            .item-card {
                height: 240px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .card:hover {
                transform: scale(1.05);
                box-shadow: 0 0 30px rgba(255, 165, 0, 0.8);
            }
            .character-card img {
                width: 160px;
                height: 240px;
                border-radius: 10px;
                object-fit: cover;
                object-position: top;
                margin: 0 auto;
                display: block;
                filter: drop-shadow(0 0 15px rgba(255, 165, 0, 0.7));
                position: relative;
                top: -20px;
            }
            .item-card img {
                width: 140px;
                height: 140px;
                border-radius: 10px;
                object-fit: cover;
                margin: 0 auto;
                display: block;
                filter: drop-shadow(0 0 15px rgba(255, 165, 0, 0.7));
            }
            .diamond-card img {
                width: 120px;
                height: 120px;
                border-radius: 10px;
                object-fit: cover;
                margin: 0 auto;
                display: block;
                filter: drop-shadow(0 0 15px rgba(255, 165, 0, 0.7));
            }
            .card h3 {
                font-family: 'Montserrat', sans-serif;
                font-size: 16px;
                margin: 5px 0;
                text-shadow: 0 0 5px rgba(255, 165, 0, 0.5);
            }
            .card p {
                font-size: 12px;
                margin: 0;
                height: auto;
                min-height: 20px;
                background: transparent;
                padding: 5px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }
            .item-card p, .diamond-card p {
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2px 12px;
                line-height: 12px;
                height: 20px;
                border-radius: 12px;
                background: rgba(255, 165, 0, 0.2);
                margin-bottom: 5px;
            }
            .diamond-card p {
                padding: 2px 8px;
                height: 18px;
            }
            .story-card {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 15px;
                padding: 10px;
                border: 1px solid rgba(255, 165, 0, 0.2);
                box-shadow: 0 0 20px rgba(255, 165, 0, 0.6);
                margin-bottom: 10px;
                position: relative;
                display: flex;
                flex-direction: column;
            }
            .story-card img {
                width: 100%;
                height: auto;
                max-height: 300px;
                border-radius: 10px;
                object-fit: cover;
            }
            .story-card .play-button {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 50px;
                height: 50px;
                background: #FFA500;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background 0.3s;
            }
            .story-card .play-button:hover {
                background: #FF8C00;
            }
            .story-card .play-button::before {
                content: '▶';
                color: black;
                font-size: 24px;
            }
            .back-button {
                background: #FFA500;
                color: black;
                padding: 10px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
                font-size: 16px;
                font-weight: 600;
                box-shadow: 0 0 15px rgba(255, 165, 0, 0.5);
                transition: transform 0.2s, box-shadow 0.3s;
            }
            .back-button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 25px rgba(255, 165, 0, 0.8);
            }
            .plan-card {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
                box-shadow: 0 0 10px rgba(255, 165, 0, 0.3);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .button {
                background: #FFA500;
                color: black;
                padding: 6px;
                border-radius: 10px;
                border: none;
                cursor: pointer;
                width: 100%;
                margin-top: 5px;
                font-size: 16px;
                font-weight: 600;
                box-shadow: 0 0 15px rgba(255, 165, 0, 0.5);
                transition: transform 0.2s, box-shadow 0.3s;
            }
            .button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 25px rgba(255, 165, 0, 0.8);
            }
            .header {
                font-family: 'Montserrat', sans-serif;
                text-align: center;
                font-size: 28px;
                font-weight: 800;
                margin: 20px 0;
                text-shadow: 0 0 15px rgba(255, 165, 0, 0.7);
            }
            .currency {
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(0, 0, 0, 0.7);
                padding: 5px 15px;
                border-radius: 15px;
                border: 1px solid rgba(255, 165, 0, 0.2);
                display: flex;
                align-items: center;
                box-shadow: 0 0 20px rgba(255, 165, 0, 0.6);
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.3s;
            }
            .currency:hover {
                transform: scale(1.05);
                box-shadow: 0 0 25px rgba(255, 165, 0, 0.8);
            }
            .currency img {
                width: 24px;
                height: 24px;
                margin-right: 5px;
                filter: drop-shadow(0 0 5px rgba(255, 165, 0, 0.5));
            }
            .language-option, .plan-option {
                background: rgba(0, 0, 0, 0.7);
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 0 10px rgba(255, 165, 0, 0.3);
                transition: background 0.3s, transform 0.2s;
            }
            .language-option:hover, .plan-option:hover {
                background: rgba(58, 58, 94, 0.5);
                transform: scale(1.02);
            }
        </style>
    </head>
    <body>
        <div class="stars">
            <div class="celestial"></div>
            <div class="celestial"></div>
            <div class="celestial"></div>
        </div>
        <div class="container">
            <div class="currency" onclick="showCurrencySection()">
                <img src="/static/images/diamond.png" alt="Diamonds">
                <span id="diamonds">0</span>
                <img src="/static/images/energy.png" alt="Energy" style="margin-left: 10px;">
                <span id="energy">100/100</span>
            </div>

            <!-- Персонажи -->
            <div id="characters" class="section active">
                <div class="header" data-i18n="characters_header">Персонажи</div>
                <div class="card-grid">
                    <div class="card character-card" onclick="setStyle('nika')">
                        <img src="/static/images/nika.png" alt="Nika">
                        <h3 data-i18n="character_nika_name">Ника</h3>
                        <p data-i18n="character_nika_desc">Робкая мечтательница</p>
                    </div>
                    <div class="card character-card" onclick="setStyle('nastya')">
                        <img src="/static/images/teta.png" alt="Nastya">
                        <h3 data-i18n="character_nastya_name">Настя</h3>
                        <p data-i18n="character_nastya_desc">Таинственная дива</p>
                    </div>
                    <div class="card character-card" onclick="setStyle('lara')">
                        <img src="/static/images/sa.png" alt="Lara">
                        <h3 data-i18n="character_lara_name">Лара</h3>
                        <p data-i18n="character_lara_desc">Смелая авантюристка</p>
                    </div>
                    <div class="card character-card" onclick="setStyle('skyler')">
                        <img src="/static/images/rik.png" alt="Skyler">
                        <h3 data-i18n="character_skyler_name">Скайлер</h3>
                        <p data-i18n="character_skyler_desc">Элегантная утонченность</p>
                    </div>
                </div>
            </div>

            <!-- История -->
            <div id="story" class="section">
                <div class="header" data-i18n="story_header">История</div>
                <div id="story-content"></div>
                <button class="back-button" data-i18n="back_button" onclick="showSection('characters')">Назад</button>
            </div>

            <!-- Магазин -->
            <div id="store" class="section">
                <div class="header" data-i18n="store_header">Магазин</div>
                <div class="subtabs">
                    <div class="subtab active" data-i18n="appearance_tab" onclick="showSubSection('appearance', this)">Внешний вид</div>
                    <div class="subtab" data-i18n="items_tab" onclick="showSubSection('items', this)">Предметы</div>
                    <div class="subtab" data-i18n="currency_tab" onclick="showSubSection('currency', this)">Валюта</div>
                </div>

                <!-- Внешний вид -->
                <div id="appearance" class="sub-section active">
                    <div class="card-grid">
                        <div class="card item-card">
                            <img src="/static/images/pajamas.png" alt="Pajamas">
                            <h3 data-i18n="item_pajamas_name">Милая пижама</h3>
                            <p>50 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('pajamas')">Разблокировать</button>
                        </div>
                        <div class="card item-card">
                            <img src="/static/images/lingerie.png" alt="Lingerie">
                            <h3 data-i18n="item_lingerie_name">Кружевное белье</h3>
                            <p>75 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('lingerie')">Разблокировать</button>
                        </div>
                        <div class="card item-card">
                            <img src="/static/images/cat_ears.png" alt="Cat Ears">
                            <h3 data-i18n="item_cat_ears_name">Ободок с ушками</h3>
                            <p>30 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('cat_ears')">Разблокировать</button>
                        </div>
                    </div>
                </div>

                <!-- Предметы -->
                <div id="items" class="sub-section">
                    <div class="card-grid">
                        <div class="card item-card">
                            <img src="/static/images/vip_pass.png" alt="VIP Pass">
                            <h3 data-i18n="item_vip_pass_name">Пропуск VIP</h3>
                            <p>40 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('vip_pass')">Разблокировать</button>
                        </div>
                        <div class="card item-card">
                            <img src="/static/images/wine_bottle.png" alt="Wine Bottle">
                            <h3 data-i18n="item_wine_bottle_name">Бутылка вина</h3>
                            <p>12 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('wine_bottle')">Разблокировать</button>
                        </div>
                        <div class="card item-card">
                            <img src="/static/images/control_charm.png" alt="Control Charm">
                            <h3 data-i18n="item_control_charm_name">Контрольный шарм</h3>
                            <p>20 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('control_charm')">Разблокировать</button>
                        </div>
                        <div class="card item-card">
                            <img src="/static/images/flower_bouquet.png" alt="Flower Bouquet">
                            <h3 data-i18n="item_flower_bouquet_name">Букет цветов</h3>
                            <p>15 💎</p>
                            <button class="button" data-i18n="unlock_button" onclick="buyItem('flower_bouquet')">Разблокировать</button>
                        </div>
                    </div>
                </div>

                <!-- Валюта -->
                <div id="currency" class="sub-section">
                    <div class="card-grid">
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_540.png" alt="Diamonds">
                            <h3>540 💎</h3>
                            <p>50 💎</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(540)">Купить</button>
                        </div>
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_1360.png" alt="Diamonds">
                            <h3>1360 💎</h3>
                            <p>$55.00</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(1360)">Купить</button>
                        </div>
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_2720.png" alt="Diamonds">
                            <h3>2720 💎</h3>
                            <p>$100.00</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(2720)">Купить</button>
                        </div>
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_85.png" alt="Diamonds">
                            <h3>85 💎</h3>
                            <p>$4.40</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(85)">Купить</button>
                        </div>
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_210.png" alt="Diamonds">
                            <h3>210 💎</h3>
                            <p>$12.00</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(210)">Купить</button>
                        </div>
                        <div class="card diamond-card">
                            <img src="/static/images/diamonds_5000.png" alt="Diamonds">
                            <h3>5000 💎</h3>
                            <p>$150.00</p>
                            <button class="button" data-i18n="buy_button" onclick="buyDiamonds(5000)">Купить</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Настройки -->
            <div id="settings" class="section">
                <div class="header" data-i18n="settings_header">Настройки</div>
                <div class="subtabs">
                    <div class="subtab active" data-i18n="language_tab" onclick="showSubSection('language', this)">Язык</div>
                    <div class="subtab" data-i18n="plan_tab" onclick="showSubSection('plan', this)">Статус вашего плана</div>
                </div>

                <!-- Язык -->
                <div id="language" class="sub-section active">
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

                <!-- План -->
                <div id="plan" class="sub-section">
                    <div class="plan-card">
                        <span data-i18n="plan_month">Плюс на месяц</span>
                        <span>30 💎 ($6.90 / месяц)</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_three_months">Плюс на три месяца</span>
                        <span>70 💎 ($13.80 / 3 месяца)</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_year">Плюс на год</span>
                        <span>210 💎 ($41.40 / год)</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_infinite_energy">Бесконечная энергия</span>
                        <span>⚡</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_210_diamonds">210 кристаллов для покупок</span>
                        <span>💎</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_ai_priority">Начинать субпрерогативу ИИ-моделей</span>
                        <span>🚀</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_unlimited_images">Неограниченная генерация изображений</span>
                        <span>📸</span>
                    </div>
                    <div class="plan-card">
                        <span data-i18n="plan_instant_replies">Практически мгновенные ответы</span>
                        <span>💬</span>
                    </div>
                    <button class="button" data-i18n="select_button" onclick="alert('Выбор плана в разработке')">Выбрать</button>
                </div>
            </div>
        </div>

        <div class="tabs">
            <div class="tab" onclick="showSection('characters')"><img src="/static/images/character.png" alt="Characters"></div>
            <div class="tab" onclick="showSection('store')"><img src="/static/images/store.png" alt="Store"></div>
            <div class="tab" onclick="showSection('settings')"><img src="/static/images/settings.png" alt="Settings"></div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.ready();
            tg.expand();
            tg.enableClosingConfirmation();

            let userId = tg.initDataUnsafe.user.id;
            let currentLanguage = 'Русский';

            const translations = {
                'Русский': {
                    characters_header: 'Персонажи',
                    story_header: 'История',
                    store_header: 'Магазин',
                    settings_header: 'Настройки',
                    appearance_tab: 'Внешний вид',
                    items_tab: 'Предметы',
                    currency_tab: 'Валюта',
                    language_tab: 'Язык',
                    plan_tab: 'Статус вашего плана',
                    select_button: 'Выбрать',
                    unlock_button: 'Разблокировать',
                    buy_button: 'Купить',
                    back_button: 'Назад',
                    character_nika_name: 'Ника',
                    character_nika_desc: 'Робкая мечтательница',
                    character_nastya_name: 'Настя',
                    character_nastya_desc: 'Таинственная дива',
                    character_lara_name: 'Лара',
                    character_lara_desc: 'Смелая авантюристка',
                    character_skyler_name: 'Скайлер',
                    character_skyler_desc: 'Элегантная утонченность',
                    item_pajamas_name: 'Милая пижама',
                    item_lingerie_name: 'Кружевное белье',
                    item_cat_ears_name: 'Ободок с ушками',
                    item_vip_pass_name: 'Пропуск VIP',
                    item_wine_bottle_name: 'Бутылка вина',
                    item_control_charm_name: 'Контрольный шарм',
                    item_flower_bouquet_name: 'Букет цветов',
                    plan_month: 'Плюс на месяц',
                    plan_three_months: 'Плюс на три месяца',
                    plan_year: 'Плюс на год',
                    plan_infinite_energy: 'Бесконечная энергия',
                    plan_210_diamonds: '210 кристаллов для покупок',
                    plan_ai_priority: 'Начинать субпрерогативу ИИ-моделей',
                    plan_unlimited_images: 'Неограниченная генерация изображений',
                    plan_instant_replies: 'Практически мгновенные ответы',
                    story_nika_title: 'Урок полового воспитания',
                    story_nika_desc: 'Забавная юная затейница пойдет на всё, чтобы получить заветный оргазм.',
                    story_nastya_title: 'Семейный инцидент',
                    story_nastya_desc: 'Юная Сводная сестра случайно прыгнула прямо на твой стояк.',
                    story_lara_title: 'В трёх соснах',
                    story_lara_desc: 'Накажи в лесу, мокрую и совершенно голую?',
                    story_skyler_title: 'Тайна элегантности',
                    story_skyler_desc: 'Раскрой секрет утонченности Скайлер в её новой истории.'
                },
                'English': {
                    characters_header: 'Characters',
                    story_header: 'Story',
                    store_header: 'Store',
                    settings_header: 'Settings',
                    appearance_tab: 'Appearance',
                    items_tab: 'Items',
                    currency_tab: 'Currency',
                    language_tab: 'Language',
                    plan_tab: 'Your Plan Status',
                    select_button: 'Select',
                    unlock_button: 'Unlock',
                    buy_button: 'Buy',
                    back_button: 'Back',
                    character_nika_name: 'Nika',
                    character_nika_desc: 'Shy Dreamer',
                    character_nastya_name: 'Nastya',
                    character_nastya_desc: 'Mysterious Diva',
                    character_lara_name: 'Lara',
                    character_lara_desc: 'Bold Adventurer',
                    character_skyler_name: 'Skyler',
                    character_skyler_desc: 'Elegant Sophistication',
                    item_pajamas_name: 'Cute Pajamas',
                    item_lingerie_name: 'Lace Lingerie',
                    item_cat_ears_name: 'Cat Ears Headband',
                    item_vip_pass_name: 'VIP Pass',
                    item_wine_bottle_name: 'Bottle of Wine',
                    item_control_charm_name: 'Control Charm',
                    item_flower_bouquet_name: 'Flower Bouquet',
                    plan_month: 'Plus for a Month',
                    plan_three_months: 'Plus for Three Months',
                    plan_year: 'Plus for a Year',
                    plan_infinite_energy: 'Infinite Energy',
                    plan_210_diamonds: '210 Diamonds for Purchases',
                    plan_ai_priority: 'Start AI Model Subprerogative',
                    plan_unlimited_images: 'Unlimited Image Generation',
                    plan_instant_replies: 'Near-Instant Replies',
                    story_nika_title: 'Sex Education Lesson',
                    story_nika_desc: 'A funny young trickster will go all out to achieve the desired climax.',
                    story_nastya_title: 'Family Incident',
                    story_nastya_desc: 'Your step-sister accidentally jumped right onto your lap.',
                    story_lara_title: 'Lost in the Woods',
                    story_lara_desc: 'Punish in the forest, wet and completely naked?',
                    story_skyler_title: 'The Secret of Elegance',
                    story_skyler_desc: 'Uncover the secret of Skyler’s sophistication in her new story.'
                }
            };

            // Функция для обновления текста на странице
            function updateLanguage(lang) {
                document.querySelectorAll('[data-i18n]').forEach(element => {
                    const key = element.getAttribute('data-i18n');
                    if (translations[lang] && translations[lang][key]) {
                        element.innerText = translations[lang][key];
                    }
                });
            }

            // Загрузка данных пользователя
            fetch('/get_user_data?user_id=' + userId)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('diamonds').innerText = data.diamonds;
                    document.getElementById('energy').innerText = data.energy + '/100';
                    if (data.language) {
                        currentLanguage = data.language;
                        updateLanguage(currentLanguage);
                        document.querySelectorAll('.language-option span[id^="lang-"]').forEach(span => {
                            span.style.display = 'none';
                        });
                        const langElement = document.getElementById('lang-' + data.language);
                        if (langElement) {
                            langElement.style.display = 'inline';
                        }
                    }
                })
                .catch(error => console.error('Error loading user data:', error));

            function showSection(sectionId) {
                document.querySelectorAll('.section').forEach(section => {
                    section.classList.remove('active');
                });
                document.getElementById(sectionId).classList.add('active');
                if (sectionId === 'store') {
                    showSubSection('appearance', document.querySelector('#store .subtab'));
                } else if (sectionId === 'settings') {
                    showSubSection('language', document.querySelector('#settings .subtab'));
                }
            }

            function showSubSection(subSectionId, element) {
                const parentSection = element.closest('.section');
                parentSection.querySelectorAll('.sub-section').forEach(section => {
                    section.classList.remove('active');
                });
                parentSection.querySelectorAll('.subtab').forEach(tab => {
                    tab.classList.remove('active');
                });
                parentSection.querySelector('#' + subSectionId).classList.add('active');
                element.classList.add('active');
            }

            function showCurrencySection() {
                showSection('store');
                showSubSection('currency', document.querySelector('#store .subtab:nth-child(3)'));
            }

            function showStory(character) {
                const stories = {
                    'nika': {
                        image: '/static/images/1.png',
                        title: 'story_nika_title',
                        desc: 'story_nika_desc'
                    },
                    'nastya': {
                        image: '/static/images/2.png',
                        title: 'story_nastya_title',
                        desc: 'story_nastya_desc'
                    },
                    'lara': {
                        image: '/static/images/3.png',
                        title: 'story_lara_title',
                        desc: 'story_lara_desc'
                    },
                    'skyler': {
                        image: '/static/images/4.png',
                        title: 'story_skyler_title',
                        desc: 'story_skyler_desc'
                    }
                };

                const story = stories[character];
                if (!story) return;

                const storyContent = `
                    <div class="story-card">
                        <img src="${story.image}" alt="${character} Story">
                        <div class="play-button" onclick="alert('Запуск истории в разработке')"></div>
                        <h3 data-i18n="${story.title}">${translations[currentLanguage][story.title]}</h3>
                        <p data-i18n="${story.desc}">${translations[currentLanguage][story.desc]}</p>
                    </div>
                `;
                document.getElementById('story-content').innerHTML = storyContent;
                showSection('story');
            }

            function setStyle(style) {
                fetch('/set_style', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, style: style })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Стиль изменен!');
                        showStory(style);
                    }
                })
                .catch(error => console.error('Error setting style:', error));
            }

            function setLanguage(language) {
                fetch('/set_language', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, language: language })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        currentLanguage = language;
                        updateLanguage(language);
                        document.querySelectorAll('.language-option span[id^="lang-"]').forEach(span => {
                            span.style.display = 'none';
                        });
                        const langElement = document.getElementById('lang-' + language);
                        if (langElement) {
                            langElement.style.display = 'inline';
                        }
                    }
                })
                .catch(error => console.error('Error setting language:', error));
            }

            function buyItem(item) {
                fetch('/buy_item', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, item: item })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('diamonds').innerText = data.diamonds;
                        alert('Предмет куплен!');
                    } else {
                        alert('Недостаточно кристаллов! Перейди в магазин.');
                    }
                })
                .catch(error => console.error('Error buying item:', error));
            }

            function buyDiamonds(amount) {
                fetch('/buy_diamonds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, amount: amount })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('diamonds').innerText = data.diamonds;
                        alert('Кристаллы добавлены!');
                    } else {
                        alert('Ошибка при добавлении кристаллов.');
                    }
                })
                .catch(error => console.error('Error buying diamonds:', error));
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
    c.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    updated_language = c.fetchone()[0]
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
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, diamonds, energy, style, language) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 0, 100, 'nika', 'Русский'))
        conn.commit()
        diamonds = 0
    else:
        diamonds = user[0]

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

# Покупка кристаллов
@app.route('/buy_diamonds', methods=['POST'])
def buy_diamonds():
    data = request.get_json()
    user_id = data['user_id']
    amount = data['amount']
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    
    # Проверяем, существует ли пользователь
    c.execute("SELECT diamonds FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if not user:
        c.execute("INSERT INTO users (user_id, diamonds, energy, style, language) VALUES (?, ?, ?, ?, ?)",
                  (user_id, 0, 100, 'nika', 'Русский'))
        conn.commit()
    
    # Обновляем количество кристаллов
    c.execute("UPDATE users SET diamonds = diamonds + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    
    # Получаем обновленное количество кристаллов
    c.execute("SELECT diamonds FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    if result is None:
        conn.close()
        return jsonify({"success": False, "error": "User not found after update"})
    
    new_diamonds = result[0]
    conn.close()
    return jsonify({"success": True, "diamonds": new_diamonds})

# Вебхук для Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST]')
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
