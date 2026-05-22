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
    # AVATAR PREVIEW
    # =====================================

    avatar_preview = ft.CircleAvatar(
        foreground_image_src=page.my_avatar,
        radius=20,
    )

    # =====================================
    # AVATAR MENU
    # =====================================

    avatar_menu = ft.Column(
        visible=False,
        spacing=5,
    )

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
                                color="#00FF00",
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
    # AVATAR SELECT
    # =====================================

    def choose_avatar(e):

        selected = e.control.data

        page.my_avatar = selected

        avatar_preview.foreground_image_src = selected

        avatar_menu.visible = False

        page.update()

    # =====================================
    # OPEN MENU
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
    # HEADER
    # =====================================

    header = ft.Container(

        padding=10,
        border_radius=15,
        bgcolor="#111111",

        content=ft.Column(

            spacing=10,

            controls=[

                ft.Row(

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

                                ft.Text(
                                    page.my_user_nick,
                                    color="#008800",
                                )
                            ]
                        ),

                        ft.Row(

                            controls=[

                                avatar_preview,

                                ft.IconButton(
                                    icon=ft.Icons.PERSON,
                                    icon_color="#00FF00",
                                    on_click=open_avatar_menu,
                                )
                            ]
                        )
                    ]
                ),

                avatar_menu
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
