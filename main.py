import flet as ft
import random
import asyncio
import os
import base64
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
    page.bgcolor = "#0a0a0a"
    page.padding = ft.padding.all(8)

    # =====================================
    # USER
    # =====================================

    page.my_user_nick = f"User.._{random.randint(1000,9999)}"
    page.my_avatar = random.choice(AVATARS)

    page.last_msg_id = 0
    page.reply_to_user = ""
    page.reply_to_text = ""

    # =====================================
    # CHAT
    # =====================================

    chat_display = ft.ListView(
        expand=True,
        spacing=2,
        auto_scroll=True,
        padding=ft.padding.symmetric(horizontal=4, vertical=4),
    )

    msg_input = ft.TextField(
        hint_text="type message and press Enter...",
        hint_style=ft.TextStyle(color="#334433"),
        expand=True,
        color="#00FF00",
        border_color="transparent",
        focused_border_color="transparent",
        bgcolor="transparent",
        cursor_color="#00FF00",
        on_submit=lambda e: send_msg(e),
    )

    reply_bar_label = ft.Text(
        "",
        color="#888888",
        size=12,
        expand=True,
        italic=True,
        no_wrap=True,
        overflow="ellipsis",
    )

    reply_bar = ft.Container(
        visible=False,
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
        bgcolor="#060e06",
        border=ft.border.only(
            top=ft.BorderSide(1, "#1a2a1a"),
            left=ft.BorderSide(2, "#00AA00"),
        ),
        content=ft.Row(
            spacing=6,
            vertical_alignment="center",
            controls=[
                ft.Text("↩", color="#00AA00", size=13),
                reply_bar_label,
                ft.IconButton(
                    icon=ft.icons.CLOSE,
                    icon_color="#336633",
                    icon_size=14,
                    on_click=lambda e: cancel_reply(e),
                ),
            ]
        )
    )

    # =====================================
    # SETTINGS
    # =====================================

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

    upload_status = ft.Text(
        "",
        color="#00FF00",
        size=12,
    )

    # =====================================
    # FILE PICKER
    # =====================================

    def on_file_picked(e):
        if not e.files:
            return
        file = e.files[0]
        upload_url = page.get_upload_url(file.name, 60)
        file_picker.upload([ft.FilePickerUploadFile(file.name, upload_url=upload_url)])

    def on_upload_progress(e):
        if e.progress == 1.0:
            file_path = os.path.join("uploads", e.file_name)
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                ext = e.file_name.rsplit(".", 1)[-1].lower()
                mime = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"
                avatar_url = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            except Exception:
                avatar_url = f"/uploads/{e.file_name}"
            page.my_avatar = avatar_url
            avatar_preview.foreground_image_src = avatar_url
            settings_big_avatar.foreground_image_src = avatar_url
            upload_status.value = "Аватарка загружена!"
            page.update()
        elif e.error:
            upload_status.value = "Ошибка загрузки"
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked, on_upload=on_upload_progress)

    # =====================================
    # USER LABEL
    # =====================================

    user_text = ft.Text(
        page.my_user_nick,
        color="#00CC00",
        weight="bold",
        size=13,
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

    def toggle_settings(e):
        settings_dialog.open = True
        page.update()

    def close_settings(e):
        settings_dialog.open = False
        page.update()

    # =====================================
    # REPLY HELPERS
    # =====================================

    def cancel_reply(e):
        page.reply_to_user = ""
        page.reply_to_text = ""
        reply_bar.visible = False
        page.update()

    def set_reply(reply_user, reply_text):
        page.reply_to_user = reply_user
        page.reply_to_text = reply_text[:80]
        snippet = reply_text[:55] + ("…" if len(reply_text) > 55 else "")
        reply_bar_label.value = f"{reply_user}: {snippet}"
        reply_bar.visible = True
        msg_input.focus()
        page.update()

    # =====================================
    # RENDER MESSAGE
    # =====================================

    def render_msg(user, text, avatar):

        user_lower = user.lower()

        # =====================================
        # SERVER MESSAGE
        # =====================================

        if user_lower in ["server", "сервер"]:

            chat_display.controls.append(
                ft.Text(
                    f"*** SYSTEM: {text} ***",
                    color="#FFFF00",
                    size=13,
                    weight="bold",
                )
            )

            page.update()
            return

        # =====================================
        # NAME COLORS
        # =====================================

        if user_lower == "кевин":
            name_color = "cyan"

        elif user_lower in ["хан", "солвер"]:
            name_color = "red"

        elif user == page.my_user_nick:
            name_color = "#00FF00"

        else:
            name_color = "#aaaaaa"

        # =====================================
        # PARSE REPLY PREFIX
        # =====================================

        quoted_user = None
        quoted_text = None
        display_text = text

        if text.startswith("↪REPLY↪"):
            parts = text.split("↪")
            # ['', 'REPLY', username, quoted_text, '', '\nactual']
            if len(parts) >= 5:
                quoted_user = parts[2]
                quoted_text = parts[3]
                newline_idx = text.find("\n")
                display_text = text[newline_idx + 1:] if newline_idx != -1 else text

        # =====================================
        # TERMINAL-STYLE MESSAGE ROW
        # =====================================

        def make_reply_fn(u, t):
            def fn(e):
                set_reply(u, t)
            return fn

        reply_btn = ft.IconButton(
            icon=ft.icons.REPLY,
            icon_color="#1a3a1a",
            icon_size=14,
            tooltip="Ответить",
            on_click=make_reply_fn(user, display_text),
        )

        message_row = ft.Row(
            vertical_alignment="center",
            spacing=6,
            controls=[
                ft.CircleAvatar(
                    foreground_image_src=avatar,
                    radius=12,
                ),
                ft.Text(
                    user,
                    color=name_color,
                    weight="bold",
                    size=13,
                    no_wrap=True,
                ),
                ft.Text(
                    ">",
                    color="#1a3a1a",
                    size=13,
                ),
                ft.Text(
                    display_text,
                    color="#c8c8c8",
                    size=13,
                    expand=True,
                    selectable=True,
                ),
                reply_btn,
            ]
        )

        col_controls = []

        if quoted_user:
            col_controls.append(
                ft.Container(
                    padding=ft.padding.only(left=32, bottom=1),
                    content=ft.Row(
                        spacing=6,
                        controls=[
                            ft.Container(
                                width=2,
                                height=16,
                                bgcolor="#336633",
                                border_radius=1,
                            ),
                            ft.Text(
                                f"↩ {quoted_user}: {quoted_text}",
                                color="#446644",
                                size=11,
                                italic=True,
                                no_wrap=True,
                                overflow="ellipsis",
                            ),
                        ]
                    )
                )
            )

        col_controls.append(message_row)

        chat_display.controls.append(
            ft.Column(spacing=0, tight=True, controls=col_controls)
        )

        page.update()

    # =====================================
    # SEND MESSAGE
    # =====================================

    def send_msg(e):

        text = msg_input.value.strip()

        if text == "":
            return

        msg_input.value = ""

        full_text = text
        if page.reply_to_user:
            full_text = f"↪REPLY↪{page.reply_to_user}↪{page.reply_to_text}↪\n{text}"
            page.reply_to_user = ""
            page.reply_to_text = ""
            reply_bar.visible = False

        try:

            res = (
                supabase
                .table("messages")
                .insert({

                    "user_name": page.my_user_nick,
                    "text": full_text,
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
            full_text,
            page.my_avatar
        )

    # =====================================
    # SETTINGS DIALOG
    # =====================================

    settings_dialog = ft.AlertDialog(
        modal=True,
        bgcolor="#0d1a0d",
        title=ft.Row(
            spacing=12,
            controls=[
                settings_big_avatar,
                settings_nick
            ]
        ),
        content=ft.Column(
            width=300,
            spacing=12,
            tight=True,
            controls=[
                ft.ElevatedButton(
                    "Сменить аватар",
                    on_click=open_avatar_menu
                ),
                avatar_menu,
                ft.ElevatedButton(
                    "Загрузить свою аватарку",
                    icon=ft.icons.UPLOAD,
                    on_click=lambda _: file_picker.pick_files(
                        allow_multiple=False,
                        allowed_extensions=["png", "jpg", "jpeg", "gif", "webp"],
                    ),
                ),
                upload_status,
                nick_input,
                ft.ElevatedButton(
                    "Сохранить ник",
                    on_click=change_nick
                ),
            ]
        ),
        actions=[
            ft.TextButton(
                "[ ЗАКРЫТЬ ]",
                style=ft.ButtonStyle(color="#00FF00"),
                on_click=close_settings,
            ),
        ],
        actions_alignment="end",
    )

    # =====================================
    # HEADER
    # =====================================

    header = ft.Container(

        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border=ft.border.only(bottom=ft.BorderSide(1, "#1a2a1a")),
        bgcolor="#050505",

        content=ft.Row(

            alignment="spaceBetween",

            controls=[

                ft.Row(
                    spacing=6,
                    expand=True,
                    controls=[
                        ft.Text("■", color="#00FF00", size=10),
                        ft.Text(
                            "TERMINAL CHAT",
                            size=13,
                            weight="bold",
                            color="#00FF00",
                        ),
                        ft.Text("|", color="#1a3a1a", size=13),
                        user_text,
                    ]
                ),

                ft.Row(
                    spacing=2,
                    controls=[
                        avatar_preview,
                        ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            icon_color="#336633",
                            icon_size=18,
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

        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border=ft.border.only(top=ft.BorderSide(1, "#1a2a1a")),
        bgcolor="#050505",

        content=ft.Row(

            spacing=4,
            vertical_alignment="center",

            controls=[

                ft.Text(
                    ">_",
                    color="#00FF00",
                    size=14,
                    weight="bold",
                ),

                msg_input,

                ft.IconButton(
                    icon=ft.icons.SEND,
                    icon_color="#336633",
                    icon_size=18,
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

    page.overlay.append(file_picker)
    page.overlay.append(settings_dialog)

    page.add(
        header,
        ft.Container(
            expand=True,
            content=chat_display,
        ),
        reply_bar,
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
    os.makedirs("uploads", exist_ok=True)
    if not os.getenv("FLET_SECRET_KEY"):
        os.environ["FLET_SECRET_KEY"] = "terminal-chat-upload-secret-key-2024"
    port = int(os.getenv("PORT", 8080))
    ft.app(target=main, view=None, port=port, upload_dir="uploads")
