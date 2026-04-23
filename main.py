import flet as ft
import json
import os

# --- РАБОТА С ХРАНИЛИЩЕМ ---
DB_FILE = "messenger_data.json"

def save_to_db(key, value):
    data = {"user_name": "Гость", "history": []}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: data = json.load(f)
            except: pass
    data[key] = value
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def get_from_db(key, default=None):
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f).get(key, default)
            except: return default
    return default

# --- ОСНОВНОЙ КОД ---
def main(page: ft.Page):
    page.title = "Flet Online Chat + History"
    page.bgcolor = "black"

    chat_display = ft.Column(scroll="always", expand=True)
    contacts_column = ft.Column() # Список людей онлайн
    
    # Вспомогательная функция для отрисовки сообщения
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

    # 1. ЗАГРУЗКА ИСТОРИИ ПРИ СТАРТЕ
    history = get_from_db("history", [])
    for msg in history:
        add_message_ui(msg["user"], msg["text"], is_history=True)

    # 2. ОБРАБОТКА PUB/SUB (Онлайн события)
    def on_broadcast(data):
        if data["type"] == "chat":
            add_message_ui(data["user"], data["text"])
            # Сохраняем в локальную историю
            curr_history = get_from_db("history", [])
            curr_history.append({"user": data["user"], "text": data["text"]})
            save_to_db("history", curr_history)
            
        elif data["type"] == "join":
            # Добавляем в список онлайн
            contacts_column.controls.append(
                ft.Text(f"● {data['user']}", color="green", size=12)
            )
            chat_display.controls.append(
                ft.Text(f" Пользователь {data['user']} вошел", size=10, italic=True, color="grey")
            )
        
        page.update()

    page.pubsub.subscribe(on_broadcast)

    # 3. ПАНЕЛЬ УПРАВЛЕНИЯ
    user_name = get_from_db("user_name", "Гость")
    name_input = ft.TextField(label="Твой ник", value=user_name, height=45, text_size=12)
    msg_input = ft.TextField(hint_text="Сообщение...", expand=True)

    def send_click(e):
        if msg_input.value:
            page.pubsub.send_all({
                "type": "chat", 
                "user": get_from_db("user_name", "Гость"), 
                "text": msg_input.value
            })
            msg_input.value = ""
            page.update()

    def change_name_click(e):
        if name_input.value:
            save_to_db("user_name", name_input.value)
            page.pubsub.send_all({"type": "join", "user": name_input.value})
            page.update()

    # 4. ИНТЕРФЕЙС
    page.add(
        ft.Row([
            # Левая панель (Профиль + Онлайн)
            ft.Container(
                content=ft.Column([
                    ft.Text("ПРОФИЛЬ", weight="bold", size=14),
                    name_input,
                    ft.ElevatedButton("Сменить ник", on_click=change_name_click),
                    ft.Divider(),
                    ft.Text("СЕЙЧАС В СЕТИ", weight="bold", size=12),
                    contacts_column,
                ], spacing=10),
                width=180, bgcolor="grey900", padding=15
            ),
            # Правая панель (Чат)
            ft.Column([
                ft.Container(content=chat_display, expand=True, padding=10),
                ft.Row([
                    msg_input, 
                    ft.IconButton(ft.Icons.SEND, on_click=send_click, icon_color="blue")
                ])
            ], expand=True)
        ], expand=True)
    )

    # При входе уведомляем всех
    page.pubsub.send_all({"type": "join", "user": user_name})

ft.app(target=main)