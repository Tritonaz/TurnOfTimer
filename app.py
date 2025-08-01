from media_getter import get_active_audio_sessions, get_media_info, control_media
from blya import fix_keyboard_layout
import asyncio
from threading import Thread, Lock
from flask import Flask, request, redirect, url_for, session, render_template, jsonify
from datetime import timedelta
import os
import time
import pandas as pd
import datetime
# imports for show_notification
import time
import random
import tkinter as tk
from PIL import Image, ImageTk
# imports for track_active_window
from win32gui import GetWindowText, GetForegroundWindow
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)  # змінити на щось випадкове
app.permanent_session_lifetime = timedelta(minutes=30)

# 🔐 пароль, який треба ввести
PASSWORD = '4521'

timer_data = {
    "remaining": 60,
    "running": False,
    "mode": "sleep"  # або "shutdown"
}


def show_notification(
        title="",
        text="",
        duration=5,
        image_path=None,  # Шлях до PNG зображення
        max_image_size=(64, 64)):
    """
    Показує кастомне сповіщення в кутку екрана на вказану кількість секунд.
    :param title: Заголовок сповіщення.
    :param text: Текст сповіщення.
    :param duration: Час у секундах, протягом якого сповіщення буде видно.
    :param image_path: Шлях до зображення (PNG).
    :param max_image_size: Максимальні розміри зображення (ширина, висота).
    """

    def create_window(custom_title, custom_text):
        # варіації кольорів заголовків і повідомлень
        colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#33FFF5", "#A133FF", "#FF5733", "#F5A623", "#F82323",
            "#00C896", "#FFC300", "#3CFF33", "#3C33FF", "#FF333C", "#33F5FF", "#A1FF33", "#FFD433", "#FF6633",
            "#33DFFF", "#23A6F5", "#3CA6F5", "#5DFFAA", "#FF8833", "#33FF4D", "#44AAFF", "#FFCC33", "#33E8FF",
            "#FF33D4", "#A633FF", "#FF3366", "#33FF88", "#333AFF", "#FF8F33", "#3CA2FF", "#FF8D33", "#FF77AA",
            "#E8FF33", "#FFC233", "#FF5544", "#3399FF", "#FF3355", "#33DFFF", "#55FF33", "#FFAA88", "#77FF33",
            "#33A6FF", "#FF33AA", "#AAFF33", "#33AAFF", "#FF3399", "#FF88FF", "#AA33FF", "#FF3388", "#88FF33",
            "#55AAFF", "#AA3388", "#FF6655", "#33CCFF", "#CC33FF", "#55FF77", "#FFAA55", "#FF5566", "#99FF33",
            "#FF3388", "#66FF33", "#44FFAA", "#FFAA77", "#33FF66", "#AA55FF", "#FF5544", "#99FFAA", "#FFAA33",
            "#55FF99", "#33FF55", "#77AAFF", "#44CCFF", "#CCFF33", "#FF66AA", "#CC33AA", "#FF99FF", ]
        # Створюємо вікно
        root = tk.Tk()
        root.title(title)
        root.attributes("-topmost", True)  # Поверх інших вікон
        root.overrideredirect(True)  # Вимикаємо рамку вікна
        # Визначаємо розміри та розташування
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 310
        window_height = 110
        x = screen_width - window_width - 20  # Відступ від правого краю
        y = screen_height - window_height - 60  # Відступ від нижнього краю
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        # Налаштовуємо фон і обводку
        random.seed(time.time_ns())
        random.shuffle(colors)
        outer_frame = tk.Frame(root, bg=random.choice(
            colors), bd=3)  # колір обводки в bg
        outer_frame.pack(fill="both", expand=True)
        inner_frame = tk.Frame(outer_frame, bg="black")
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        # Додаємо контейнер для напису і картинки
        image_with_caption_frame = tk.Frame(inner_frame, bg="black")
        image_with_caption_frame.pack(side="right", padx=5, pady=5)
        # Час
        time_label = tk.Label(
            image_with_caption_frame,
            text=str(datetime.datetime.now().time().strftime('%H:%M')),
            bg="black",
            fg="white",
            justify="right",
            font=("Bahnschrift SemiLight Condensed", 12, "bold"))
        time_label.pack(side="top", anchor="ne")
        # Завантаження зображення (якщо задано)
        if image_path:
            try:
                # Завантажуємо зображення
                # img = tk.PhotoImage(file=image_path) # непрацює з деякими png
                img = Image.open(image_path)
                max_width, max_height = max_image_size
                img = img.resize((max_width, max_height))
                img = ImageTk.PhotoImage(img)
                # Масштабуємо зображення
                width, height = img.width(), img.height()
                # Визначаємо коефіцієнт масштабування
                scale = max(width / max_width, height / max_height)
                if scale > 1:  # Зменшуємо лише, якщо зображення більше за ліміт
                    img = img.subsample(int(scale), int(scale))
                # Додаємо зображення до коробки
                img_label = tk.Label(
                    image_with_caption_frame, image=img, bg="black")
                img_label.image = img  # Зберігаємо посилання, щоб не було GC
                img_label.pack(side="bottom", padx=5, pady=5)
            except Exception as e:
                print(f"Помилка завантаження зображення: {e}")
        # Заголовок
        # random.shuffle(titles)
        title_label = tk.Label(
            inner_frame,
            text=custom_title,  # random.choice(titles),
            bg="black",
            fg=random.choice(colors),
            font=("Bahnschrift SemiLight Condensed", 16, "bold"))
        title_label.pack(pady=(5, 0))
        # Розділювальна риска з кастомним кольором
        canvas = tk.Canvas(inner_frame, height=2,
                           bg="black", highlightthickness=0)
        canvas.pack(fill="x", padx=10)  # Розтягуємо по ширині вікна
        canvas.create_line(0, 1, 500, 1, fill="#2C2E2D",
                           width=2)  # Додаємо лінію
        # Текст повідомлення
        # random.shuffle(messages)
        message_label = tk.Label(
            inner_frame,
            text=custom_text,  # random.choice(messages),
            bg="black",
            fg=random.choice(colors),
            font=("Bahnschrift SemiLight Condensed", 14))
        message_label.pack(pady=(5, 0))
        # Закриваємо вікно через "duration" секунд
        root.after(duration * 1000, root.destroy)
        # Запускаємо вікно
        root.mainloop()
    # параметри сповіщення
    titles = [
        "Пауза для розуму",
        "Час випити води",
        "Коротка перерва",
        "Ей, відпочинь!",
        "Перекур для мозку",
        "Хочеш кави?",
        "Зупинись на хвильку",
        "Нагадування: пауза",
        "Дай мозку перерву",
        "Згадай про себе",
        "Пора розім'ятись",
        "Відпусти клавіатуру",
        "Кава вже стукає",
        "Ще працюєш? Справді?",
        "Просто віддихни",
        "Релакс-зона чекає",
        "Тобі потрібен дзен",
        "Перезарядка мозку",
        "Онови свій процесор",
        "Відпочинь, друже",
        "Мить для перерви",
        "Час глибокого вдиху",
        "Перерва: ініціюй",
        "Досить, зроби паузу",
        "Ти не робот, так?",
        "Клавіатура не втече",
        "Переключись на дзен",
        "Дай пальцям відпочити",
        "Релакс для чемпіона",
        "Майндфулнес-режим",
        "Не згоряй, відпочинь",
        "Вода? Ходи за нею",
        "Робота зачекає",
        "Турбота про тебе",
        "Час для паузи",
        "Твій дзен-таймер",
        "Перезарядись зараз",
        "Онови енергію",
        "Тайм-аут для генія",
        "Зроби паузу швидше",
        "Твій мозок стомився",
        "Пауза: завантаження",
        "Заварю чай і відпочинь",
        "Годі залипати тут",
        "Давай, перерва час",
        "Режим: відпочинок",
        "Свіже повітря кличе",
        "Відпусти і відпочинь",
        "Перерва: активовано",
        "Зроби перерву NOW", ]
    messages = [
        "Ти сильно залипаєш пам'ятаєш?\nЗроби перерву!",
        "Екран не втече, серйозно.\nЗроби перерву!",
        "Просто відірвися на 5 хв.\nМайндфулнес чекає!",
        "Пальці вже втомились?\nРозімни їх на паузі!",
        "Всі геніальні ідеї\nпісля короткої перерви.",
        "Годі, дружок, екран\nне твоє дзеркало!",
        "Монітор теж хоче\nвідпочити, як і ти.",
        "Свіже повітря - твій\nкращий союзник зараз.",
        "Пауза для кави або чаю.\nРеально, це корисно!",
        "Не будь героєм залипання.\nРелакс – твій вибір.",
        "5 хвилин для себе –\nце інвестиція в генія.",
        "Не жени коней, заліпання\nце не твій шлях.",
        "Час подбати про спину.\nПросто розтягнись!",
        "Монітор мовчить, але\nти маєш зробити перерву.",
        "Мозок скаже тобі дякую\nпісля короткої паузи.",
        "Коротка пауза = довга\nенергія для нових справ.",
        "Просто згадай: навіть\nроботи роблять перерви!",
        "Якщо ти читаєш це –\nзроби перерву негайно.",
        "Твій час втікти від екрану\nвже настав, вперед!",
        "Енергія не безкінечна.\nЗроби зарядку зараз.",
        "Вікно не втече, робота\nпочекає, а ти відпочинь.",
        "Екран теж хоче відпочити,\nяк і твій мозок.",
        "Ще працюєш? Може час\nзробити ковток кави?",
        "Просто знай своє місце.\nНа перерві, друже!",
        "Генії беруть паузи.\nХочеш бути генієм?",
        "Воду ти ще не пив?\nТоді перерва зараз!",
        "Твоя спина скаже тобі\nдякую за рух зараз.",
        "Майндфулнес – це круто.\nРелакс зараз!",
        "Просто короткий відпочинок.\nВін змінює все.",
        "Може час подивитись\nна світ поза екраном?",
        "Годі вже! Монітор не\nтвоя друга половинка.",
        "Монітор тобі не скаже:\n'Я теж тебе люблю'.",
        "Твій стілець уже\nплаче без перерви.",
        "Скільки можна?!\nНавіть Wi-Fi хоче відпочити.",
        "Поглянь на руки –\nвони ж просять паузи!",
        "Ти вже побив рекорд\nзалипання? Відпочинь.",
        "Монітор і без тебе\nне вимикається.",
        "Навіть коти знають, що\nсон важливіший за це.",
        "Твоя клавіатура хоче\nрозлучення від пальців.",
        "Твої очі зараз в\nрежимі 'синій екран'.",
        "Монітор не замінить\nобіймів з реальністю.",
        "Навіть у Google є час\nна каву. Що з тобою?",
        "Твій мозок вже хоче\nперезавантаження.",
        "Не забувай: ти не\nробот, а може й робот?",
        "Пора нагадати собі,\nщо ти – не Wi-Fi роутер.",
        "Якщо ти це читаєш,\nчас піти зробити чай.",
        "Годі вже фармити\nсиндром тунелю!",
        "Монітор не виросте в\nпікселях від залипання.",
        "Як щодо 5 хвилин\nзустрічі з реальністю?",
        "Твій стіл за тебе\nхвилюється. Вставай!",
        "Навіть стілець мріє\nпро твоє повернення.",
        "Твоя шия зараз плаче\nз підсвідомості.",
        "Монітор теж хоче трохи\nінтимності без тебе.",
        "Зараз саме час для\nпаузи. Серйозно.",
        "Чому ти так любиш цей\nмонітор? Вийди з ним.",
        "Перестань годувати\nмонітор своїми слізьми.",
        "Твій монітор не стане\nкращим від погляду.",
        "В очах вже 'сніг'? А\nна вулиці є справжній.",
        "Монітор вже бачить\nусе двічі. Відпочинь!",
        "Якщо твій стіл міг\nби говорити, він би кричав.",
        "Поглянь на себе, ти ж\nуже пікселізований!",
        "Відпочинь. Навіть\nТетріс має паузу.",
        "Твій спинний мозок\nобразився на тебе.",
        "Монітору не потрібна\nтвоя безсоння.",
        "Час сказати монітору:\n'Я зараз повернусь'.",
        "Ти не шпигун за\nмоніторами. Відпочинь.",
        "Навіть сервери мають\nчас для техобслуговування.",
        "Перестань фармити\nпрофесійне вигорання.",
        "Твій стілець втомився\nбути твоїм життям.",
        "Монітор тебе любить,\nале не настільки.",
        "Ти виграв марафон\nнерухомості. Відпочинь.",
        "Не псуй собі поставу,\nпотримай світло.",
        "Твій мозок просить\nвітаміну D. Вийди надвір.",
        "Ще трошки і ти станеш\nдругим Робокопом.",
        "Монітор бачить більше,\nніж твої очі. Перерва.",
        "Твій стілець протестує\nмовчки. Встань.",
        "Перестань фармити\nсимптоми тунелю. Час руху.",
        "Клавіатура не буде\nписати за тебе відмову.",
        "Відпочинь! Коврик для\nмиші хоче простору.",
        "Монітор каже, що ти\nзабув, як виглядаєш.",
        "Пора оновити себе до\nверсії 'живий'.",
        "Відпочинок – це\nбезкоштовний апгрейд мозку.",
        "П'ять хвилин на чай –\nце цілий ритуал.",
        "Твій стіл мріє, щоб ти\nнарешті встав.",
        "Твій екран не чекає\nтвоєї відданості.",
        "Монітор вже думає, що\nти – його частина.",
        "Твоя миша хоче\nреваншу в русі.",
        "Не дай монітору зжерти\nусе твоє життя.",
        "Поглянь у дзеркало:\nти вже піксельний!",
        "Монітор не зможе\nсказати 'дякую' за це.",
        "Навіть NPC потребують\nпауз між завданнями.",
        "Твій Wi-Fi хоче, щоб\nти вийшов на вулицю.",
        "Ти заслуговуєш на\nкаву. Зроби це зараз.",
        "Твоя клавіатура хоче\nнаписати тобі лист.",
        "Екран не вирішить\nтвоїх проблем. Відпочинь.",
        "Чому монітор краще за\nсон? Він не краще.",
        "Ти думаєш, що граєш в\n'Життя', але граєш в 'AFK'.",
        "Відпочинок – це як\nлаг для твоїх думок.",
        "Твій екран хоче, щоб\nти його забув на годину.",
        "Монітор тебе не\nзаспокоїть. Лише чай.",
        "Твоя шия зібрала вже\nусі коментарі болю.",
        "Вийди надвір. Монітор\nвсе одно тебе не любить.",
        "Твій CPU зараз на\nнизькому енергозбереженні.",
        "Як щодо перезавантаження\nсвого настрою?",
        "Монітору начхати на\nтвою продуктивність.",
        "Твій мозок хоче кеш-\nочищення. Дій зараз!",
        "Навіть NPC мають свої\nперерви. Що з тобою?",
        "Твій стіл уже не вірить,\nщо ти живий.",
        "Твоя клавіатура хоче\nпоспати, як і ти.",
        "Монітор все одно не\nрозкаже тобі жартів.",
        "Краще 5 хвилин зараз,\nніж 5 годин потім.",
        "Монітор не буде\nсумувати за тобою.",
        "Твій стілець вже мріє\nпро іншу частину тіла.",
        "Твоя шия – це не\nWi-Fi антенна. Відпочинь.",
        "Ти вже відпустив свій\nмонітор? Зроби це зараз.",
        "Перерва – це як Ctrl+Z\nдля втоми.",
        "Монітор не відчинить\nтобі портал до реальності.",
        "Твоя миша хоче пробіжку.\nЧому ні?",
        "Монітор не замінить\nсонця. Іди назустріч йому."]

    random.shuffle(titles)
    title = random.choice(titles) if title == "" else title
    random.shuffle(messages)
    text = random.choice(messages) if text == "" else text
    # Запускаємо сповіщення в окремому потоці
    Thread(target=create_window(title, text)).start()


