import flet as ft
import os
import random

# Пробуем импортировать supabase
try:
    from supabase import create_client
except:
    pass

# --- ТВОИ ДАННЫЕ (ВСТАВЬ ИХ!) ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"

def main(page: ft.Page):
    page.title = "C:\\SYSTEM\\CHAT.EXE"
    page.bgcolor = "black"
    
    # 1. Генерируем имя в обычную переменную (сработает везде)
    my_name = f"USER_{random.randint(100, 999)}"
    
    chat_display = ft.Column(scroll="always", expand=True)
    msg_input = ft.TextField(label="COMMAND", expand=True)

    # 2. Сначала рисуем интерфейс
    page.add(
        ft.Text("--- TERMINAL READY ---", color="green"),
        ft.Text(f"LOGGED AS: {my_name}", color="green"),
        ft.Container(content=chat_display, expand=True),
        ft.Row([msg_input, ft.IconButton(ft.Icons.SEND, on_click=lambda _: send_msg())])
    )
    page.update()

    # 3. Подключаем базу
    try:
        sb = create_client(URL, KEY)
        # Загрузка последних 10 сообщений
        res = sb.table("messages").select("*").order("created_at").limit(10).execute()
        for msg in res.data:
            chat_display.controls.append(ft.Text(f"[{msg['user_name']}]: {msg['text']}", color="green"))
    except Exception as e:
        chat_display.controls.append(ft.Text(f"DATABASE ERROR", color="red"))

    def send_msg():
        if msg_input.value:
            text = msg_input.value
            try:
                sb.table("messages").insert({"user_name": my_name, "text": text}).execute()
                chat_display.controls.append(ft.Text(f"[{my_name}]: {text}", color="green"))
                page.pubsub.send_all({"user": my_name, "text": text, "sid": page.session_id})
                msg_input.value = ""
            except:
                pass
            page.update()

    def on_broadcast(data):
        # В старых версиях может не быть session_id, просто проверяем ник
        if data["user"] != my_name:
            chat_display.controls.append(ft.Text(f"[{data['user']}]: {data['text']}", color="green"))
            page.update()

    page.pubsub.subscribe(on_broadcast)
    page.update()

if __name__ == "__main__":
    # Для Render важно оставить этот блок
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
