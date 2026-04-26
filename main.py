import flet as ft
import os
import random
import threading
from supabase import create_client

# --- 1. НАСТРОЙКИ (ВСТАВЬ СВОИ ДАННЫЕ) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co" 
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"             
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # Инициализация переменных сессии
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"
    if not hasattr(page, "my_avatar_url"):
        page.my_avatar_url = f"https://dicebear.com{page.my_user_nick}"
    
    page.last_msg_id = 0
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # --- ФУНКЦИЯ ОТРИСОВКИ СООБЩЕНИЯ ---
    def render_msg(user, text, avatar_url=None, is_history=False):
        user_lower = user.lower()
        
        # 1. СПЕЦИАЛЬНЫЙ ВИД ДЛЯ СЕРВЕРА
        if user_lower == "сервер" or user_lower == "server":
            chat_display.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"SYSTEM NOTICE:> {text.upper()}", 
                        color="yellow", 
                        italic=True, 
                        size=12
                    ),
                    alignment="center", # Используем строку вместо ft.alignment.center
                    padding=10
                )
            )
            page.update()
            return

        # 2. ЛОГИКА ЦВЕТОВ ДЛЯ ОБЫЧНЫХ НИКОВ
        if user_lower == "кевин":
            name_color = "cyan"
        elif user_lower in ["хан", "солвер"]:
            name_color = "red"
        else:
            name_color = "#00FF00" if not is_history else "#008800"

        img_src = avatar_url if avatar_url else f"https://dicebear.com{user}"

        # 3. ОБЫЧНЫЙ БАБЛ СООБЩЕНИЯ
        chat_display.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=img_src, width=30, height=30, border_radius=15),
                        ft.Text(f"[{user}]:> {text}", color=name_color, font_family="Courier New")
                    ], tight=True, vertical_alignment="center", spacing=10),
                    bgcolor="#1c1c1c",
                    padding=10,
                    border_radius=15,
                    margin=ft.margin.only(bottom=5),
                )
            ], alignment="start") # Используем строку вместо ft.MainAxisAlignment.START
        )
        page.update()

    # --- ОБНОВЛЕНИЕ ЧАТА ---
    def check_updates():
        try:
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != page.my_user_nick:
                    render_msg(msg["user_name"], msg["text"], msg.get("avatar_url"))
                page.last_msg_id = msg["id"]
            page.update()
        except: pass
        threading.Timer(3, check_updates).start()

    # --- ОТПРАВКА ---
    def send_msg(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                res = supabase.table("messages").insert({
                    "user_name": page.my_user_nick, 
                    "text": text,
                    "avatar_url": page.my_avatar_url 
                }).execute()
                
                # Обновляем ID
                if isinstance(res.data, list) and len(res.data) > 0:
                    page.last_msg_id = res.data[0]["id"]
                elif isinstance(res.data, dict):
                    page.last_msg_id = res.data["id"]
                
                render_msg(page.my_user_nick, text, page.my_avatar_url)
            except Exception as ex:
                chat_display.controls.append(ft.Text(f"!! ERROR: {ex}", color="red", size=10))
            page.update()

    # --- НАСТРОЙКИ ---
    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="NEW ID", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        avatar_edit = ft.TextField(label="AVATAR URL", value=page.my_avatar_url, border_color="#00FF00", color="#00FF00")
        
        def save_name(e):
            page.my_user_nick = name_edit.value
            page.update()

        def save_avatar(e):
            page.my_avatar_url = avatar_edit.value
            page.update()

        page.add(
            ft.Text("--- TERMINAL CONFIG ---", color="#00FF00", size=18, weight="bold"),
            name_edit, ft.ElevatedButton("SAVE NAME", on_click=save_name),
            ft.Divider(color="#004400"),
            avatar_edit, ft.ElevatedButton("SAVE AVATAR", on_click=save_avatar),
            ft.ElevatedButton("BACK TO TERMINAL", on_click=lambda _: show_chat_ui())
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
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
            ft.Row([ft.Text(">", color="#00FF00"), msg_input, ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")])
        )
        
        if page.last_msg_id == 0:
            try:
                res = supabase.table("messages").select("*").order("created_at").limit(10).execute()
                for msg in res.data:
                    render_msg(msg["user_name"], msg["text"], msg.get("avatar_url"), is_history=True)
                    page.last_msg_id = msg["id"]
            except: pass
        page.update()

    show_chat_ui()
    if not hasattr(page, "thread_running"):
        check_updates()
        page.thread_running = True

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