def countdown():
    while timer_data["remaining"] > 0 and timer_data["running"]:
        time.sleep(1)
        timer_data["remaining"] -= 1
        # Попередження за 5 хвилин
        if timer_data["remaining"] == 300:
            if timer_data["mode"] == "sleep":
                def notify():
                    show_notification(title="💤залишилось 5 хв💤",
                                      text="Комп'ютер переходить\nв сон через 5 хвилин",
                                      duration=10,
                                      image_path=r"icons/bye_sleep.png")
                Thread(target=notify, daemon=True).start()
            else:
                def notify():
                    show_notification(title="👋залишилось 5 хв👋",
                                      text="Комп'ютер вимкнеться\nчерез 5 хвилин",
                                      duration=10,
                                      image_path=r"icons/bye.png")
                Thread(target=notify, daemon=True).start()
        # Попередження за 10s
        if timer_data["remaining"] == 10:
            if timer_data["mode"] == "sleep":
                def notify():
                    show_notification(title="💤Я спати💤",
                                      text="Комп'ютер переходить\nв сон через 10 секунд",
                                      duration=10,
                                      image_path=r"icons/bye_sleep.png")
                Thread(target=notify, daemon=True).start()
            else:
                def notify():
                    show_notification(title="👋ББ👋",
                                      text="Комп'ютер вимикається\nчерез 10 секунд",
                                      duration=10,
                                      image_path=r"icons/bye.png")
                Thread(target=notify, daemon=True).start()

    if timer_data["remaining"] == 0 and timer_data["running"]:
        if timer_data["mode"] == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        else:
            os.system("shutdown /s /t 5")
        timer_data["running"] = False


