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

def send_msg(e=None): # Добавили e=None для стабильности
        if msg_input.value:
            text = msg_input.value
            # 1. Очищаем поле ввода СРАЗУ, чтобы не было задержек
            msg_input.value = ""
            page.update()
            
            try:
                # 2. Сохраняем в облако
                sb.table("messages").insert({"user_name": my_name, "text": text}).execute()
                
                # 3. Добавляем у себя на экран
                chat_display.controls.append(ft.Text(f"[{my_name}]: {text}", color="green"))
                
                # 4. Рассылаем ПРОСТУЮ СТРОКУ (так надежнее для старых версий)
                # Мы склеиваем имя и текст в одну строку через разделитель "::"
                page.pubsub.send_all(f"{my_name}::{text}")
            except Exception as ex:
                chat_display.controls.append(ft.Text(f"SYSTEM ERROR: {ex}", color="red"))
            
            page.update()

def on_broadcast(data):
        # 5. Принимаем строку и режем её обратно на имя и текст
        try:
            user, text = data.split("::", 1)
            # Если имя отправителя не моё — рисуем на экране
            if user != my_name:
                chat_display.controls.append(ft.Text(f"[{user}]: {text}", color="green"))
                page.update()
        except:
            # Если пришло что-то странное, просто игнорируем
            pass

    page.pubsub.subscribe(on_broadcast)
    page.update()

if __name__ == "__main__":
    # Для Render важно оставить этот блок
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
    page.update()

if __name__ == "__main__":
    # Для Render важно оставить этот блок
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
