import flet as ft
import os
import random
import threading
from supabase import create_client

# --- 1. ТВОИ КЛЮЧИ ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co" # Проверь, что тут твой URL
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"             # Проверь, что тут твой KEY
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # Генерация ника для текущей сессии
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"HACKER_{random.randint(1000, 9999)}"
    
    page.last_msg_id = 0
    page.title = "C:\\SYSTEM\\HBF-FLUD\\CHAT.EXE"
    page.bgcolor = "black"

    # Список сообщений
    chat_display = ft.Column(scroll="always", expand=True)
    
    # Поле ввода
    msg_input = ft.TextField(
        label="TYPE COMMAND", 
        expand=True, 
        border_color="#00FF00", 
        color="#00FF00"
    )

    # Функция отрисовки сообщения (с поддержкой голубого Кевина)
    def render_msg(user, text, is_history=False):
        if user.lower() == "кевин":
            name_color = "cyan"
        else:
            name_color = "#00FF00" if not is_history else "#008800"
            
        chat_display.controls.append(
            ft.Text(f"[{user}]:> {text}", color=name_color, font_family="Courier New")
        )
        page.update()

    # --- 3. ОБНОВЛЕНИЕ ---
    def check_updates():
        try:
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != page.my_user_nick:
                    render_msg(msg["user_name"], msg["text"])
                page.last_msg_id = msg["id"]
            page.update()
        except:
            pass
        threading.Timer(3, check_updates).start()

    # --- 4. ОТПРАВКА ---
    def send_msg(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                res = supabase.table("messages").insert({"user_name": page.my_user_nick, "text": text}).execute()
                # Обработка ID для старых версий
                if isinstance(res.data, list) and len(res.data) > 0:
                    page.last_msg_id = res.data[0]["id"]
                
                render_msg(page.my_user_nick, text)
            except:
                chat_display.controls.append(ft.Text("!! DB ERROR", color="red"))
            page.update()

    # --- 5. ИНТЕРФЕЙС ---
    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="EDIT NICKNAME", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        
        def save_name(e):
            if name_edit.value:
                page.my_user_nick = name_edit.value
            show_chat_ui()

        page.add(
            ft.Text("--- SETTINGS ---", color="#00FF00", size=18, weight="bold"),
            name_edit,
            ft.Row([
                ft.ElevatedButton("APPLY", on_click=save_name),
                ft.ElevatedButton("BACK", on_click=lambda _: show_chat_ui())
            ])
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        
        # СТАРЫЙ ДИЗАЙН: ВЕРХНЯЯ НАДПИСЬ
        header = ft.Column([
            ft.Text("--- TERMINAL CHAT SYSTEM v1.0 ONLINE ---", color="#00FF00", size=18, weight="bold"),
            ft.Row([
                ft.Text(f"ID: {page.my_user_nick}", color="#008800", size=12),
                ft.IconButton(ft.Icons.SETTINGS, on_click=show_settings, icon_color="#00FF00")
            ], alignment="spaceBetween"),
            ft.Divider(color="#004400"),
        ])

        page.add(
            header,
            ft.Container(content=chat_display, expand=True),
            ft.Row([
                ft.Text(">", color="#00FF00", size=20),
                msg_input,
                ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")
            ])
        )
        
        # Загрузка истории при старте (один раз)
        if page.last_msg_id == 0:
            try:
                res = supabase.table("messages").select("*").order("created_at").limit(10).execute()
                for msg in res.data:
                    render_msg(msg["user_name"], msg["text"], is_history=True)
                    page.last_msg_id = msg["id"]
            except: pass
        page.update()

    show_chat_ui()
    
    # Запуск фонового процесса
    if not hasattr(page, "thread_running"):
        check_updates()
        page.thread_running = True

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
