import sys
import os
import customtkinter as ctk
import requests
from PIL import Image, ImageFilter
from io import BytesIO
import json
from datetime import datetime
from customtkinter import CTkImage

# ------------------------------------------------------------
# Функция для получения правильного пути к ресурсам (для PyInstaller)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ------------------------------------------------------------
API_KEY = "249f1386b3a04dba97653827240609"
SETTINGS_FILE = resource_path("settings.json")  # сохраняем в папке с exe

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"city": "Chisinau"}

def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f)

settings = load_settings()
CITY = settings["city"]

def make_url(city):
    return f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=2&lang=ru"

URL = make_url(CITY)
data = None

def fetch():
    global data
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            data = response.json()
        else:
            data = None
    except:
        data = None

fetch()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Meteo")
root.geometry("1200x800")
root.attributes("-alpha", 0.0)

# Установка иконки окна
icon_path = resource_path("weather-app.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)

# Фоновое изображение
bg_image_path = resource_path("Weather.png")
try:
    bg = Image.open(bg_image_path).resize((1200, 800))
    blurred = bg.filter(ImageFilter.GaussianBlur(12))
    bg_ctk = CTkImage(light_image=blurred, dark_image=blurred, size=(1200, 800))
    bg_label = ctk.CTkLabel(root, image=bg_ctk, text="")
    bg_label.place(relx=0.5, rely=0.5, anchor="center")
except Exception:
    blurred = None
    root.configure(fg_color="#1a1a1a")

# Основная карточка
CARD_WIDTH = 1000
CARD_HEIGHT = 700
frame = ctk.CTkFrame(root, corner_radius=40, fg_color=("white", "#222222"),
                     width=CARD_WIDTH, height=CARD_HEIGHT)
frame.place(relx=0.5, rely=0.5, anchor="center")
frame.pack_propagate(False)

def create_blurred_card():
    if blurred is None:
        return
    card_bg = blurred.crop((100, 100, 1100, 700))
    card_blurred = card_bg.filter(ImageFilter.GaussianBlur(20))
    card_ctk = CTkImage(light_image=card_blurred, dark_image=card_blurred, size=(CARD_WIDTH, CARD_HEIGHT))
    card_label = ctk.CTkLabel(frame, image=card_ctk, text="")
    card_label.place(relx=0.5, rely=0.5, anchor="center")

def load_icon(url):
    try:
        full_url = "https:" + url if not url.startswith("https") else url
        img = Image.open(BytesIO(requests.get(full_url).content)).convert("RGBA")
        return CTkImage(light_image=img, dark_image=img, size=(64, 64))
    except:
        return None

def toggle_theme():
    current = ctk.get_appearance_mode()
    ctk.set_appearance_mode("light" if current == "Dark" else "dark")

def change_city():
    global CITY, URL, data
    dialog = ctk.CTkInputDialog(text="Введите город:", title="Город")
    new_city = dialog.get_input()
    if new_city:
        CITY = new_city
        settings["city"] = CITY
        save_settings(settings)
        URL = make_url(CITY)
        fetch()
        draw()

def fade_out():
    alpha = root.attributes("-alpha")
    if alpha > 0:
        alpha -= 0.05
        root.attributes("-alpha", alpha)
        root.after(50, fade_out)
    else:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", fade_out)

def fade_in(alpha=0.0):
    if alpha < 1.0:
        root.attributes("-alpha", alpha)
        root.after(50, lambda: fade_in(alpha + 0.05))
    else:
        root.attributes("-alpha", 1.0)

def scale_in(scale=0.1):
    if scale < 0.85:
        frame.place(relx=0.5, rely=0.5, anchor="center",
                    relwidth=scale, relheight=scale)
        root.after(50, lambda: scale_in(scale + 0.05))
    else:
        bounce()

def bounce(step=0):
    if step == 0:
        frame.place(relx=0.5, rely=0.5, anchor="center",
                    relwidth=0.90, relheight=0.80)
        root.after(120, lambda: bounce(1))
    elif step == 1:
        frame.place(relx=0.5, rely=0.5, anchor="center",
                    relwidth=0.80, relheight=0.70)
        root.after(120, lambda: bounce(2))
    elif step == 2:
        frame.place(relx=0.5, rely=0.5, anchor="center",
                    relwidth=0.85, relheight=0.75)
        frame.configure(width=CARD_WIDTH, height=CARD_HEIGHT)

def format_day(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    return f"{dt.strftime('%d.%m')} ({days[dt.weekday()]})"

def draw():
    for widget in frame.winfo_children():
        widget.destroy()
    create_blurred_card()

    if data and "forecast" in data:
        city_name = data['location']['name']
        country = data['location']['country']
        header = ctk.CTkLabel(frame, text=f"🌍 {city_name}, {country}",
                              font=("Segoe UI", 28, "bold", "italic"))
        header.pack(pady=(20, 5))

        columns_frame = ctk.CTkFrame(frame, fg_color="transparent")
        columns_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # День 1
        day0 = data['forecast']['forecastday'][0]
        col0 = ctk.CTkFrame(columns_frame, fg_color="transparent", corner_radius=20,
                            border_width=2, border_color=("gray70", "gray30"))
        col0.pack(side="left", padx=10, fill="both", expand=True)

        date0 = format_day(day0['date'])
        day_name0 = datetime.strptime(day0['date'], "%Y-%m-%d").strftime("%A")
        days_ru = {"Monday":"Понедельник","Tuesday":"Вторник","Wednesday":"Среда",
                   "Thursday":"Четверг","Friday":"Пятница","Saturday":"Суббота",
                   "Sunday":"Воскресенье"}
        title0 = ctk.CTkLabel(col0, text=f"📅 {date0} – {days_ru.get(day_name0, day_name0)}",
                              font=("Segoe UI", 20, "bold"))
        title0.pack(pady=(15,5))

        icon0 = load_icon(day0['day']['condition']['icon'])
        if icon0:
            lbl_icon0 = ctk.CTkLabel(col0, image=icon0, text="")
            lbl_icon0.pack(pady=5)
        temp0 = ctk.CTkLabel(col0, text=f"🌡️ {day0['day']['avgtemp_c']}°C",
                             font=("Segoe UI", 24, "bold", "italic"))
        temp0.pack(pady=5)

        lbl_hours0 = ctk.CTkLabel(col0, text="Почасовой прогноз",
                                  font=("Segoe UI", 18, "bold"))
        lbl_hours0.pack(pady=(10,5))

        hours_frame0 = ctk.CTkScrollableFrame(col0, fg_color="transparent", height=320, width=420)
        hours_frame0.pack(pady=10, padx=10, fill="both", expand=True)

        for h in day0['hour']:
            hour_text = f"{h['time'][-5:]} — {h['temp_c']}°C, {h['condition']['text']}"
            lbl = ctk.CTkLabel(hours_frame0, text=hour_text,
                               font=("Segoe UI", 16, "bold", "italic"),
                               anchor="w", justify="left")
            lbl.pack(fill="x", padx=10, pady=5)

        # День 2
        if len(data['forecast']['forecastday']) > 1:
            day1 = data['forecast']['forecastday'][1]
            col1 = ctk.CTkFrame(columns_frame, fg_color="transparent", corner_radius=20,
                                border_width=2, border_color=("gray70", "gray30"))
            col1.pack(side="right", padx=10, fill="both", expand=True)

            date1 = format_day(day1['date'])
            day_name1 = datetime.strptime(day1['date'], "%Y-%m-%d").strftime("%A")
            title1 = ctk.CTkLabel(col1, text=f"📅 {date1} – {days_ru.get(day_name1, day_name1)}",
                                  font=("Segoe UI", 20, "bold"))
            title1.pack(pady=(15,5))

            icon1 = load_icon(day1['day']['condition']['icon'])
            if icon1:
                lbl_icon1 = ctk.CTkLabel(col1, image=icon1, text="")
                lbl_icon1.pack(pady=5)
            temp1 = ctk.CTkLabel(col1, text=f"🌡️ {day1['day']['avgtemp_c']}°C",
                                 font=("Segoe UI", 24, "bold", "italic"))
            temp1.pack(pady=5)

            lbl_hours1 = ctk.CTkLabel(col1, text="Почасовой прогноз",
                                      font=("Segoe UI", 18, "bold"))
            lbl_hours1.pack(pady=(10,5))

            hours_frame1 = ctk.CTkScrollableFrame(col1, fg_color="transparent", height=320, width=420)
            hours_frame1.pack(pady=10, padx=10, fill="both", expand=True)

            for h in day1['hour']:
                hour_text = f"{h['time'][-5:]} — {h['temp_c']}°C, {h['condition']['text']}"
                lbl = ctk.CTkLabel(hours_frame1, text=hour_text,
                                   font=("Segoe UI", 16, "bold", "italic"),
                                   anchor="w", justify="left")
                lbl.pack(fill="x", padx=10, pady=5)
        else:
            col1 = ctk.CTkFrame(columns_frame, fg_color="transparent", corner_radius=20,
                                border_width=2, border_color=("gray70", "gray30"))
            col1.pack(side="right", padx=10, fill="both", expand=True)
            no_data = ctk.CTkLabel(col1, text="Прогноз на завтра\nнедоступен",
                                   font=("Segoe UI", 20, "bold"), text_color="red")
            no_data.pack(expand=True)
    else:
        error_label = ctk.CTkLabel(frame, text="Не удалось загрузить погоду.\nПроверьте интернет или город.",
                                   font=("Segoe UI", 24, "bold"), text_color="red")
        error_label.pack(expand=True)

    buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
    buttons_frame.pack(side="bottom", pady=20)

    btn_city = ctk.CTkButton(buttons_frame, text="🏙️ Сменить город", command=change_city,
                             corner_radius=12, border_width=2,
                             fg_color="#2E86C1", hover_color="#5DADE2",
                             text_color="white", width=200, height=50,
                             font=("Segoe UI", 18, "bold", "italic"))
    btn_city.pack(side="left", padx=20)

    btn_theme = ctk.CTkButton(buttons_frame, text="🎨 Сменить тему", command=toggle_theme,
                              corner_radius=12, border_width=2,
                              fg_color="#28B463", hover_color="#58D68D",
                              text_color="white", width=200, height=50,
                              font=("Segoe UI", 18, "bold", "italic"))
    btn_theme.pack(side="left", padx=20)

draw()
fade_in()
scale_in()
root.mainloop()