@app.route('/start_timer', methods=['POST'])
def start_timer():
    data = request.json
    seconds = data['hours'] * 3600 + data['minutes'] * 60 + data['seconds']
    mode = data['mode']

    timer_data["remaining"] = seconds
    timer_data["running"] = True
    timer_data["mode"] = mode

    thread = Thread(target=countdown)
    thread.start()

    return jsonify({"status": "started"})


@app.route('/stop_timer', methods=['POST'])
def stop_timer():
    timer_data["running"] = False
    return jsonify({"status": "stopped"})


@app.route('/get_time')
def get_time():
    return jsonify({
        "remaining": timer_data["remaining"],
        "running": timer_data["running"],
        "mode": timer_data["mode"]
    })


@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    mode = data.get('mode')
    if mode in ['shutdown', 'sleep']:
        timer_data['mode'] = mode
        return jsonify({'status': 'mode updated'})
    return jsonify({'status': 'invalid mode'}), 400


@app.route('/', methods=['GET', 'POST'])
def login():
    if 'authenticated' in session:
        return render_template('index.html')

    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session.permanent = True
            session['authenticated'] = True
            return redirect(url_for('login'))
        else:
            # login_page_head + login_page_body_error
            return render_template('login_page.html')

    # login_page_head + login_page_body
    return render_template('login_page.html')


