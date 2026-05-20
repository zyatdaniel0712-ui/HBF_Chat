import flet as ft
import os
import random
import asyncio
from supabase import create_client

# =========================
# SUPABASE
# =========================
URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"
supabase = create_client(URL, KEY)

# =========================
# ЛОКАЛЬНЫЕ АВАТАРКИ
# =========================
# Положи картинки сюда:
# assets/avatars/avatar1.png
# assets/avatars/avatar2.png
# assets/avatars/avatar3.png
# assets/avatars/avatar4.png
#
# Можно добавить свои файлы и просто дописать их в список ниже.
AVATARS = [
    "avatars/avatar1.png",
    "avatars/avatar2.png",
    "avatars/avatar3.png",
    "avatars/avatar4.png",
]


def main(page: ft.Page):
    # =========================
    # НАСТРОЙКИ ПРИЛОЖЕНИЯ
    # =========================
    page.title = "TERMINAL CHAT"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b0f14"
    page.padding = 10
    page.scroll = "auto"

    # =========================
    # СОСТОЯНИЕ ПОЛЬЗОВАТЕЛЯ
    # =========================
    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000, 9999)}"

    if not hasattr(page, "my_avatar"):
        page.my_avatar = random.choice(AVATARS)

    page.last_msg_id = 0

    # =========================
    # UI-ЭЛЕМЕНТЫ
    # =========================
    chat_display = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
        padding=10,
    )

    msg_input = ft.TextField(
        hint_text="Введите сообщение...",
        expand=True,
        color="#00FF00",
        border_color="#00FF00",
        bgcolor="#111111",
        cursor_color="#00FF00",
        focused_border_color="#00FF00",
    )

    avatar_preview = ft.CircleAvatar(
        foreground_image_src=page.my_avatar,
        radius=22,
        background_color="#222222",
    )

    avatar_list = ft.Wrap(
        spacing=10,
        run_spacing=10,
    )

    # =========================
    # ДИАЛОГ ВЫБОРА АВАТАРА
    # =========================
    avatar_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Выбери аватар"),
        content=ft.Container(
            width=340,
            height=380,
            content=avatar_list,
        ),
    )
    page.dialog = avatar_dialog

    # =========================
    # ФУНКЦИЯ РЕНДЕРА СООБЩЕНИЙ
    # =========================
    def render_msg(user, text, avatar_path, is_history=False):
        user_lower = user.lower()

        if user_lower in ["сервер", "server"]:
            chat_display.controls.append(
                ft.Container(
                    padding=10,
                    border_radius=12,
                    bgcolor="#151515",
                    content=ft.Text(
                        f"[SYSTEM]: {text.upper()}",
                        color="yellow",
                        weight="bold",
                    ),
                )
            )
            page.update()
            return

        if user_lower == "кевин":
            name_color = "cyan"
        elif user_lower in ["хан", "солвер"]:
            name_color = "red"
        else:
            name_color = "#00FF00" if not is_history else "#008800"

        bubble = ft.Container(
            bgcolor="#1c1c1c",
            border_radius=16,
            padding=10,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10,
                controls=[
                    ft.CircleAvatar(
                        foreground_image_src=avatar_path,
                        radius=20,
                        background_color="#222222",
                    ),
                    ft.Column(
                        spacing=4,
                        expand=True,
                        controls=[
                            ft.Text(
                                f"[{user}]",
                                color=name_color,
                                weight="bold",
                                size=14,
                            ),
                            ft.Text(
                                text,
                                color="white",
                                selectable=True,
                            ),
                        ],
                    ),
                ],
            ),
        )

        chat_display.controls.append(bubble)
        page.update()

    # =========================
    # ОТПРАВКА СООБЩЕНИЯ
    # =========================
    def send_msg(e):
        text = (msg_input.value or "").strip()
        if not text:
            return

        msg_input.value = ""

        try:
            res = (
                supabase.table("messages")
                .insert(
                    {
                        "user_name": page.my_user_nick,
                        "text": text,
                        "avatar_url": page.my_avatar,  # храним путь к локальному аватару
                    }
                )
                .execute()
            )

            if res.data:
                if isinstance(res.data, list) and len(res.data) > 0:
                    page.last_msg_id = res.data[0].get("id", page.last_msg_id)
                elif isinstance(res.data, dict):
                    page.last_msg_id = res.data.get("id", page.last_msg_id)

        except Exception as ex:
            print("send_msg error:", ex)

        render_msg(page.my_user_nick, text, page.my_avatar)
        page.update()

    msg_input.on_submit = send_msg

    # =========================
    # ВЫБОР АВАТАРА
    # =========================
    def open_avatar_picker(e):
        avatar_list.controls.clear()

        for avatar in AVATARS:
            def choose(ev, selected=avatar):
                page.my_avatar = selected
                avatar_preview.foreground_image_src = selected
                avatar_dialog.open = False
                page.snack_bar = ft.SnackBar(
                    ft.Text("Аватар выбран")
                )
                page.snack_bar.open = True
                page.update()

            avatar_list.controls.append(
                ft.GestureDetector(
                    on_tap=choose,
                    content=ft.Container(
                        width=90,
                        height=110,
                        padding=8,
                        border_radius=18,
                        bgcolor="#141414",
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.CircleAvatar(
                                    foreground_image_src=avatar,
                                    radius=28,
                                    background_color="#222222",
                                ),
                                ft.Text(
                                    avatar.split("/")[-1],
                                    size=10,
                                    color="#00FF00",
                                ),
                            ],
                        ),
                    ),
                )
            )

        avatar_dialog.open = True
        page.update()

    # =========================
    # ШАПКА
    # =========================
    header = ft.Container(
        padding=12,
        border_radius=16,
        bgcolor="#111111",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=2,
                    controls=[
                        ft.Text(
                            "TERMINAL CHAT",
                            size=20,
                            weight="bold",
                            color="#00FF00",
                        ),
                        ft.Text(
                            f"ID: {page.my_user_nick}",
                            color="#008800",
                            size=12,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=8,
                    controls=[
                        avatar_preview,
                        ft.IconButton(
                            icon=ft.Icons.PERSON,
                            icon_color="#00FF00",
                            on_click=open_avatar_picker,
                        ),
                    ],
                ),
            ],
        ),
    )

    # =========================
    # НИЖНЯЯ ПАНЕЛЬ
    # =========================
    input_bar = ft.Container(
        padding=10,
        border_radius=16,
        bgcolor="#111111",
        content=ft.Row(
            spacing=8,
            controls=[
                ft.Text(">", color="#00FF00", size=18),
                msg_input,
                ft.IconButton(
                    icon=ft.Icons.SEND,
                    icon_color="#00FF00",
                    on_click=send_msg,
                ),
            ],
        ),
    )

    # =========================
    # ЗАГРУЗКА ИСТОРИИ
    # =========================
    try:
        res = (
            supabase.table("messages")
            .select("*")
            .order("id")
            .limit(30)
            .execute()
        )

        for msg in res.data:
            render_msg(
                msg["user_name"],
                msg["text"],
                msg.get("avatar_url") or msg.get("avatar_path") or AVATARS[0],
                is_history=True,
            )
            page.last_msg_id = msg["id"]

    except Exception as ex:
        print("history load error:", ex)

    # =========================
    # ОСНОВНОЙ ЭКРАН
    # =========================
    page.add(
        header,
        ft.Container(expand=True, content=chat_display),
        input_bar,
    )

    # =========================
    # ФОНОВОЕ ОБНОВЛЕНИЕ
    # =========================
    async def check_updates():
        while True:
            try:
                res = (
                    supabase.table("messages")
                    .select("*")
                    .gt("id", page.last_msg_id)
                    .order("id")
                    .execute()
                )

                for msg in res.data:
                    if msg["user_name"] != page.my_user_nick:
                        render_msg(
                            msg["user_name"],
                            msg["text"],
                            msg.get("avatar_url") or msg.get("avatar_path") or AVATARS[0],
                        )

                    page.last_msg_id = msg["id"]

                page.update()

            except Exception as ex:
                print("check_updates error:", ex)

            await asyncio.sleep(3)

    page.run_task(check_updates)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
