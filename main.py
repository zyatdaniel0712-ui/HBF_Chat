import flet as ft
import os
from supabase import create_client

# --- НАСТРОЙКИ ОБЛАКА ---
SUPABASE_URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
SUPABASE_KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def main(page: ft.Page):
    # Настройки стиля "Терминал"
    page.title = "C:\\SYSTEM\\CHAT.EXE"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    # Зеленый "фосфорный" шрифт
    page.theme = ft.Theme(font_family="Courier New")
    
    # Генерируем уникальное имя для каждой новой вкладки/сессии
    if not page.session.get("my_name"):
        import random
        anon_name = f"USER_{random.randint(100, 999)}"
        page.session.set("my_name", anon_name)

    chat_display = ft.ListView(expand=True, spacing=5, auto_scroll=True)

    def add_msg(user, text, color="#00FF00"):
        chat_display.controls.append(
            ft.Text(
                f"[{user}]:> {text}", 
                color=color, 
                font_family="Courier New",
                size=14
            )
        )
        page.update()

    # Загрузка истории
    try:
        res = supabase.table("messages").select("*").order("created_at").limit(20).execute()
        for msg in res.data:
            add_msg(msg["user_name"], msg["text"], color="#008800") # Старые сообщения чуть тусклее
    except:
        add_msg("SYSTEM", "DATABASE CONNECTION ERROR", color="red")

    def on_message(data):
        if data["type"] == "chat" and data["session_id"] != page.session_id:
            add_msg(data["user"], data["text"])

    page.pubsub.subscribe(on_message)

    # Поле ввода в стиле командной строки
    msg_input = ft.TextField(
        label="ENTER COMMAND",
        label_style=ft.TextStyle(color="#00FF00"),
        border_color="#00FF00",
        color="#00FF00",
        cursor_color="#00FF00",
        expand=True,
        on_submit=lambda _: send_click(None)
    )

    def send_click(e):
        if msg_input.value:
            my_name = page.session.get("my_name")
            text = msg_input.value
            
            # Сохраняем в базу
            supabase.table("messages").insert({"user_name": my_name, "text": text}).execute()
            
            # Показываем у себя
            add_msg(my_name, text)
            
            # Отправляем другим
            page.pubsub.send_all({
                "type": "chat", 
                "user": my_name, 
                "text": text,
                "session_id": page.session_id
            })
            msg_input.value = ""
            page.update()

    # Сборка интерфейса
    page.add(
        ft.Text("--- TERMINAL CHAT v1.0 ONLINE ---", color="#00FF00", weight="bold"),
        ft.Text(f"LOGGED IN AS: {page.session.get('my_name')}", color="#00FF00", size=12),
        ft.Divider(color="#00FF00"),
        ft.Container(content=chat_display, expand=True),
        ft.Row([
            ft.Text(">", color="#00FF00", size=20),
            msg_input,
            ft.TextButton("EXECUTE", on_click=send_click, style=ft.ButtonStyle(color="#00FF00"))
        ])
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
