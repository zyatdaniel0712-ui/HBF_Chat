import flet as ft
import os
import random
import threading
import base64  # Для превращения картинки в текст
from supabase import create_client

# --- НАСТРОЙКИ ---
URL = "https://nesxjcdhqgstahwfnrba.supabase.co" 
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"             
supabase = create_client(URL, KEY)

def main(page: ft.Page):
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"
    if not hasattr(page, "my_avatar_url"):
        page.my_avatar_url = f"https://dicebear.com{page.my_user_nick}"
    
    page.last_msg_id = 0
    page.bgcolor = "black"

    chat_display = ft.Column(scroll="always", expand=True)
    
    # --- ЛОГИКА ВЫБОРА ФАЙЛА ---
    def on_file_result(e: ft.FilePickerResultEvent):
        if e.files:
            file = e.files[0]
            # Читаем файл и превращаем в Base64 строку
            with open(file.path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode("utf-8")
                # Формируем Data URL, который понимает ft.Image
                page.my_avatar_url = f"data:image/png;base64,{encoded_string}"
                page.snack_bar = ft.SnackBar(ft.Text("ФОТО ЗАГРУЖЕНО В ПАМЯТЬ"))
                page.snack_bar.open = True
                page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    def render_msg(user, text, avatar_url, is_history=False):
        user_lower = user.lower()
        if user_lower == "кевин": name_color = "cyan"
        elif user_lower in ["хан", "солвер"]: name_color = "red"
        elif user_lower in ["cистема"]: name_color = "black"
        else: name_color = "#00FF00" if not is_history else "#008800"

        img_src = avatar_url if avatar_url else f"https://dicebear.com{user}"

        chat_display.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Image(src=img_src, width=30, height=30, border_radius=15),
                        ft.Text(f"[{user}]:> {text}", color=name_color, font_family="Courier New")
                    ], tight=True, vertical_alignment="center", spacing=10),
                    bgcolor="#1c1c1c", padding=10, border_radius=15, margin=ft.margin.only(bottom=5),
                )
            ], alignment=ft.MainAxisAlignment.START)
        )
        page.update()

    # (Функции check_updates и send_msg остаются такими же, как раньше)
    # ...

    def show_settings(e):
        page.controls.clear()
        name_edit = ft.TextField(label="NEW ID", value=page.my_user_nick, border_color="#00FF00", color="#00FF00")
        
        page.add(
            ft.Text("--- CONFIGURATION ---", color="#00FF00", size=18, weight="bold"),
            name_edit,
            ft.ElevatedButton("СМЕНИТЬ НИК", on_click=lambda _: page.client_storage.set("user_nickname", name_edit.value)),
            ft.Divider(color="#004400"),
            ft.Text("АВАТАР:", color="#008800"),
            ft.Row([
                ft.Image(src=page.my_avatar_url, width=50, height=50, border_radius=25),
                ft.ElevatedButton("ВЫБРАТЬ ИЗ ГАЛЕРЕИ", 
                                  icon=ft.Icons.UPLOAD_FILE, 
                                  on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type="image")),
            ]),
            ft.Divider(color="#004400"),
            ft.ElevatedButton("UPDATE & RETURN", on_click=lambda _: show_chat_ui())
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
