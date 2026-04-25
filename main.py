import flet as ft
import os
import random
import threading
from supabase import create_client

# --- 1. ТВОИ КЛЮЧИ (ВСТАВЬ СВОИ!) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # --- 2. ГЕНЕРАЦИЯ ИМЕНИ (ИСПРАВЛЕНИЕ ОШИБКИ) ---
    # Мы используем page.session вместо client_storage, чтобы не было ошибки на Render
    if not page.session.get("my_user_nick"):
        page.session.set("my_user_nick", f"HACKER_{random.randint(1000, 9999)}")
    
    # Запоминаем ID последнего сообщения
    page.last_msg_id = 0

    # Настройки страницы
    page.title = "C:\\SYSTEM\\HBF-FLUD\\CHAT.EXE"
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    # Элементы интерфейса
    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(
        label="ENTER COMMAND...", 
        expand=True, 
        border_color="#00FF00", 
        color="#00FF00"
    )

    # --- 3. ФУНКЦИЯ ОБНОВЛЕНИЯ ЧАТА ---
    def check_updates():
        try:
            current_nick = page.session.get("my_user_nick")
            # Запрашиваем новые сообщения из базы
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                # Если сообщение чужое - показываем
                if msg["user_name"] != current_nick:
                    chat_display.controls.append(
                        ft.Text(f"[{msg['user_name']}]:> {msg['text']}", color="#00FF00")
                    )
                page.last_msg_id = msg["id"]
            page.update()
        except:
            pass
        # Повтор через 3 секунды
        threading.Timer(3, check_updates).start()

    # --- 4. ФУНКЦИЯ ОТПРАВКИ ---
    def send_msg(e):
        current_nick = page.session.get("my_user_nick")
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                # Сохраняем в облако
                res = supabase.table("messages").insert({"user_name": current_nick, "text": text}).execute()
                if res.data:
                    page.last_msg_id = res.data[0]["id"]
                # Рисуем у себя
                chat_display.controls.append(ft.Text(f"[{current_nick}]:> {text}", color="#008800"))
            except:
                chat_display.controls.append(ft.Text("!! DATABASE ERROR", color="red"))
            page.update()

    # --- 5. СТРАНИЦЫ ---

    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(
            label="EDIT NICKNAME", 
            value=page.session.get("my_user_nick"),
            border_color="#00FF00", color="#00FF00"
        )
        
        def save_name(e):
            page.session.set("my_user_nick", name_edit.value)
            show_chat_ui()

        page.add(
            ft.Text("--- SETTINGS ---", color="#00FF00", size=20),
            name_edit,
            ft.Row([
                ft.ElevatedButton("SAVE", on_click=save_name),
                ft.ElevatedButton("BACK", on_click=lambda _: show_chat_ui())
            ])
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        current_nick = page.session.get("my_user_nick")
        page.add(
            ft.Row([
                ft.Text(f"SESSION_ID: {current_nick}", color="#00FF00", weight="bold"),
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

    # Запуск
    show_chat_ui()
    check_updates()

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
