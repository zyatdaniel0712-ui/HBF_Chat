import flet as ft
import os
import random
import threading
from supabase import create_client

# --- НАСТРОЙКИ (ВСТАВЬ СВОИ) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    page.title = "C:\\SYSTEM\\HBF-FLUD\\CHAT.EXE"
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")
    
    # 1. Инициализация ID пользователя
    if not page.client_storage.get("user_nickname"):
        page.client_storage.set("user_nickname", f"HACKER_{random.randint(1000, 9999)}")
    
    page.last_msg_id = 0

    # Элементы интерфейса чата
    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(
        label="TYPE COMMAND...", 
        expand=True, 
        border_color="#00FF00", 
        color="#00FF00"
    )

    # Функция фоновой проверки новых сообщений
    def check_updates():
        try:
            my_name = page.client_storage.get("user_nickname")
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != my_name:
                    chat_display.controls.append(
                        ft.Text(f"[{msg['user_name']}]:> {msg['text']}", color="#00FF00")
                    )
                page.last_msg_id = msg["id"]
            page.update()
        except:
            pass
        threading.Timer(3, check_updates).start()

    # Функция отправки
    def send_msg(e):
        my_name = page.client_storage.get("user_nickname")
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                res = supabase.table("messages").insert({"user_name": my_name, "text": text}).execute()
                if res.data:
                    page.last_msg_id = res.data[0]["id"]
                chat_display.controls.append(ft.Text(f"[{my_name}]:> {text}", color="#008800"))
            except:
                chat_display.controls.append(ft.Text("!! SEND ERROR", color="red"))
            page.update()

    # --- ПЕРЕКЛЮЧЕНИЕ СТРАНИЦ ---
    
    def show_settings(e):
        page.controls.clear()
        # Поле для смены имени
        new_name_input = ft.TextField(
            label="EDIT NICKNAME", 
            value=page.client_storage.get("user_nickname"),
            border_color="#00FF00", color="#00FF00"
        )
        
        def save_and_back(e):
            page.client_storage.set("user_nickname", new_name_input.value)
            show_chat_ui()

        page.add(
            ft.Text("--- SETTINGS ---", color="#00FF00", size=20),
            new_name_input,
            ft.Row([
                ft.ElevatedButton("SAVE & EXIT", on_click=save_and_back),
                ft.ElevatedButton("CANCEL", on_click=lambda _: show_chat_ui())
            ])
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        my_name = page.client_storage.get("user_nickname")
        page.add(
            ft.Row([
                ft.Text(f"ID: {my_name}", color="#00FF00", weight="bold"),
                ft.IconButton(ft.Icons.SETTINGS, on_click=show_settings, icon_color="#00FF00")
            ], alignment="spaceBetween"),
            ft.Divider(color="#004400"),
            ft.Container(content=chat_display, expand=True),
            ft.Row([
                ft.Text(">", color="#00FF00"),
                msg_input,
                ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")
            ])
        )
        page.update()

    # Сначала рисуем чат
    show_chat_ui()
    # Запускаем бесконечный цикл проверки
    check_updates()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
