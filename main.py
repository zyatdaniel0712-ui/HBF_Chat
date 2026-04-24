import flet as ft
import os
import random

# Пытаемся импортировать supabase. Если на сервере ошибка — мы её увидим.
try:
    from supabase import create_client
    SUPABASE_IMPORT_ERROR = None
except Exception as e:
    SUPABASE_IMPORT_ERROR = str(e)

# --- ДАННЫЕ (ПРОВЕРЬ ИХ ЕЩЕ РАЗ!) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"

def main(page: ft.Page):
    page.title = "C:\\SYSTEM\\CHAT.EXE"
    page.bgcolor = "black"
    page.theme = ft.Theme(font_family="Courier New")
    
    # 1. Генерируем имя сразу
    if not page.session.get("my_name"):
        page.session.set("my_name", f"USER_{random.randint(100, 999)}")
    
    my_name = page.session.get("my_name")
    
    # 2. Создаем элементы ДО подключения к базе
    chat_display = ft.ListView(expand=True, spacing=5, auto_scroll=True)
    msg_input = ft.TextField(label="COMMAND", expand=True, border_color="#00FF00", color="#00FF00")
    
    # Сразу выводим базу на экран
    page.add(
        ft.Text("--- TERMINAL READY ---", color="#00FF00"),
        ft.Text(f"ID: {my_name}", color="#008800"),
        ft.Divider(color="#004400"),
        ft.Container(content=chat_display, expand=True),
        ft.Row([msg_input, ft.IconButton(ft.icons.SEND, on_click=lambda _: send_msg(), icon_color="#00FF00")])
    )
    page.update()

    # 3. Теперь пробуем подключить облако
    if SUPABASE_IMPORT_ERROR:
        chat_display.controls.append(ft.Text(f"IMPORT ERROR: {SUPABASE_IMPORT_ERROR}", color="red"))
        page.update()
        return

    try:
        sb = create_client(URL, KEY)
        # Пробная загрузка
        res = sb.table("messages").select("*").order("created_at").limit(10).execute()
        for msg in res.data:
            chat_display.controls.append(ft.Text(f"[{msg['user_name']}]: {msg['text']}", color="#008800"))
        chat_display.controls.append(ft.Text("SYSTEM: DATABASE CONNECTED", color="yellow", size=10))
    except Exception as e:
        chat_display.controls.append(ft.Text(f"DB ERROR: {str(e)}", color="red"))

    def send_msg():
        if msg_input.value:
            text = msg_input.value
            try:
                sb.table("messages").insert({"user_name": my_name, "text": text}).execute()
                chat_display.controls.append(ft.Text(f"[{my_name}]: {text}", color="#00FF00"))
                page.pubsub.send_all({"user": my_name, "text": text, "sid": page.session_id})
                msg_input.value = ""
            except:
                chat_display.controls.append(ft.Text("FAILED TO SEND", color="red"))
            page.update()

    def on_broadcast(data):
        if data["sid"] != page.session_id:
            chat_display.controls.append(ft.Text(f"[{data['user']}]: {data['text']}", color="#00FF00"))
            page.update()

    page.pubsub.subscribe(on_broadcast)
    page.update()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
