"""
main.py
AutoReel - Android app built with Kivy
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

Window.clearcolor = (0.08, 0.08, 0.08, 1)

VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm")

KV = """
ScreenManager:
    MainScreen:
    SettingsScreen:
    HistoryScreen:

<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(8)

        Label:
            text: "AutoReel"
            font_size: "24sp"
            bold: True
            color: 1,1,1,1
            size_hint_y: None
            height: dp(34)

        Label:
            text: "Video Auto-Publisher"
            font_size: "13sp"
            color: 0.6,0.6,0.6,1
            size_hint_y: None
            height: dp(20)

        Label:
            text: "Selected: " + (app.selected_folder or "No folder selected")
            color: 0.9,0.9,0.9,1
            font_size: "12sp"
            size_hint_y: None
            height: dp(40)
            text_size: self.width, None

        Button:
            text: "Browse Folder"
            size_hint_y: None
            height: dp(40)
            background_color: 0.2,0.2,0.2,1
            on_release: app.browse_folder()

        Label:
            text: "Platforms"
            color: 0.6,0.6,0.6,1
            font_size: "12sp"
            size_hint_y: None
            height: dp(20)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            Label:
                text: "Upload to YouTube"
                color: 1,1,1,1
            Switch:
                active: True
                size_hint_x: None
                width: dp(60)
                on_active: app.youtube_enabled = self.active

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            Label:
                text: "Post to Facebook Page"
                color: 1,1,1,1
            Switch:
                active: True
                size_hint_x: None
                width: dp(60)
                on_active: app.facebook_enabled = self.active

        Label:
            text: "AI Options"
            color: 0.6,0.6,0.6,1
            font_size: "12sp"
            size_hint_y: None
            height: dp(20)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            Label:
                text: "Auto-write Caption"
                color: 1,1,1,1
            Switch:
                active: True
                size_hint_x: None
                width: dp(60)
                on_active: app.caption_enabled = self.active

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            Label:
                text: "Viral Hashtags"
                color: 1,1,1,1
            Switch:
                active: True
                size_hint_x: None
                width: dp(60)
                on_active: app.hashtags_enabled = self.active

        Button:
            text: "Upload Now"
            size_hint_y: None
            height: dp(48)
            background_color: 1,1,1,1
            color: 0,0,0,1
            bold: True
            on_release: app.start_upload()

        BoxLayout:
            size_hint_y: None
            height: dp(36)
            Button:
                text: "History"
                background_color: 0.1,0.1,0.1,1
                on_release: app.goto_history()
            Button:
                text: "Settings"
                background_color: 0.1,0.1,0.1,1
                on_release: app.goto_settings()

        ScrollView:
            Label:
                text: app.log_text
                color: 0.8,0.8,0.8,1
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
                       background_color=(0.1, 0.1, 0.1, 1))
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
                           background_color=(0.24, 0.81, 0.56, 1))
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
                       background_color=(0.1, 0.1, 0.1, 1))
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
        for screen in self.root.screens:
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