@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))


@app.route("/get_usage_data", methods=['POST'])
def get_usage_data():
    js_data = request.get_json()
    chart_type = js_data.get("chart_type")
    period = js_data.get("period")
    prevdays = None

    data = pd.read_csv("time_tracker_stat.csv")
    if period == 'week':
        prevdays = 7
    elif period == 'month':
        prevdays = 31
    elif period == 'all_time':
        prevdays = None
    elif re.compile("^\d{4}-\d{2}-\d{2}$").match(period):
        data = data[data['Date'] == period]
    else:
        date = data['Date'].iloc[-1]
        data = data[data['Date'] == date]
    if prevdays is not None:
        last_date = pd.to_datetime(
            data['Date'].iloc[-1]) - pd.Timedelta(days=prevdays)
        date_range = list(pd.date_range(last_date, freq="D", periods=prevdays))
        date_range = [tmsp.strftime("%Y-%m-%d") for tmsp in date_range]
        data = data[data['Date'].isin(date_range)]

    if chart_type == 'total_usage':
        return get_total_usage_data(data)
    elif chart_type == 'apps_usage':
        return get_apps_usage_data(data, period, min_dur=30)
    elif chart_type == 'time_table':
        return get_time_table_data(data, period)
    else:
        return None


@app.route('/media_info')
def media_info():
    try:
        # Створюємо новий event loop для цього запиту
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        media = new_loop.run_until_complete(get_media_info())
        new_loop.close()
    except Exception as e:
        print('ERROR!!!!!!!! media_info() app.py: ', e)
        media = []
    sound_peak = get_active_audio_sessions(threshold=0.005)
    source_peak = []
    for name, peak in sound_peak:
        source_peak.append([name, peak])
    return jsonify({
        "title": media["title"] if media else "Невідома назва",
        "artist": media["artist"] if media else "Невідомий виконавець",
        "playback_status": media["is_playing"] if media else "Playback status not defined",
        "source": source_peak[0][0] if source_peak else "No source",
        "peak": source_peak[0][1] if source_peak else 0.005
    })


