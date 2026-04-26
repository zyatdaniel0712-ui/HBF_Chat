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
    # Безопасная инициализация ника и авы
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"HACKER_{random.randint(1000, 9999)}"
    if not hasattr(page, "my_avatar_url"):
        # Стандартная аватарка (робот)
        page.my_avatar_url = f"https://dicebear.com{page.my_user_nick}"
    
    page.last_msg_id = 0
    page.title = "C:\\SYSTEM\\HBF-FLUD\\CHAT.EXE"
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="TYPE COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # ФУНКЦИЯ ОТРИСОВКИ СООБЩЕНИЯ С КАРТИНКОЙ
    def render_message(user, text, avatar_url=None, is_history=False):
        user_lower = user.lower()
        
        # 1. СПЕЦИАЛЬНЫЙ ВИД ДЛЯ СЕРВЕРА
        if user_lower == "сервер" or user_lower == "server":
            chat_display.controls.append(
                ft.Container(
                    content=ft.Text(
                        f"SYSTEM NOTICE:> {text.upper()}", 
                        color="yellow", 
                        italic=True, 
                        size=12,
                        font_family="Courier New"
                    ),
                    alignment=ft.alignment.center,
                    padding=10
                )
            )
            page.update()
            return # Выходим, чтобы не рисовать обычный бабл

        # 2. ЛОГИКА ЦВЕТОВ ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ
        if user_lower == "кевин":
            main_color = "cyan"
        elif user_lower == "хан" or user_lower == "солвер":
            main_color = "red"
        else:
            main_color = "#00FF00" if not is_history else "#008800"

        img_src = avatar_url if avatar_url else f"https://dicebear.com{user}"

        # 3. ОБЫЧНЫЙ БАБЛ СООБЩЕНИЯ
        chat_display.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=img_src, width=30, height=30, border_radius=15),
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
                    render_message(msg["user_name"], msg["text"], msg.get("avatar_url"))
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
                # Отправляем ник, текст и текущую ссылку на аву
                res = supabase.table("messages").insert({
                    "user_name": page.my_user_nick, 
                    "text": text,
                    "avatar_url": page.my_avatar_url
                }).execute()
                
                data = res.data
                new_id = data[0]["id"] if isinstance(data, list) else data["id"]
                page.last_msg_id = new_id
                
                render_message(page.my_user_nick, text, page.my_avatar_url)
            except:
                chat_display.controls.append(ft.Text("!! DB ERROR", color="red"))
            page.update()

    # --- СТРАНИЦА НАСТРОЕК (РАЗДЕЛЬНАЯ) ---
    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="EDIT ID", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        avatar_edit = ft.TextField(label="AVATAR URL", value=page.my_avatar_url, border_color="#00FF00", color="#00FF00")
        
        def save_name(e):
            page.my_user_nick = name_edit.value
            page.update()

        def save_avatar(e):
            page.my_avatar_url = avatar_edit.value
            page.update()

        page.add(
            ft.Text("--- TERMINAL CONFIG ---", color="#00FF00", size=18, weight="bold"),
            ft.Column([
                name_edit,
                ft.ElevatedButton("SAVE NAME", on_click=save_name),
            ]),
            ft.Divider(color="#004400"),
            ft.Column([
                avatar_edit,
                ft.ElevatedButton("SAVE AVATAR", on_click=save_avatar),
            ]),
            ft.ElevatedButton("BACK TO CHAT", on_click=lambda _: show_chat_ui())
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
            ft.Row([
                ft.Text(">", color="#00FF00"),
                msg_input,
                ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")
            ])
        )
        # Загрузка истории
        if page.last_msg_id == 0:
            try:
                res = supabase.table("messages").select("*").order("created_at").limit(10).execute()
                for msg in res.data:
                    render_message(msg["user_name"], msg["text"], msg.get("avatar_url"), is_history=True)
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
