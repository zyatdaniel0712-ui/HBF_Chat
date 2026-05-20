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
# Положи картинки в папку:
#
# assets/avatars/
#
# Например:
# assets/avatars/avatar1.png
# assets/avatars/avatar2.png
# assets/avatars/avatar3.png
#
# =========================

AVATARS = [
    "avatars/avatar1.png",
    "avatars/avatar2.png",
    "avatars/avatar3.png",
    "avatars/avatar4.png",
]


def main(page: ft.Page):

    # =========================
    # НАСТРОЙКИ ОКНА
    # =========================

    page.title = "TERMINAL CHAT"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "black"
    page.padding = 10
    page.scroll = "auto"

    # =========================
    # СОСТОЯНИЕ
    # =========================

    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000,9999)}"

    if not hasattr(page, "my_avatar"):
        page.my_avatar = random.choice(AVATARS)

    page.last_msg_id = 0

    # =========================
    # UI
    # =========================

    chat_display = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )

    msg_input = ft.TextField(
        hint_text="Введите сообщение...",
        expand=True,
        color="#00FF00",
        border_color="#00FF00",
        bgcolor="#111111"
    )

    # =========================
    # РЕНДЕР СООБЩЕНИЯ
    # =========================

    def render_msg(user, text, avatar_path, is_history=False):

        user_lower = user.lower()

        if user_lower in ["server", "сервер"]:
            chat_display.controls.append(
                ft.Text(
                    f"[SYSTEM]: {text}",
                    color="yellow",
                    size=14,
                    weight="bold"
                )
            )

            page.update()
            return

        # Цвета ников
        if user_lower == "кевин":
            name_color = "cyan"

        elif user_lower in ["хан", "солвер"]:
            name_color = "red"

        else:
            name_color = "#00FF00"

        bubble = ft.Container(
            bgcolor="#1c1c1c",
            border_radius=15,
            padding=10,

            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START,

                controls=[

                    ft.Image(
                        src=avatar_path,
                        width=45,
                        height=45,
                        border_radius=999
                    ),

                    ft.Column(
                        spacing=5,

                        controls=[

                            ft.Text(
                                user,
                                color=name_color,
                                weight="bold",
                                size=14
                            ),

                            ft.Text(
                                text,
                                color="white",
                                selectable=True
                            )
                        ]
                    )
                ]
            )
        )

        chat_display.controls.append(bubble)

        page.update()

    # =========================
    # ОБНОВЛЕНИЕ ЧАТА
    # =========================

    async def check_updates():

        while True:

            try:

                res = (
                    supabase
                    .table("messages")
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
                            msg.get("avatar", "avatars/avatar1.png")
                        )

                    page.last_msg_id = msg["id"]

                page.update()

            except Exception as ex:
                print(ex)

            await asyncio.sleep(2)

    # =========================
    # ОТПРАВКА
    # =========================

    def send_msg(e):

        if not msg_input.value:
            return

        text = msg_input.value

        msg_input.value = ""

        try:

            res = (
                supabase
                .table("messages")
                .insert({

                    "user_name": page.my_user_nick,
                    "text": text,
                    "avatar": page.my_avatar

                })
                .execute()
            )

            data = res.data[0]

            page.last_msg_id = data["id"]

            render_msg(
                page.my_user_nick,
                text,
                page.my_avatar
            )

        except Exception as ex:
            print(ex)

        page.update()

    # =========================
    # ВЫБОР АВАТАРКИ
    # =========================

    def open_avatar_selector(e):

        avatars_grid = ft.GridView(
            expand=True,
            max_extent=120,
            spacing=10,
            run_spacing=10
        )

        for avatar in AVATARS:

            def select_avatar(ev, selected=avatar):

                page.my_avatar = selected

                dialog.open = False

                page.snack_bar = ft.SnackBar(
                    ft.Text("Аватар изменён")
                )

                page.snack_bar.open = True

                page.update()

            avatars_grid.controls.append(

                ft.Container(

                    content=ft.Image(
                        src=avatar,
                        fit=ft.ImageFit.COVER
                    ),

                    border_radius=20,
                    ink=True,
                    on_click=select_avatar
                )
            )

        dialog.content = avatars_grid

        dialog.open = True

        page.update()

    # =========================
    # DIALOG
    # =========================

    dialog = ft.AlertDialog()

    page.dialog = dialog

    # =========================
    # HEADER
    # =========================

    header = ft.Container(

        padding=10,
        border_radius=15,
        bgcolor="#111111",

        content=ft.Row(

            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,

            controls=[

                ft.Column(
                    spacing=2,

                    controls=[

                        ft.Text(
                            "TERMINAL CHAT",
                            size=20,
                            weight="bold",
                            color="#00FF00"
                        ),

                        ft.Text(
                            f"ID: {page.my_user_nick}",
                            color="#008800",
                            size=12
                        )
                    ]
                ),

                ft.Row(

                    controls=[

                        ft.CircleAvatar(
                            foreground_image_src=page.my_avatar,
                            radius=22
                        ),

                        ft.IconButton(
                            icon=ft.Icons.PERSON,
                            icon_color="#00FF00",
                            on_click=open_avatar_selector
                        )
                    ]
                )
            ]
        )
    )

    # =========================
    # INPUT BAR
    # =========================

    input_bar = ft.Container(

        padding=10,
        border_radius=15,
        bgcolor="#111111",

        content=ft.Row(

            controls=[

                msg_input,

                ft.IconButton(
                    icon=ft.Icons.SEND,
                    icon_color="#00FF00",
                    on_click=send_msg
                )
            ]
        )
    )

    # =========================
    # LOAD HISTORY
    # =========================

    try:

        res = (
            supabase
            .table("messages")
            .select("*")
            .order("id")
            .limit(30)
            .execute()
        )

        for msg in res.data:

            render_msg(
                msg["user_name"],
                msg["text"],
                msg.get("avatar", "avatars/avatar1.png"),
                is_history=True
            )

            page.last_msg_id = msg["id"]

    except Exception as ex:
        print(ex)

    # =========================
    # MAIN UI
    # =========================

    page.add(
        header,
        ft.Container(
            content=chat_display,
            expand=True
        ),
        input_bar
    )

    # =========================
    # START BACKGROUND TASK
    # =========================

    page.run_task(check_updates)


# =========================
# START
# =========================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