@app.route("/control_media", methods=['POST'])
def bridge_to_control_media():
    js_data = request.get_json()
    action = js_data.get("action")
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    msg = new_loop.run_until_complete(control_media(action))
    new_loop.close()
    done_action = {'play': 'media played', 'pause': 'media paused', 'next': 'media switched', 'previous': 'media switched'}
    if msg == 'success':
        print({"status": f"{done_action[action]}"})
        return jsonify({"status": f"{done_action[action]}"})
    else:
        print({'status': msg})
        return jsonify({'status': msg})


@app.route("/blya", methods=["POST"])
def blya():
    fix_keyboard_layout()
    return jsonify({'status': 'ok'})


@app.before_request
def check_session_timeout():
    session.permanent = True  # оновлює час життя при кожному запиті
    if request.path.startswith("/static/public/"):
        return
    if 'authenticated' in session:
        pass  # все ок
    else:
        # якщо сесія протухла — перенаправляємо
        if request.endpoint != 'login':
            return redirect(url_for('login'))


def track_active_window(break_time=2400, save_period=300):
    last_window = None
    start_time = time.time()
    start_time_for_breaks = time.time()
    big_break = time.time()
    last_save_time = time.time()
    log = []
    global running
    running = True

    def update_log(start_time, end_time, last_window, log):
        date_and_time = str(
            datetime.datetime.fromtimestamp(start_time)).split(" ")
        duration = round((end_time - start_time), 2)
        log.append((date_and_time[0],
                    date_and_time[1].split(".")[0],
                    duration,
                    last_window))
        return log

    while running:
        # re.sub видаляє числа в дужках з дефісами та невидимі символи
        window = (re.sub(r"\s*–*\s*\(\d+\)\s*–*\s*|[\u200B-\u200D\u200E\u200F\u202A-\u202E\uFEFF\"|●]",
                         "",
                         GetWindowText(GetForegroundWindow()))).strip()
        # для пустого вікна == "undefined"
        window = "undefined" if window == "" or window == None else window
        if window != last_window:
            end_time = time.time()
            if last_window:
                log = update_log(start_time, end_time, last_window, log)
            # print(f"Активне вікно: {window}")
            last_window = window
            start_time = time.time()
            start_time_for_breaks = time.time()
        elif (time.time() - start_time_for_breaks > break_time) or (time.time() - big_break > break_time + 1800):
            # Thread(target=play_sound).start()  Ідею зі звуковим сповіщенням поки відкидаю. winsound, playsound, pydub не дають бажаного результату
            show_notification(duration=7,
                              image_path=r"icons/break-time by juicy_fish.png")
            start_time_for_breaks = time.time()
            big_break = time.time()
        if time.time() - last_save_time > save_period:
            print("Autosave...")
            end_time = time.time()
            log = update_log(start_time, end_time, last_window, log)
            # чищу логи, щоб при наступному збереженні вони не записались повторно
            log = save_log(log, "time_tracker_stat.csv")  # повертає []
            # збиваю час, щоб при наступному збереженні час додавався до нової точки
            start_time = time.time()
            last_save_time = time.time()
        time.sleep(1)  # перевіряємо кожну секунду


