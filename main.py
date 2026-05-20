import flet as ft
import random
import asyncio
from supabase import create_client

# =========================================
# SUPABASE
# =========================================

URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"

supabase = create_client(URL, KEY)

# =========================================
# АВАТАРКИ
# =========================================

AVATARS = [
    "https://api.dicebear.com/7.x/bottts/png?seed=1",
    "https://api.dicebear.com/7.x/bottts/png?seed=2",
    "https://api.dicebear.com/7.x/bottts/png?seed=3",
    "https://api.dicebear.com/7.x/bottts/png?seed=4",
    "https://api.dicebear.com/7.x/bottts/png?seed=5",
]

# =========================================
# MAIN
# =========================================

def main(page: ft.Page):

    # =========================================
    # PAGE
    # =========================================

    page.title = "TERMINAL CHAT"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0b0f14"
    page.padding = 10

    # =========================================
    # USER
    # =========================================

    if not hasattr(page, "my_user_nick"):
        page.my_user_nick = f"USER_{random.randint(1000,9999)}"

    if not hasattr(page, "my_avatar"):
        page.my_avatar = random.choice(AVATARS)

    page.last_msg_id = 0

    # =========================================
    # CHAT
    # =========================================

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

    # =========================================
    # АВАТАР
    # =========================================

    avatar_preview = ft.CircleAvatar(
        foreground_image_url=page.my_avatar,
        radius=22,
    )

    avatar_wrap = ft.Wrap(
        spacing=10,
        run_spacing=10,
    )

    avatar_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Выбор аватара"),
        content=ft.Container(
            width=350,
            height=350,
            content=avatar_wrap,
        ),
    )

    page.dialog = avatar_dialog

    # =========================================
    # РЕНДЕР СООБЩЕНИЙ
    # =========================================

    def render_msg(user, text, avatar):

        user_lower = user.lower()

        # =========================================
        # SYSTEM
        # =========================================

        if user_lower in ["server", "сервер"]:

            chat_display.controls.append(

                ft.Container(
                    bgcolor="#151515",
                    border_radius=15,
                    padding=10,

                    content=ft.Text(
                        f"[SYSTEM]: {text}",
                        color="yellow",
                        weight="bold",
                    )
                )
            )

            page.update()
            return

        # =========================================
        # COLORS
        # =========================================

        if user_lower == "кевин":
            color = "cyan"

        elif user_lower in ["хан", "солвер"]:
            color = "red"

        else:
            color = "#00FF00"

        # =========================================
        # MESSAGE
        # =========================================

        bubble = ft.Container(

            bgcolor="#1c1c1c",
            border_radius=15,
            padding=10,

            content=ft.Row(

                vertical_alignment=ft.CrossAxisAlignment.START,

                controls=[

                    ft.CircleAvatar(
                        foreground_image_url=avatar,
                        radius=20,
                    ),

                    ft.Column(

                        spacing=5,
                        expand=True,

                        controls=[

                            ft.Text(
                                f"[{user}]",
                                color=color,
                                weight="bold",
                            ),

                            ft.Text(
                                text,
                                color="white",
                                selectable=True,
                            )
                        ]
                    )
                ]
            )
        )

        chat_display.controls.append(bubble)

        page.update()

    # =========================================
    # SEND MESSAGE
    # =========================================

    def send_msg(e):

        text = msg_input.value.strip()

        if not text:
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

    msg_input.on_submit = send_msg

    # =========================================
    # AVATAR PICKER
    # =========================================

    def open_avatar_picker(e):

        avatar_wrap.controls.clear()

        for avatar in AVATARS:

            def select(ev, selected=avatar):

                page.my_avatar = selected

                avatar_preview.foreground_image_url = selected

                avatar_dialog.open = False

                page.update()

            avatar_wrap.controls.append(

                ft.GestureDetector(

                    on_tap=select,

                    content=ft.Container(

                        width=80,
                        height=80,

                        border_radius=20,
                        bgcolor="#111111",

                        alignment=ft.alignment.center,

                        content=ft.CircleAvatar(
                            foreground_image_url=avatar,
                            radius=28,
                        )
                    )
                )
            )

        avatar_dialog.open = True

        page.update()

    # =========================================
    # HEADER
    # =========================================

    header = ft.Container(

        padding=12,
        border_radius=16,
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
                            color="#00FF00",
                        ),

                        ft.Text(
                            f"ID: {page.my_user_nick}",
                            color="#008800",
                            size=12,
                        )
                    ]
                ),

                ft.Row(

                    controls=[

                        avatar_preview,

                        ft.IconButton(
                            icon=ft.Icons.PERSON,
                            icon_color="#00FF00",
                            on_click=open_avatar_picker,
                        )
                    ]
                )
            ]
        )
    )

    # =========================================
    # INPUT BAR
    # =========================================

    input_bar = ft.Container(

        padding=10,
        border_radius=16,
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

    # =========================================
    # HISTORY
    # =========================================

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

    # =========================================
    # UPDATE LOOP
    # =========================================

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

    # =========================================
    # UI
    # =========================================

    page.add(
        header,
        ft.Container(
            expand=True,
            content=chat_display,
        ),
        input_bar
    )

    # =========================================
    # START LOOP
    # =========================================

    page.run_task(check_updates)

# =========================================
# START
# =========================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port)
