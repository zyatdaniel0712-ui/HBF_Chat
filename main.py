import flet as ft
import os
import random
import threading
from supabase import create_client

# --- 1. ТВОИ КЛЮЧИ ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co" 
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"             
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    # Инициализация ника и аватарки
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"
    if not hasattr(page, "my_avatar_url"):
        # По умолчанию — случайный робот
        page.my_avatar_url = f"https://dicebear.com{page.my_user_nick}"
    
    page.last_msg_id = 0
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="TYPE COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # Функция отрисовки сообщения с аватаркой
    def render_msg(user, text, avatar_url, is_history=False):
        user_lower = user.lower()
        # Цвета ников
        if user_lower == "кевин": name_color = "cyan"
        elif user_lower == "хан" or user_lower == "солвер": name_color = "red"
        else: name_color = "#00FF00" if not is_history else "#008800"

        # Если в базе нет ссылки на аватар, ставим робота
        img_src = avatar_url if avatar_url else f"https://dicebear.com{user}"

        chat_display.controls.append(
            ft.Row([
                ft.Image(src=img_src, width=30, height=30, border_radius=15),
                ft.Text(f"[{user}]:> {text}", color=name_color, font_family="Courier New", expand=True)
            ], vertical_alignment="center")
        )
        page.update()

    def check_updates():
        try:
            # ТЕПЕРЬ ЗАПРАШИВАЕМ И user_name, И text, И avatar_url (убедись, что колонка есть в базе или используй select("*"))
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != page.my_user_nick:
                    # Извлекаем аватарку из сообщения в базе
                    remote_avatar = msg.get("avatar_url") 
                    render_msg(msg["user_name"], msg["text"], remote_avatar)
                page.last_msg_id = msg["id"]
            page.update()
        except: pass
        threading.Timer(3, check_updates).start()

    def send_msg(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                # ОТПРАВЛЯЕМ В БАЗУ ТРИ ПОЛЯ: ник, текст и ссылку на аватар
                res = supabase.table("messages").insert({
                    "user_name": page.my_user_nick, 
                    "text": text,
                    "avatar_url": page.my_avatar_url 
                }).execute()
                
                if isinstance(res.data, list) and len(res.data) > 0:
                    page.last_msg_id = res.data[0]["id"]
                
                render_msg(page.my_user_nick, text, page.my_avatar_url)
            except:
                chat_display.controls.append(ft.Text("!! DB ERROR", color="red"))
            page.update()

    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="EDIT NICKNAME", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        avatar_edit = ft.TextField(label="AVATAR URL (PNG/JPG)", value=page.my_avatar_url, border_color="#00FF00", color="#00FF00")
        
        def save_settings(e):
            page.my_user_nick = name_edit.value
            page.my_avatar_url = avatar_edit.value
            show_chat_ui()

        page.add(
            ft.Text("--- SETTINGS ---", color="#00FF00", size=18, weight="bold"),
            name_edit,
            avatar_edit,
            ft.Row([
                ft.ElevatedButton("APPLY", on_click=save_settings),
                ft.ElevatedButton("BACK", on_click=lambda _: show_chat_ui())
            ])
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        header = ft.Column([
            ft.Text("--- TERMINAL CHAT v1.0 ---", color="#00FF00", size=18, weight="bold"),
            ft.Row([
                ft.Text(f"ID: {page.my_user_nick}", color="#008800", size=12),
                ft.IconButton(ft.Icons.SETTINGS, on_click=show_settings, icon_color="#00FF00")
            ], alignment="spaceBetween"),
            ft.Divider(color="#004400"),
        ])
        page.add(header, ft.Container(content=chat_display, expand=True),
                 ft.Row([ft.Text(">", color="#00FF00"), msg_input, ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")]))
        page.update()

    show_chat_ui()
    if not hasattr(page, "thread_running"):
        check_updates()
        page.thread_running = True

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
