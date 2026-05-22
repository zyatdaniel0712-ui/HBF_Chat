
import flet as ft
import random
import asyncio
import os
from supabase import create_client

# =====================================
# SUPABASE
# =====================================

URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"

supabase = create_client(URL, KEY)

# =====================================
# AVATARS
# =====================================

AVATARS = [
    "https://api.dicebear.com/7.x/bottts/png?seed=1",
    "https://api.dicebear.com/7.x/bottts/png?seed=2",
    "https://api.dicebear.com/7.x/bottts/png?seed=3",
    "https://api.dicebear.com/7.x/bottts/png?seed=4",
    "https://api.dicebear.com/7.x/bottts/png?seed=5",
]

# =====================================
# MAIN
# =====================================

def main(page: ft.Page):

    # =====================================
    # PAGE
    # =====================================

    page.title = "TERMINAL CHAT"
    page.theme_mode = "dark"
    page.bgcolor = "#0b0f14"
    page.padding = 10

    # =====================================
    # USER
    # =====================================

    page.my_user_nick = f"USER_{random.randint(1000,9999)}"
    page.my_avatar = random.choice(AVATARS)

    page.last_msg_id = 0

    # =====================================
    # CHAT
    # =====================================

    chat_display = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    msg_input = ft.TextField(
        hint_text="Введите сообщение...",
        expand=True,
        color="#00FF00",
        border_color="#00FF00",
        bgcolor="#111111",
    )

    # =====================================
    # SETTINGS
    # =====================================

    settings_visible = False

    avatar_preview = ft.CircleAvatar(
        foreground_image_src=page.my_avatar,
        radius=20,
    )

    settings_big_avatar = ft.CircleAvatar(
        foreground_image_src=page.my_avatar,
        radius=60,
    )

    settings_nick = ft.Text(
        page.my_user_nick,
        size=24,
        weight="bold",
        color="#00FF00",
    )

    nick_input = ft.TextField(
        hint_text="Новый ник...",
        color="#00FF00",
        border_color="#00FF00",
        bgcolor="#111111",
    )

    avatar_menu = ft.Column(
        visible=False,
        spacing=5,
    )

    # =====================================
    # USER LABEL
    # =====================================

    user_text = ft.Text(
        page.my_user_nick,
        color="#00FF00",
        weight="bold",
    )

    # =====================================
    # CHANGE NICK
    # =====================================

    def change_nick(e):

        new_nick = nick_input.value.strip()

        if new_nick == "":
            return

        page.my_user_nick = new_nick

        user_text.value = new_nick
        settings_nick.value = new_nick

        nick_input.value = ""

        page.update()

    # =====================================
    # CHOOSE AVATAR
    # =====================================

    def choose_avatar(e):

        selected = e.control.data

        page.my_avatar = selected

        avatar_preview.foreground_image_src = selected
        settings_big_avatar.foreground_image_src = selected

        avatar_menu.visible = False

        page.update()

    # =====================================
    # OPEN AVATAR MENU
    # =====================================

    def open_avatar_menu(e):

        avatar_menu.controls.clear()

        for avatar in AVATARS:

            avatar_menu.controls.append(

                ft.ElevatedButton(
                    f"Avatar {avatar.split('=')[-1]}",
                    data=avatar,
                    on_click=choose_avatar
                )
            )

        avatar_menu.visible = not avatar_menu.visible

        page.update()

    # =====================================
    # TOGGLE SETTINGS
    # =====================================

    settings_panel = ft.Container(
        visible=False,
        bgcolor="#111111",
        border_radius=15,
        padding=20,

        content=ft.Column(

            horizontal_alignment="center",
            spacing=20,

            controls=[

                settings_big_avatar,

                settings_nick,

                ft.ElevatedButton(
                    "Сменить аватар",
                    on_click=open_avatar_menu
                ),

                avatar_menu,

                nick_input,

                ft.ElevatedButton(
                    "Сохранить ник",
                    on_click=change_nick
                )
            ]
        )
    )

    def toggle_settings(e):

        settings_panel.visible = not settings_panel.visible

        page.update()

    # =====================================
    # NAME COLOR
    # =====================================

    def get_name_color(user):

        user_lower = user.lower()

        if user_lower == "кевин":
            return "cyan"

        elif user_lower in ["хан", "солвер"]:
            return "red"

        elif user == page.my_user_nick:
            return "#00FF00"

        return "white"

    # =====================================
    # RENDER MESSAGE
    # =====================================

    def render_msg(user, text, avatar):

        bubble = ft.Container(

            bgcolor="#1c1c1c",
            border_radius=15,
            padding=10,

            content=ft.Row(

                vertical_alignment="start",

                controls=[

                    ft.CircleAvatar(
                        foreground_image_src=avatar,
                        radius=18,
                    ),

                    ft.Column(

                        spacing=5,
                        expand=True,

                        controls=[

                            ft.Text(
                                user,
                                color=get_name_color(user),
                                weight="bold",
                            ),

                            ft.Text(
                                text,
                                color="white",
                            )
                        ]
                    )
                ]
            )
        )

        chat_display.controls.append(bubble)

        page.update()

    # =====================================
    # SEND MESSAGE
    # =====================================

    def send_msg(e):

        text = msg_input.value.strip()

        if text == "":
            return

        msg_input.value = ""

        try:

            res = (
                supabase
                .table("messages")
                .insert({

                    "user_name": page.my_user_nick,
                    "text": text,
                    "avatar_url": page.my_avatar

                })
                .execute()
            )

            if res.data:
                page.last_msg_id = res.data[0]["id"]

        except Exception as ex:
            print(ex)

        render_msg(
            page.my_user_nick,
            text,
            page.my_avatar
        )

    # =====================================
    # HEADER
    # =====================================

    header = ft.Container(

        padding=10,
        border_radius=15,
        bgcolor="#111111",

        content=ft.Row(

            alignment="spaceBetween",

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

                        user_text
                    ]
                ),

                ft.Row(

                    controls=[

                        avatar_preview,

                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            icon_color="#00FF00",
                            on_click=toggle_settings,
                        )
                    ]
                )
            ]
        )
    )

    # =====================================
    # INPUT BAR
    # =====================================

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
                    on_click=send_msg,
                )
            ]
        )
    )

    # =====================================
    # LOAD HISTORY
    # =====================================

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
                msg.get("avatar_url", AVATARS[0])
            )

            page.last_msg_id = msg["id"]

    except Exception as ex:
        print(ex)

    # =====================================
    # UPDATE LOOP
    # =====================================

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
                            msg.get("avatar_url", AVATARS[0])
                        )

                    page.last_msg_id = msg["id"]

                page.update()

            except Exception as ex:
                print(ex)

            await asyncio.sleep(2)

    # =====================================
    # UI
    # =====================================

    page.add(
        header,
        settings_panel,
        ft.Container(
            expand=True,
            content=chat_display,
        ),
        input_bar
    )

    # =====================================
    # START
    # =====================================

    page.run_task(check_updates)

# =====================================
# APP
# =====================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
