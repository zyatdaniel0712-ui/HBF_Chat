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
    # Инициализация переменных сессии (обход старой версии Flet)
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"
    if not hasattr(page, "my_avatar_url"):
        page.my_avatar_url = f"https://dicebear.com{page.my_user_nick}"
    
    page.last_msg_id = 0
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # Функция отрисовки сообщения (баблы с серым фоном по длине текста)
    def render_msg(user, text, avatar_url, is_history=False):
        user_lower = user.lower()
        if user_lower == "кевин": name_color = "cyan"
        elif user_lower in ["хан", "солвер"]: name_color = "red"
        elif user_lower in ["система"]: name_color = "black"
        else: name_color = "#00FF00" if not is_history else "#008800"

        img_src = avatar_url if avatar_url else f"https://dicebear.com{user}"

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
            ], alignment=ft.MainAxisAlignment.START)
        )
        page.update()

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

    def send_msg(e):
        if msg_input.value:
            text = msg_input.value
            msg_input.value = ""
            try:
                supabase.table("messages").insert({
                    "user_name": page.my_user_nick, 
                    "text": text,
                    "avatar_url": page.my_avatar_url 
                }).execute()
                render_msg(page.my_user_nick, text, page.my_avatar_url)
            except: pass
            page.update()

    # --- СТРАНИЦА НАСТРОЕК ---
    def show_settings(e):
        page.controls.clear()
        
        # Секция имени
        name_edit = ft.TextField(label="NEW ID", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        def save_name(e):
            page.my_user_nick = name_edit.value
            page.snack_bar = ft.SnackBar(ft.Text("ID UPDATED"))
            page.snack_bar.open = True
            page.update()

        # Секция аватара
        avatar_edit = ft.TextField(label="IMAGE URL", value=page.my_avatar_url, border_color="#00FF00", color="#00FF00")
        def save_avatar(e):
            page.my_avatar_url = avatar_edit.value
            page.snack_bar = ft.SnackBar(ft.Text("AVATAR UPDATED"))
            page.snack_bar.open = True
            page.update()

        def select_preset(e):
            avatar_edit.value = e.control.data
            page.update()

        # Выбор готовых аватарок (роботы и пиксели)
        presets = ft.Row(scroll="always")
        for style in ["bottts", "pixel-art", "avataaars"]:
            for i in range(1, 6):
                url = f"https://dicebear.com{style}/png?seed={style}{i}"
                presets.controls.append(
                    ft.GestureDetector(
                        content=ft.Image(src=url, width=50, height=50, border_radius=10),
                        data=url,
                        on_tap=select_preset
                    )
                )

        page.add(
            ft.Text("--- USER CONFIGURATION ---", color="#00FF00", size=18, weight="bold"),
            ft.Column([
                ft.Text("IDENTITY:", color="#008800", size=10),
                name_edit,
                ft.ElevatedButton("SAVE NAME", on_click=save_name),
            ]),
            ft.Divider(color="#004400"),
            ft.Column([
                ft.Text("VISUAL CORE (SELECT OR PASTE URL):", color="#008800", size=10),
                ft.Container(content=presets, padding=5, bgcolor="#0a0a0a"),
                avatar_edit,
                ft.ElevatedButton("SAVE AVATAR", on_click=save_avatar),
            ]),
            ft.Divider(color="#004400"),
            ft.ElevatedButton("RETURN TO TERMINAL", on_click=lambda _: show_chat_ui())
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        header = ft.Column([
            ft.Text("--- TERMINAL CHAT ---", color="#00FF00", size=18, weight="bold"),
            ft.Row([
                ft.Row([
                    ft.Image(src=page.my_avatar_url, width=20, height=20, border_radius=10),
                    ft.Text(f"ID: {page.my_user_nick}", color="#008800", size=12),
                ]),
                ft.IconButton(ft.Icons.SETTINGS, on_click=show_settings, icon_color="#00FF00")
            ], alignment="spaceBetween"),
            ft.Divider(color="#004400"),
        ])
        page.add(
            header, 
            ft.Container(content=chat_display, expand=True),
            ft.Row([ft.Text(">", color="#00FF00"), msg_input, ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")])
        )
        
        # Загрузка истории
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
