import flet as ft
import random
import asyncio
import os
import base64
import uuid
import httpx

# =====================================
# SUPABASE (через обычный REST — без тяжёлой библиотеки supabase,
# так приложение надёжно собирается в APK)
# =====================================

URL = "https://nesxjcdhqgstahwfnrba.supabase.co"
KEY = "sb_publishable_FLDVrbaxacdkGUI7UNN0_A_qfq0N7Lt"

REST = f"{URL}/rest/v1/messages"
HEADERS = {"apikey": KEY, "Content-Type": "application/json"}


def db_fetch(params: dict):
    r = httpx.get(REST, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def db_insert(row: dict):
    r = httpx.post(
        REST,
        headers={**HEADERS, "Prefer": "return=representation"},
        json=row,
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def upload_avatar(data: bytes, ext: str, mime: str) -> str:
    """Грузит аватарку в Supabase Storage (бакет 'avatars', public)."""
    name = f"{uuid.uuid4().hex}.{ext}"
    r = httpx.post(
        f"{URL}/storage/v1/object/avatars/{name}",
        headers={"apikey": KEY, "Content-Type": mime},
        content=data,
        timeout=30,
    )
    r.raise_for_status()
    return f"{URL}/storage/v1/object/public/avatars/{name}"


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

HISTORY_LIMIT = 50

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

    page.reply_to_user = ""
    page.reply_to_text = ""

    seen_ids = set()      # id сообщений, которые уже показаны (чтобы не было дублей)
    poll_state = {"last_id": 0}  # до какого id мы уже опрашивали сервер

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
        on_submit=lambda e: page.run_task(send_msg, e),
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

    async def apply_avatar_bytes(data: bytes, filename: str):
        ext = filename.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

        upload_status.value = "Загружаю..."
        page.update()

        avatar_url = None
        try:
            # лучший вариант: файл в Supabase Storage, в сообщения идёт короткая ссылка
            avatar_url = await asyncio.to_thread(upload_avatar, data, ext, mime)
        except Exception as ex:
            print("storage upload failed:", ex)

        if avatar_url is None:
            # запасной вариант: встроить картинку в сообщение (только маленькие файлы)
            if len(data) > 60_000:
                upload_status.value = "Файл слишком большой (нужно до 60 КБ) или не настроен бакет avatars"
                page.update()
                return
            avatar_url = f"data:{mime};base64,{base64.b64encode(data).decode()}"

        page.my_avatar = avatar_url
        avatar_preview.foreground_image_src = avatar_url
        settings_big_avatar.foreground_image_src = avatar_url
        upload_status.value = "Аватарка загружена!"
        page.update()

    async def on_file_picked(e):
        if not e.files:
            return
        file = e.files[0]
        if page.web:
            # на сайте файл сначала уходит на сервер, дальше читаем в on_upload
            upload_url = page.get_upload_url(file.name, 60)
            file_picker.upload([ft.FilePickerUploadFile(file.name, upload_url=upload_url)])
        else:
            # в приложении на телефоне читаем файл напрямую
            try:
                with open(file.path, "rb") as f:
                    data = f.read()
                await apply_avatar_bytes(data, file.name)
            except Exception as ex:
                print(ex)
                upload_status.value = "Ошибка загрузки"
                page.update()

    async def on_upload_progress(e):
        if e.progress == 1.0:
            try:
                with open(os.path.join("uploads", e.file_name), "rb") as f:
                    data = f.read()
                await apply_avatar_bytes(data, e.file_name)
            except Exception as ex:
                print(ex)
                upload_status.value = "Ошибка загрузки"
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
    # BUILD MESSAGE (возвращает контрол, сам ничего не обновляет)
    # =====================================

    def build_msg(user, text, avatar):

        user = user or "?"
        text = text or ""
        avatar = avatar or AVATARS[0]
        user_lower = user.lower()

        # SERVER MESSAGE
        if user_lower in ["server", "сервер"]:
            return ft.Text(
                f"*** SYSTEM: {text} ***",
                color="#FFFF00",
                size=13,
                weight="bold",
            )

        # NAME COLORS
        if user_lower == "кевин":
            name_color = "cyan"
        elif user_lower in ["хан", "солвер"]:
            name_color = "red"
        elif user == page.my_user_nick:
            name_color = "#00FF00"
        else:
            name_color = "#aaaaaa"

        # PARSE REPLY PREFIX
        quoted_user = None
        quoted_text = None
        display_text = text

        if text.startswith("↪REPLY↪"):
            parts = text.split("↪")
            if len(parts) >= 5:
                quoted_user = parts[2]
                quoted_text = parts[3]
                newline_idx = text.find("\n")
                display_text = text[newline_idx + 1:] if newline_idx != -1 else text

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

        return ft.Column(spacing=0, tight=True, controls=col_controls)

    # =====================================
    # ADD MESSAGES (все сообщения от всех, без дублей)
    # =====================================

    def add_messages(rows):

        added = False

        for msg in rows:

            mid = msg.get("id")

            if mid in seen_ids:
                continue

            seen_ids.add(mid)

            chat_display.controls.append(
                build_msg(
                    msg.get("user_name"),
                    msg.get("text"),
                    msg.get("avatar_url"),
                )
            )
            added = True

        if added:
            page.update()

    # =====================================
    # SEND MESSAGE
    # =====================================

    async def send_msg(e):

        text = msg_input.value.strip()

        if text == "":
            return

        full_text = text
        reply_user = page.reply_to_user
        reply_text = page.reply_to_text

        if reply_user:
            full_text = f"↪REPLY↪{reply_user}↪{reply_text}↪\n{text}"

        msg_input.value = ""
        page.reply_to_user = ""
        page.reply_to_text = ""
        reply_bar.visible = False
        page.update()

        try:
            res = await asyncio.to_thread(
                db_insert,
                {
                    "user_name": page.my_user_nick,
                    "text": full_text,
                    "avatar_url": page.my_avatar,
                },
            )
            # показываем своё сообщение сразу; poll не покажет его второй раз (seen_ids)
            add_messages(res)

        except Exception as ex:
            print(ex)
            # не потеряем текст, если отправка не удалась
            msg_input.value = text
            page.snack_bar = ft.SnackBar(ft.Text("Не удалось отправить. Проверьте интернет."))
            page.snack_bar.open = True
            page.update()

        msg_input.focus()

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
            scroll=ft.ScrollMode.AUTO,
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
                    on_click=lambda e: page.run_task(send_msg, e),
                )
            ]
        )
    )

    # =====================================
    # LOAD HISTORY + UPDATE LOOP
    # =====================================

    async def sync_loop():

        # последние HISTORY_LIMIT сообщений (раньше грузились самые СТАРЫЕ 30)
        while True:
            try:
                rows = await asyncio.to_thread(
                    db_fetch,
                    {
                        "select": "*",
                        "order": "id.desc",
                        "limit": str(HISTORY_LIMIT),
                    },
                )
                rows.reverse()
                add_messages(rows)
                if rows:
                    poll_state["last_id"] = max(m["id"] for m in rows)
                break
            except Exception as ex:
                print(ex)
                await asyncio.sleep(3)

        # дальше каждые 2 секунды забираем ВСЕ новые сообщения от всех
        while True:

            await asyncio.sleep(2)

            try:
                rows = await asyncio.to_thread(
                    db_fetch,
                    {
                        "select": "*",
                        "id": f"gt.{poll_state['last_id']}",
                        "order": "id.asc",
                    },
                )

                if rows:
                    add_messages(rows)
                    poll_state["last_id"] = max(m["id"] for m in rows)

            except Exception as ex:
                print(ex)

    # =====================================
    # UI
    # =====================================

    page.overlay.append(file_picker)
    page.overlay.append(settings_dialog)

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    header,
                    ft.Container(
                        expand=True,
                        content=chat_display,
                    ),
                    reply_bar,
                    input_bar,
                ],
            ),
        )
    )

    # =====================================
    # START
    # =====================================

    page.run_task(sync_loop)


# =====================================
# APP
# =====================================

if __name__ == "__main__":

    port = os.getenv("PORT")

    if port:
        # режим сайта (например, на хостинге) — как было раньше
        os.makedirs("uploads", exist_ok=True)
        if not os.getenv("FLET_SECRET_KEY"):
            os.environ["FLET_SECRET_KEY"] = "terminal-chat-upload-secret-key-2024"
        ft.app(target=main, view=None, port=int(port), upload_dir="uploads")
    else:
        # режим приложения (APK на телефоне / окно на компьютере)
        ft.app(target=main)
