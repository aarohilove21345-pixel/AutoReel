"""
main.py
AutoReel - Android app built with Kivy (English UI, matches approved design)
"""
import os
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, BooleanProperty
from kivy.core.window import Window

import storage_helper
import ai_helper
import youtube_uploader
import facebook_uploader

try:
    from plyer import filechooser
except Exception:
    filechooser = None

Window.clearcolor = (0.06, 0.06, 0.06, 1)

VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")

KV = """
#:import dp kivy.metrics.dp

ScreenManager:
    MainScreen:
    SettingsScreen:
    HistoryScreen:

<SectionLabel@Label>:
    color: 0.55,0.55,0.55,1
    font_size: "12sp"
    size_hint_y: None
    height: dp(22)
    halign: "left"
    text_size: self.size

<ToggleRow@BoxLayout>:
    prop_name: ""
    label_text: ""
    size_hint_y: None
    height: dp(50)
    padding: dp(14), 0
    canvas.before:
        Color:
            rgba: 0.12,0.12,0.12,1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
    Label:
        text: root.label_text
        color: 0.95,0.95,0.95,1
        font_size: "14sp"
        halign: "left"
        valign: "middle"
        text_size: self.size
    Button:
        size_hint: None, None
        size: dp(28), dp(28)
        pos_hint: {"center_y": 0.5}
        background_normal: ""
        background_down: ""
        background_color: (0.24,0.80,0.56,1) if getattr(app, root.prop_name) else (0.22,0.22,0.22,1)
        color: 0.03,0.22,0.16,1
        font_size: "16sp"
        bold: True
        text: "OK" if getattr(app, root.prop_name) else ""
        on_release: setattr(app, root.prop_name, not getattr(app, root.prop_name))

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(14)

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(12)

            BoxLayout:
                size_hint: None, None
                size: dp(52), dp(52)
                canvas.before:
                    Color:
                        rgba: 0.10,0.36,0.63,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [14,]
                Label:
                    text: "AR"
                    bold: True
                    color: 1,1,1,1
                    font_size: "16sp"

            BoxLayout:
                orientation: "vertical"
                Label:
                    text: "AutoReel"
                    font_size: "20sp"
                    bold: True
                    color: 1,1,1,1
                    halign: "left"
                    valign: "bottom"
                    text_size: self.size
                Label:
                    text: "Video Auto-Publisher"
                    font_size: "12sp"
                    color: 0.55,0.55,0.55,1
                    halign: "left"
                    valign: "top"
                    text_size: self.size

        BoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(150)
            padding: dp(14)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 0.10,0.10,0.10,1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [14,]
                Color:
                    rgba: 0.32,0.32,0.32,1
                Line:
                    rounded_rectangle: (self.x, self.y, self.width, self.height, 14)
                    dash_length: 6
                    dash_offset: 4
                    width: 1.2

            Widget:
                size_hint_y: None
                height: dp(6)

            BoxLayout:
                size_hint: None, None
                size: dp(40), dp(32)
                pos_hint: {"center_x": 0.5}
                canvas.before:
                    Color:
                        rgba: 0.85,0.68,0.15,1
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [4,]

            Label:
                text: "Select Folder"
                color: 0.85,0.85,0.85,1
                font_size: "13sp"
                size_hint_y: None
                height: dp(24)

            Label:
                text: app.selected_folder or "No folder selected"
                color: 0.5,0.5,0.5,1
                font_size: "10sp"
                size_hint_y: None
                height: dp(16)

            Button:
                text: "Browse"
                size_hint: None, None
                size: dp(120), dp(34)
                pos_hint: {"center_x": 0.5}
                background_normal: ""
                background_down: ""
                background_color: 0.2,0.2,0.2,1
                color: 1,1,1,1
                font_size: "12sp"
                on_release: app.browse_folder()

        SectionLabel:
            text: "PLATFORMS"

        ToggleRow:
            prop_name: "youtube_enabled"
            label_text: "Upload to YouTube"

        ToggleRow:
            prop_name: "facebook_enabled"
            label_text: "Post to Facebook Page"

        SectionLabel:
            text: "AI OPTIONS"

        ToggleRow:
            prop_name: "caption_enabled"
            label_text: "Auto-write Caption"

        ToggleRow:
            prop_name: "hashtags_enabled"
            label_text: "Viral Hashtags"

        Button:
            text: "Upload Now"
            size_hint_y: None
            height: dp(50)
            background_normal: ""
            background_down: ""
            background_color: 1,1,1,1
            color: 0,0,0,1
            font_size: "15sp"
            bold: True
            on_release: app.start_upload()

        Widget:
            size_hint_y: None
            height: dp(1)
            canvas:
                Color:
                    rgba: 0.2,0.2,0.2,1
                Rectangle:
                    pos: self.pos
                    size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(30)
            Button:
                text: "History"
                background_normal: ""
                background_down: ""
                background_color: 0.06,0.06,0.06,1
                color: 0.55,0.55,0.55,1
                font_size: "12sp"
                on_release: app.goto_history()
            Button:
                text: "Settings (API keys)"
                background_normal: ""
                background_down: ""
                background_color: 0.06,0.06,0.06,1
                color: 0.55,0.55,0.55,1
                font_size: "12sp"
                on_release: app.goto_settings()

        ScrollView:
            Label:
                text: app.log_text
                color: 0.7,0.7,0.7,1
                font_size: "11sp"
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
"""
class MainScreen(Screen):
    pass


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings"
        self.inputs = {}
        self.build_ui()

    def build_ui(self):
        cfg = storage_helper.load_config()
        root = BoxLayout(orientation="vertical", padding=20, spacing=8)

        back = Button(text="< Back", size_hint_y=None, height=40,
                       background_normal="", background_down="",
                       background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "main"))
        root.add_widget(back)

        root.add_widget(Label(text="Settings (API keys)", font_size="18sp",
                               bold=True, color=(1, 1, 1, 1),
                               size_hint_y=None, height=36))

        fields = [
            ("YouTube Client ID", "youtube_client_id"),
            ("YouTube Client Secret", "youtube_client_secret"),
            ("YouTube Refresh Token", "youtube_refresh_token"),
            ("Facebook Page ID", "facebook_page_id"),
            ("Facebook Page Access Token", "facebook_page_access_token"),
            ("Anthropic (Claude) API Key", "anthropic_api_key"),
        ]

        scroll = ScrollView()
        inner = BoxLayout(orientation="vertical", spacing=8, size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))

        for label, key in fields:
            inner.add_widget(Label(text=label, color=(0.6, 0.6, 0.6, 1),
                                    size_hint_y=None, height=22, font_size="12sp"))
            ti = TextInput(text=cfg.get(key, ""), multiline=False,
                            size_hint_y=None, height=40,
                            background_color=(0.13, 0.13, 0.13, 1),
                            foreground_color=(1, 1, 1, 1))
            inner.add_widget(ti)
            self.inputs[key] = ti

        scroll.add_widget(inner)
        root.add_widget(scroll)

        save_btn = Button(text="Save", size_hint_y=None, height=48,
                           background_normal="", background_down="",
                           background_color=(0.24, 0.81, 0.56, 1), color=(0.03, 0.22, 0.16, 1))
        save_btn.bind(on_release=self.save)
        root.add_widget(save_btn)

        self.add_widget(root)

    def save(self, *args):
        cfg = storage_helper.load_config()
        for key, ti in self.inputs.items():
            cfg[key] = ti.text.strip()
        storage_helper.save_config(cfg)
        self.manager.current = "main"


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "history"
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=20, spacing=8)

        back = Button(text="< Back", size_hint_y=None, height=40,
                       background_normal="", background_down="",
                       background_color=(0.1, 0.1, 0.1, 1), color=(1, 1, 1, 1))
        back.bind(on_release=lambda *a: setattr(self.manager, "current", "main"))
        root.add_widget(back)

        root.add_widget(Label(text="History", font_size="18sp", bold=True,
                               color=(1, 1, 1, 1), size_hint_y=None, height=36))

        scroll = ScrollView()
        inner = BoxLayout(orientation="vertical", spacing=6, size_hint_y=None)
        inner.bind(minimum_height=inner.setter("height"))

        entries = storage_helper.load_history()
        if not entries:
            inner.add_widget(Label(text="No history yet.", color=(0.6, 0.6, 0.6, 1),
                                    size_hint_y=None, height=30))
        for e in entries:
            txt = (f"[{e['time']}] {e['filename']}\n"
                   f"Platforms: {', '.join(e['platforms']) or '-'}  Status: {e['status']}")
            inner.add_widget(Label(text=txt, color=(0.85, 0.85, 0.85, 1),
                                    font_size="11sp", size_hint_y=None, height=50,
                                    text_size=(Window.width - 60, None)))

        scroll.add_widget(inner)
        root.add_widget(scroll)
        self.add_widget(root)