def save_log(usage_log, save_location):
    new_data = pd.DataFrame(
        usage_log, columns=["Date", "StartTime", "Duration(sec)", "Program"])
    data = pd.read_csv(save_location)

    new_data = new_data.groupby(['Date', 'Program']).agg(
        {'StartTime': 'min', 'Duration(sec)': 'sum'}).reset_index()
    new_data.sort_values(['StartTime'], ascending=[True], inplace=True)

    # зрізать дані старші місяця
    # if 14000 рядків тоді все що старіше отого рядка deletаємо

    # скорочую назви програм
    new_data['Program'] = new_data['Program'].apply(lambda x: x.replace(
        "Google Chrome", "GChrome") if 'Google Chrome' in x else x)
    new_data['ShortName'] = new_data['Program'].apply(lambda x: (
        x[:20] + " ... " + x[-25:]) if len(x) > 50 else x)

    # пишу дні тижня
    weekdays_ua = {0: "Понеділок", 1: "Вівторок", 2: "Середа",
                   3: "Четвер", 4: "П\'ятниця", 5: "Субота", 6: "Неділя"}
    new_data['WeekDay'] = pd.to_datetime(new_data['Date']).apply(
        lambda d: weekdays_ua[(d).weekday()])

    # вичленить big app name
    def cut_to_big(program):
        big_apps = ["- YouTube -", "- Twitch -", "- Cursor", "- GChrome"]
        for big_name in big_apps:
            if big_name in program:
                return big_name.split(" ")[1]
        return 'Others'

    new_data['BigApp'] = new_data['Program'].apply(lambda x: cut_to_big(x))

    # призначить колір
    def set_color(name):
        colors_map = {"YouTube": "#FF0033",  # червоний
                      "Twitch": "#9147FF",  # фіолетовий
                      "Cursor": "#ADBAB6",  # сірий
                      "GChrome": "#8DBF6C",  # зелений
                      }
        try:
            return colors_map[name]
        except KeyError:
            return "#757575"  # попільно-коричневий

    new_data['Color'] = new_data['BigApp'].apply(lambda x: set_color(x))

    data = pd.concat([data, new_data], ignore_index=True)
    data.to_csv(save_location, index=False)
    saved_at = str(datetime.datetime.fromtimestamp(time.time())).split(" ")[1].split(".")[0]
    print(f"{saved_at} Logs Saved.")
    return []


