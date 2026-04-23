import flet as ft
import os
import json
from supabase import create_client

# --- НАСТРОЙКИ ОБЛАКА (SUPABASE) ---
# Возьми эти данные в Project Settings -> API
SUPABASE_URL = "https://nesxjcdhqgstahwfnrba.supabase.co" 
SUPABASE_KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Файл для локального хранения ника (на устройстве)
SETTINGS_FILE = "user_settings.json"

def save_local_name(name):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_name": name}, f)

def get_local_name():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("user_name", "Гость")
    return "Гость"

# --- ОСНОВНОЙ КОД ПРИЛОЖЕНИЯ ---
def main(page: ft.Page):
    page.title = "Flet Cloud Messenger"
    page.bgcolor = "black"

    # Загружаем ник из локального файла
    user_name = get_local_name()

    chat_display = ft.Column(scroll="always", expand=True)
    contacts_column = ft.Column()

    # Вспомогательная функция для отрисовки сообщения в UI
    def add_message_ui(user, text, is_history=False):
        chat_display.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(user, size=10, color="blue" if not is_history else "grey", weight="bold"),
                    ft.Text(text, size=14, color="white"),
                ], spacing=2),
                bgcolor="grey800", padding=8, border_radius=10,
            )
        )

    # 1. ЗАГРУЗКА ИСТОРИИ ИЗ ОБЛАКА ПРИ СТАРТЕ
    try:
        response = supabase.table("messages").select("*").order("created_at").execute()
        for msg in response.data:
            add_message_ui(msg["user_name"], msg["text"], is_history=True)
    except Exception as ex:
        print(f"Ошибка загрузки истории: {ex}")

    # 2. ОБРАБОТКА PUB/SUB (Обмен сообщениями в реальном времени)
    def on_broadcast(data):
        if data["type"] == "chat":
            add_message_ui(data["user"], data["text"])
        elif data["type"] == "join":
            contacts_column.controls.append(ft.Text(f"● {data['user']}", color="green", size=12))
            chat_display.controls.append(ft.Text(f" Пользователь {data['user']} вошел", size=10, italic=True, color="grey"))
        page.update()

    page.pubsub.subscribe(on_broadcast)

    # 3. ЭЛЕМЕНТЫ УПРАВЛЕНИЯ
    name_input = ft.TextField(label="Твой ник", value=user_name, height=45, text_size=12)
    msg_input = ft.TextField(hint_text="Сообщение...", expand=True)

    def send_click(e):
        if msg_input.value:
            current_user = get_local_name()
            # Сохраняем в облачную базу Supabase
            try:
                supabase.table("messages").insert({
                    "user_name": current_user,
                    "text": msg_input.value
                }).execute()
            except Exception as ex:
                print(f"Ошибка сохранения в базу: {ex}")

            # Рассылаем всем, кто сейчас онлайн
            page.pubsub.send_all({
                "type": "chat", 
                "user": current_user, 
                "text": msg_input.value
            })
            msg_input.value = ""
            page.update()

    def change_name_click(e):
        if name_input.value:
            save_local_name(name_input.value)
            page.pubsub.send_all({"type": "join", "user": name_input.value})
            page.update()

    # 4. ИНТЕРФЕЙС
    page.add(
        ft.Row([
            # Левая панель (Настройки ника и онлайн)
            ft.Container(
                content=ft.Column([
                    ft.Text("ПРОФИЛЬ", weight="bold", size=14, color="white"),
                    name_input,
                    ft.ElevatedButton("ОК", on_click=change_name_click),
                    ft.Divider(),
                    ft.Text("ОНЛАЙН", weight="bold", size=12, color="white"),
                    contacts_column,
                ], spacing=10),
                width=180, bgcolor="grey900", padding=15
            ),
            # Правая панель (Чат)
            ft.Column([
                ft.Container(content=chat_display, expand=True, padding=10),
                ft.Row([
                    msg_input, 
                    ft.IconButton(ft=Icons.SEND, on_click=send_click, icon_color="blue")
                ])
            ], expand=True)
        ], expand=True)
    )

    # Уведомляем о входе
    page.pubsub.send_all({"type": "join", "user": user_name})

# ЗАПУСК (Настройки для Render)
if __name__ == "__main__":
    # На Render переменная PORT подставится автоматически
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)

