import flet as ft
import os
import random
import threading
from supabase import create_client

# --- 1. ТВОИ КЛЮЧИ (ПРОВЕРЬ ИХ!) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # Генерация ника (обход ошибок старой версии)
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"
    
    page.last_msg_id = 0
    page.title = "C:\\SYSTEM\\HBF-CHAT\\CHAT.EXE"
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="TYPE COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # ФУНКЦИЯ ОТРИСОВКИ СООБЩЕНИЯ (Буквы вместо картинок)
    def render_message(user, text, is_history=False):
        user_lower = user.lower()
        
        # Определяем цвет ника и аватарки
        if user_lower == "кевин":
            main_color = "cyan"
        elif user_lower == "хан" or user_lower == "солвер":
            main_color = "red"
        elif user_lower == "система":
            main_color = "black"
        else:
            main_color = "#00FF00" if not is_history else "#008800"

        # Создаем текстовую аватарку (первая буква ника)
        first_letter = user[0].upper() if user else "?"
        avatar = ft.Container(
            content=ft.Text(first_letter, color="black", weight="bold", size=14),
            bgcolor=main_color,
            width=30,
            height=30,
            border_radius=15,
            alignment=ft.alignment.center
        )

        # Собираем бабл сообщения
        chat_display.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        avatar,
                        ft.Text(f"[{user}]:> {text}", color=main_color, font_family="Courier New")
                    ], tight=True, vertical_alignment="center", spacing=10),
                    bgcolor="#1c1c1c",
                    padding=10,
                    border_radius=15,
                    margin=ft.margin.only(bottom=5),
                )
            ], alignment=ft.MainAxisAlignment.START)
        )
        page.update()

    # --- ЛОГИКА ОБНОВЛЕНИЯ ---
    def check_updates():
        try:
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != page.my_user_nick:
                    render_message(msg["user_name"], msg["text"])
                page.last_msg_id = msg["id"]
            page.update()
        except:
            pass
        threading.Timer(3, check_updates).start()

    # --- ЛОГИКА ОТПРАВКИ ---
    def send_msg(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                res = supabase.table("messages").insert({"user_name": page.my_user_nick, "text": text}).execute()
                # Обработка ID для старых версий библиотек
                data = res.data
                new_id = data[0]["id"] if isinstance(data, list) else data["id"]
                page.last_msg_id = new_id
                
                render_message(page.my_user_nick, text)
            except:
                chat_display.controls.append(ft.Text("!! DB ERROR", color="red"))
            page.update()

    # --- ИНТЕРФЕЙС СТРАНИЦ ---
    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="EDIT NICKNAME", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        
        def save_name(e):
            if name_edit.value:
                page.my_user_nick = name_edit.value
            show_chat_ui()

        page.add(
            ft.Text("--- CHAT ---", color="#00FF00", size=18, weight="bold"),
            ft.Text("IDENTITY CONFIGURATION:", color="#008800", size=12),
            name_edit,
            ft.Row([
                ft.ElevatedButton("SAVE", on_click=save_name),
                ft.ElevatedButton("CANCEL", on_click=lambda _: show_chat_ui())
            ])
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        header = ft.Column([
            ft.Text("--- CHAT ---", color="#00FF00", size=18, weight="bold"),
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
                ft.Text(">", color="#00FF00"),
                msg_input,
                ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")
            ])
        )
        # Загрузка истории
        if page.last_msg_id == 0:
            try:
                res = supabase.table("messages").select("*").order("created_at").limit(15).execute()
                for msg in res.data:
                    render_message(msg["user_name"], msg["text"], is_history=True)
                    page.last_msg_id = msg["id"]
            except: pass
        page.update()

    show_chat_ui()
    
    if not hasattr(page, "running"):
        check_updates()
        page.running = True

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
