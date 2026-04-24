import flet as ft
import os
import threading
import random
from supabase import create_client

# --- НАСТРОЙКИ ОБЛАКА (SUPABASE) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co" 
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # Стиль терминала
    page.title = "C:\\SYSTEM\\CHAT.EXE"
    page.bgcolor = "#000000"
    page.theme = ft.Theme(font_family="Courier New")
    page.padding = 20

    # Генерируем уникальное имя для этой вкладки
    my_id = f"User_{random.randint(1000, 9999)}"
    page.last_msg_id = 0 # Для отслеживания новых сообщений

    chat_display = ft.ListView(expand=True, spacing=5, auto_scroll=True)

    def add_line(text, color="#00FF00", bold=False):
        chat_display.controls.append(
            ft.Text(text, color=color, font_family="Courier New", weight="bold" if bold else "normal")
        )
        page.update()

    # 1. ФУНКЦИЯ ПРОВЕРКИ НОВЫХ СООБЩЕНИЙ (Polling)
    def check_updates():
        try:
            # Запрашиваем только те, что появились после page.last_msg_id
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != my_id:
                    add_line(f"[{msg['user_name']}]:> {msg['text']}")
                page.last_msg_id = msg["id"]
        except:
            pass
        # Повтор через 3 секунды
        threading.Timer(3, check_updates).start()

    # 2. ОТПРАВКА СООБЩЕНИЯ
    msg_input = ft.TextField(
        label="TYPE COMMAND...",
        border_color="#00FF00",
        color="#00FF00",
        cursor_color="#00FF00",
        label_style=ft.TextStyle(color="#008800"),
        expand=True,
        on_submit=lambda _: send_click(None)
    )

    def send_click(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            page.update()
            try:
                # Пишем в облако
                res = supabase.table("messages").insert({"user_name": my_id, "text": text}).execute()
                # Сразу обновляем наш ID последнего сообщения
                if res.data:
                    page.last_msg_id = res.data[0]["id"]
                # Показываем у себя
                add_line(f"[{my_id}]:> {text}", color="#00AA00")
            except Exception as ex:
                add_line(f"!! SYSTEM ERROR: {ex}", color="red")

    # 3. ИНТЕРФЕЙС
    page.add(
        ft.Text("--- TERMINAL ACCESS GRANTED ---", color="#00FF00", size=18, weight="bold"),
        ft.Text(f"CONNECTION SECURE. YOUR_ID: {my_id}", color="#008800", size=12),
        ft.Divider(color="#004400"),
        ft.Container(content=chat_display, expand=True),
        ft.Row([
            ft.Text(">", color="#00FF00", size=20),
            msg_input,
            ft.IconButton(ft.Icons.KEYBOARD_ARROW_RIGHT, on_click=send_click, icon_color="#00FF00")
        ])
    )

    # ЗАПУСК ФОНОВОЙ ПРОВЕРКИ
    check_updates()
    add_line("SYSTEM: INITIALIZING DATABASE...", color="#004400")

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
