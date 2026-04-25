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
    # --- 2. ГЕНЕРАЦИЯ ИМЕНИ (БЕЗ ОШИБОК) ---
    # В версии 0.84.0 просто создаем свой атрибут
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"HACKER_{random.randint(1000, 9999)}"
    
    page.last_msg_id = 0

    page.title = "C:\\SYSTEM\\CHAT.EXE"
    page.bgcolor = "black"

    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="COMMAND", expand=True, border_color="#00FF00", color="#00FF00")

    # --- 3. ОБНОВЛЕНИЕ ---
    def check_updates():
        try:
            # Запрашиваем новые сообщения
            res = supabase.table("messages").select("*").gt("id", page.last_msg_id).order("id").execute()
            for msg in res.data:
                if msg["user_name"] != page.my_user_nick:
                    chat_display.controls.append(
                        ft.Text(f"[{msg['user_name']}]:> {msg['text']}", color="#00FF00")
                    )
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
                # В старых версиях res.data может быть списком или словарем
                if isinstance(res.data, list) and len(res.data) > 0:
                    page.last_msg_id = res.data[0]["id"]
                
                chat_display.controls.append(ft.Text(f"[{page.my_user_nick}]:> {text}", color="#008800"))
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
            ft.Text("--- SETTINGS ---", color="#00FF00"),
            name_edit,
            ft.ElevatedButton("SAVE", on_click=save_name),
            ft.ElevatedButton("BACK", on_click=lambda _: show_chat_ui())
        )
        page.update()

    def show_chat_ui():
        page.controls.clear()
        page.add(
            ft.Row([
                ft.Text(f"ID: {page.my_user_nick}", color="#00FF00", weight="bold"),
                ft.IconButton(ft.Icons.SETTINGS, on_click=show_settings, icon_color="#00FF00")
            ], alignment="spaceBetween"),
            ft.Container(content=chat_display, expand=True),
            ft.Row([
                msg_input,
                ft.IconButton(ft.Icons.SEND, on_click=send_msg, icon_color="#00FF00")
            ])
        )
        page.update()

    show_chat_ui()
    check_updates()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