class AutoReelApp(App):
    selected_folder = StringProperty("")
    youtube_enabled = BooleanProperty(True)
    facebook_enabled = BooleanProperty(True)
    caption_enabled = BooleanProperty(True)
    hashtags_enabled = BooleanProperty(True)
    log_text = StringProperty("Ready.")

    def build(self):
        self.title = "AutoReel"
        self.cfg = storage_helper.load_config()
        return Builder.load_string(KV)

    def goto_settings(self):
        self.root.current = "settings"

    def goto_history(self):
        for screen in list(self.root.screens):
            if screen.name == "history":
                self.root.remove_widget(screen)
        self.root.add_widget(HistoryScreen())
        self.root.current = "history"

    def browse_folder(self):
        if filechooser is None:
            self.log("File picker not available on this platform.")
            return
        filechooser.choose_dir(on_selection=self._folder_selected)

    def _folder_selected(self, selection):
        if selection:
            self.selected_folder = selection[0]

    @mainthread
    def log(self, msg):
        self.log_text += "\n" + msg

    def start_upload(self):
        if not self.selected_folder or not os.path.isdir(self.selected_folder):
            self.log("Please select a folder first.")
            return
        if not self.youtube_enabled and not self.facebook_enabled:
            self.log("Enable at least one platform.")
            return
        threading.Thread(target=self._run_uploads, daemon=True).start()

    def _run_uploads(self):
        cfg = storage_helper.load_config()
        folder = self.selected_folder
        videos = [f for f in os.listdir(folder) if f.lower().endswith(VIDEO_EXTENSIONS)]

        if not videos:
            self.log("No video files found in this folder.")
            return

        for filename in videos:
            file_path = os.path.join(folder, filename)
            self.log(f"--- {filename} ---")
            caption, hashtags = "", ""

            try:
                if self.caption_enabled:
                    caption = ai_helper.generate_caption(cfg["anthropic_api_key"], filename)
                    self.log(f"Caption: {caption}")
                if self.hashtags_enabled:
                    hashtags = ai_helper.generate_hashtags(cfg["anthropic_api_key"], filename, caption)
                    self.log(f"Hashtags: {hashtags}")
            except Exception as e:
                self.log(f"AI generation failed: {e}")

            description = (caption + "\n\n" + hashtags).strip()
            platforms_done = []

            if self.youtube_enabled:
                try:
                    vid_id = youtube_uploader.upload_video(
                        cfg["youtube_client_id"], cfg["youtube_client_secret"],
                        cfg["youtube_refresh_token"], file_path,
                        title=os.path.splitext(filename)[0],
                        description=description,
                        tags=hashtags.replace("#", "").split() if hashtags else [],
                    )
                    self.log(f"YouTube OK: https://youtu.be/{vid_id}")
                    platforms_done.append("YouTube")
                except Exception as e:
                    self.log(f"YouTube failed: {e}")

            if self.facebook_enabled:
                try:
                    fb_id = facebook_uploader.upload_video(
                        cfg["facebook_page_id"], cfg["facebook_page_access_token"],
                        file_path, description=description,
                    )
                    self.log(f"Facebook OK (id: {fb_id})")
                    platforms_done.append("Facebook")
                except Exception as e:
                    self.log(f"Facebook failed: {e}")

            storage_helper.add_history(filename, platforms_done,
                                        "done" if platforms_done else "failed")

        self.log("All videos processed.")


if __name__ == "__main__":
    AutoReelApp().run()