def get_time_table_data(data, period):
    if period != 'today' and re.compile("^\d{4}-\d{2}-\d{2}$").match(period) is None:
            data = data.groupby(['Date', 'Program', 'ShortName', 'Color', 'WeekDay']).agg(
                {'StartTime': 'min', 'Duration(sec)': 'sum'}).reset_index()
    else:
        data['StartTime'] = pd.to_datetime(
            data['Date'] + ' ' + data['StartTime'])
        data['Duration(sec)'] = pd.to_timedelta(data['Duration(sec)'], unit='s')
        data['EndTime'] = data['StartTime'] + data['Duration(sec)']
        data = data.sort_values(
            ['Program', 'StartTime']).reset_index(drop=True)
        group_ids = []
        group_id = 0
        for i in range(len(data)):
            if i == 0:
                group_ids.append(group_id)
                continue
            same_name = data.loc[i, 'Program'] == data.loc[i - 1, 'Program']
            time_diff = (data.loc[i, 'StartTime'] -
                         data.loc[i - 1, 'EndTime']).total_seconds()
            # Нова група, якщо інше ім’я або пауза ≥ 1 сек
            if not same_name or time_diff >= 30:
                group_id += 1
            group_ids.append(group_id)
        data['group_id'] = group_ids

        data = data.groupby(['Program', 'group_id', 'ShortName', 'Color', 'WeekDay']).agg({
            'StartTime': 'first',
            'EndTime': 'last',
            'Duration(sec)': 'sum',
            'group_id': 'count'
        }).rename(columns={'group_id': 'entries'}).reset_index()
        # повертаю до колишнього формату
        data['Date'] = data['StartTime'].apply(lambda x: x.strftime('%Y-%m-%d'))
        data['StartTime'] = data['StartTime'].dt.strftime('%H:%M:%S')
        data['Duration(sec)'] = data['Duration(sec)'].dt.total_seconds()

    data['TotalDuration(sec)'] = data.groupby('Program')[
        'Duration(sec)'].transform('sum')
    data.sort_values(['TotalDuration(sec)'], ascending=True, inplace=True)
    data = data[data['Program'].isin(data['Program'].unique()[-25:])]
    return data.to_json(orient='records')


def get_apps_usage_data(data, period, min_dur=30):
    if period != 'today' and re.compile("^\d{4}-\d{2}-\d{2}$").match(period) is None:
        data['Date'] = str(data['Date'].min()) + " – " + \
            str(data['Date'].max())
        data['WeekDay'] = 'Never mind'
    data = data.groupby(['Program', 'ShortName', 'Date', 'WeekDay', 'Color'])[
        'Duration(sec)'].sum().reset_index()
    # data = data[data['Duration(sec)'] > min_dur]
    data.sort_values(['Duration(sec)', 'Program'],
                     ascending=True, inplace=True)
    data = data.iloc[-25:, :]
    return data.to_json(orient='records')


def get_total_usage_data(data):
    data = data.groupby(['BigApp', 'Color'])[
        'Duration(sec)'].sum().reset_index()
    return data.to_json(orient='records')


if __name__ == '__main__':
    Thread(target=track_active_window, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)


# щоб при запуску або вимкненню сервака всіх розлогінювало як і по таймеру

# якщо у мене буде доступ до медіа тоді можна буде і зробити окрему стату по улюбленим треках
