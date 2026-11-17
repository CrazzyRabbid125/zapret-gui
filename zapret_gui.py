import ctypes
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request
import webbrowser
import winreg

from PIL import Image, ImageDraw
import pystray

APP_VERSION = "1.0"
GITHUB_REPO = "stepanchick646464-afk/zapret-gui"
HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

DNS_PRESETS = {
    "AdGuard DNS (No Ads)": ("94.140.14.14", "94.140.15.15"),
    "AdGuard DNS (Family)": ("94.140.14.15", "94.140.15.16"),
    "Comss.one DNS (AI & Geo)": ("83.220.169.155", "212.109.195.93"),
    "Cloudflare (1.1.1.1)": ("1.1.1.1", "1.0.0.1"),
    "Google DNS (8.8.8.8)": ("8.8.8.8", "8.8.4.4"),
    "Yandex.DNS (Basic)": ("77.88.8.8", "77.88.8.1"),
    "Custom (Manual)": ("", ""),
}

LANGS = {
    "ru": {
        "lang_label": "Язык:",
        "theme_label": "Тема:",
        "theme_system": "Как в системе",
        "theme_classic": "Классическая",
        "theme_light": "Светлая",
        "theme_dark": "Темная",
        "status_box": "Состояние обхода",
        "status_checking": "Проверка статуса...",
        "status_active": "● АКТИВЕН (обход работает)",
        "status_stopped": "● ОСТАНОВЛЕН",
        "strat_box": "Выбор стратегии (.bat / .cmd)",
        "no_scripts": "Скрипты запуска не найдены",
        "btn_start": "▶ Запустить",
        "btn_stop": "⏹ Остановить",
        "btn_auto": "🔍 Автоподбор",
        "btn_auto_stop": "⏹ Стоп подбор",
        "btn_ping": "📶 Пинг / Связь",
        "auto_testing": "Проверка [{idx}/{total}]: {name}...",
        "auto_found": "Найдена рабочая стратегия:\n{name}",
        "auto_not_found": "Ни одна стратегия не прошла проверку связи.",
        "auto_stopped": "Автоподбор остановлен пользователем.",
        "autostart_box": "Автоматизация и настройки",
        "chk_win_start": "Запускать лаунчер вместе с Windows (в трей)",
        "chk_auto_bypass": "Автоматически запускать обход при старте",
        "tools_box": "Инструменты, списки и сеть",
        "btn_lists_edit": "📋 Редактор списков (lists)",
        "btn_lists_dir": "📁 Папка списков",
        "btn_hosts": "📝 Редактор hosts",
        "btn_dns": "🌐 Настройка DNS",
        "btn_service": "⚙️ service.bat",
        "btn_update": "🔄 Обновления (v1.0)",
        "update_avail": "🆕 Доступна v{ver}!",
        "update_latest": "У вас установлена актуальная версия ({ver}).",
        "update_ask": "Доступна новая версия v{ver}!\nОткрыть страницу загрузки на GitHub?",
        "update_err": "Не удалось проверить обновления с GitHub.",
        "tray_open": "Открыть окно",
        "tray_start": "Запустить обход",
        "tray_stop": "Остановить обход",
        "tray_exit": "Выход",
        "lists_title": "Редактор списков доменов",
        "lists_select": "Выберите файл списка:",
        "lists_save": "💾 Сохранить и перезапустить обход",
        "lists_saved_msg": "Список сохранен! Если обход был активен, он перезапущен.",
        "err_title": "Ошибка",
        "warn_title": "Внимание",
        "done_title": "Готово",
        "err_file_not_found": "Файл {file} не найден в папке программы.",
        "err_start": "Ошибка запуска",
        "err_stop": "Ошибка остановки",
        "warn_no_service": "Файл управления службой не найден.",
        "warn_no_lists": "Папка со списками не найдена.",
        "ping_title": "Пинг и проверка доступности (9 сервисов)",
        "ping_btn_run": "🔄 Проверить все сейчас",
        "ping_checking": "Проверка...",
        "ping_ok": "Доступен ({ms} мс)",
        "ping_fail": "Недоступен (Таймаут)",
        "hosts_title": "Редактор системного файла hosts",
        "hosts_path_info": "Путь: {path} (изменения применяются сразу)",
        "hosts_save": "💾 Сохранить и обновить DNS",
        "hosts_reload": "🔄 Обновить из файла",
        "hosts_close": "Закрыть",
        "hosts_saved_msg": "Файл hosts успешно сохранен, а кэш DNS обновлен!",
        "hosts_err_read": "Не удалось открыть файл hosts:\n{err}",
        "hosts_err_perm": "Недостаточно прав для записи в hosts. Проверьте антивирус.",
        "hosts_err_save": "Не удалось сохранить файл:\n{err}",
        "dns_title": "Настройка DNS-серверов",
        "dns_step1": "1. Сетевое подключение (интерфейс):",
        "dns_step2": "2. Выберите готовый DNS или введите свой:",
        "dns_primary": "Предпочитаемый DNS:",
        "dns_secondary": "Альтернативный DNS:",
        "dns_curr_check": "Текущий DNS: проверка...",
        "dns_curr_val": "Текущий DNS адаптера: {ips}",
        "dns_curr_auto": "Текущий DNS адаптера: Автоматически (от провайдера)",
        "dns_no_adapters": "Сетевые адаптеры не найдены",
        "dns_apply": "✅ Применить DNS",
        "dns_reset": "🔄 Сбросить на Авто",
        "dns_err_ip1": "Введите корректный IP для предпочитаемого DNS.",
        "dns_err_ip2": "Введите корректный IP для альтернативного DNS.",
        "dns_applied_msg": "DNS успешно применен для подключения «{adapter}»!",
        "dns_reset_msg": "Для «{adapter}» возвращено автоматическое получение DNS.",
    },
    "en": {
        "lang_label": "Lang:",
        "theme_label": "Theme:",
        "theme_system": "System",
        "theme_classic": "Classic",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "status_box": "Bypass Status",
        "status_checking": "Checking status...",
        "status_active": "● ACTIVE (bypass running)",
        "status_stopped": "● STOPPED",
        "strat_box": "Select Strategy (.bat / .cmd)",
        "no_scripts": "No launch scripts found",
        "btn_start": "▶ Start",
        "btn_stop": "⏹ Stop",
        "btn_auto": "🔍 Auto-Select",
        "btn_auto_stop": "⏹ Stop Search",
        "btn_ping": "📶 Ping / Test",
        "auto_testing": "Testing [{idx}/{total}]: {name}...",
        "auto_found": "Working strategy found:\n{name}",
        "auto_not_found": "No working strategy found during test.",
        "auto_stopped": "Auto-search stopped by user.",
        "autostart_box": "Automation & Startup",
        "chk_win_start": "Run launcher at Windows startup (minimized to tray)",
        "chk_auto_bypass": "Auto-start bypass when launcher opens",
        "tools_box": "Tools, Lists & Network",
        "btn_lists_edit": "📋 Edit Domain Lists",
        "btn_lists_dir": "📁 Lists Folder",
        "btn_hosts": "📝 Edit hosts",
        "btn_dns": "🌐 DNS Settings",
        "btn_service": "⚙️ service.bat",
        "btn_update": "🔄 Updates (v1.0)",
        "update_avail": "🆕 v{ver} Available!",
        "update_latest": "You are using the latest version ({ver}).",
        "update_ask": "New version v{ver} is available!\nOpen GitHub download page?",
        "update_err": "Failed to check updates from GitHub.",
        "tray_open": "Open Window",
        "tray_start": "Start Bypass",
        "tray_stop": "Stop Bypass",
        "tray_exit": "Exit",
        "lists_title": "Domain Lists Editor",
        "lists_select": "Select list file:",
        "lists_save": "💾 Save & Restart Bypass",
        "lists_saved_msg": "List saved! Active bypass has been restarted.",
        "err_title": "Error",
        "warn_title": "Warning",
        "done_title": "Done",
        "err_file_not_found": "File {file} not found in the program folder.",
        "err_start": "Launch Error",
        "err_stop": "Stop Error",
        "warn_no_service": "Service management script not found.",
        "warn_no_lists": "Lists folder not found.",
        "ping_title": "Ping & Connection Test (9 Services)",
        "ping_btn_run": "🔄 Test All Now",
        "ping_checking": "Testing...",
        "ping_ok": "Online ({ms} ms)",
        "ping_fail": "Unreachable (Timeout)",
        "hosts_title": "System hosts File Editor",
        "hosts_path_info": "Path: {path} (changes apply immediately)",
        "hosts_save": "💾 Save & Flush DNS",
        "hosts_reload": "🔄 Reload File",
        "hosts_close": "Close",
        "hosts_saved_msg": "The hosts file was saved and DNS cache flushed!",
        "hosts_err_read": "Failed to open hosts file:\n{err}",
        "hosts_err_perm": "Access denied writing to hosts. Check your antivirus.",
        "hosts_err_save": "Failed to save file:\n{err}",
        "dns_title": "DNS Server Settings",
        "dns_step1": "1. Network Connection (Interface):",
        "dns_step2": "2. Choose a DNS Preset or Enter Custom IP:",
        "dns_primary": "Preferred DNS:",
        "dns_secondary": "Alternate DNS:",
        "dns_curr_check": "Current DNS: checking...",
        "dns_curr_val": "Current Adapter DNS: {ips}",
        "dns_curr_auto": "Current Adapter DNS: Automatic (DHCP)",
        "dns_no_adapters": "No network adapters found",
        "dns_apply": "✅ Apply DNS",
        "dns_reset": "🔄 Reset to Auto",
        "dns_err_ip1": "Enter a valid IP address for Preferred DNS.",
        "dns_err_ip2": "Enter a valid IP address for Alternate DNS.",
        "dns_applied_msg": "DNS successfully applied to «{adapter}»!",
        "dns_reset_msg": "Automatic DNS restored for «{adapter}».",
    },
}

THEMES = {
    "classic": {
        "bg": "#dcdad5",
        "fg": "#000000",
        "sub_fg": "#444444",
        "btn_bg": "#dcdad5",
        "btn_active": "#c9c7c2",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "active_green": "#1b8a2e",
        "stopped_red": "#c92a2a",
    },
    "light": {
        "bg": "#f5f5f5",
        "fg": "#111111",
        "sub_fg": "#555555",
        "btn_bg": "#e4e4e4",
        "btn_active": "#d4d4d4",
        "entry_bg": "#ffffff",
        "entry_fg": "#000000",
        "active_green": "#1b8a2e",
        "stopped_red": "#c92a2a",
    },
    "dark": {
        "bg": "#1e1e1e",
        "fg": "#f0f0f0",
        "sub_fg": "#aaaaaa",
        "btn_bg": "#333333",
        "btn_active": "#454545",
        "entry_bg": "#2b2b2b",
        "entry_fg": "#f0f0f0",
        "active_green": "#4ade80",
        "stopped_red": "#f87171",
    },
}
def get_system_theme():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        val, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if val == 1 else "dark"
    except Exception:
        return "light"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def run_hidden(cmd_list):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.run(cmd_list, startupinfo=startupinfo, capture_output=True, text=True, encoding="cp866", errors="ignore")


def set_windows_autostart(enable):
    task_name = "ZapretUniversalGUI_AutoStart"
    exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
    if enable:
        cmd = ["schtasks", "/Create", "/TN", task_name, "/TR", f'"{exe_path}" --tray', "/SC", "ONLOGON", "/RL", "HIGHEST", "/F"]
        run_hidden(cmd)
    else:
        run_hidden(["schtasks", "/Delete", "/TN", task_name, "/F"])


def check_url_ping(url, timeout=3.0):
    start_t = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(64)
        ms = int((time.perf_counter() - start_t) * 1000)
        return True, ms
    except Exception:
        return False, 0


def check_tcp_ping(host, port=443, timeout=2.5):
    start_t = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        ms = int((time.perf_counter() - start_t) * 1000)
        return True, ms
    except Exception:
        return False, 0


def create_tray_icon_image(active=False):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bg_color = (27, 138, 46, 255) if active else (201, 42, 42, 255)
    draw.ellipse((4, 4, 60, 60), fill=bg_color)
    draw.polygon([(26, 20), (46, 32), (26, 44)], fill=(255, 255, 255, 255))
    return img


class PingTestWindow(tk.Toplevel):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(self.app.tr("ping_title"))
        self.geometry("440x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.targets = [
            ("YouTube (HTTPS)", "url", "https://youtube.com"),
            ("Discord (HTTPS)", "url", "https://discord.com"),
            ("Google (HTTPS)", "url", "https://google.com"),
            ("Google Gemini (HTTPS)", "url", "https://google.com"),
            ("ChatGPT / OpenAI (HTTPS)", "url", "https://chatgpt.com"),
            ("GitHub (HTTPS)", "url", "https://github.com"),
            ("Telegram Web (HTTPS)", "url", "https://telegram.org"),
            ("Steam Store (HTTPS)", "url", "https://steampowered.com"),
            ("Cloudflare DNS (1.1.1.1)", "tcp", ("1.1.1.1", 443)),
        ]
        self.result_labels = {}
        self.setup_ui()
        self.apply_theme()
        self.run_tests()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        for name, _, _ in self.targets:
            row = ttk.Frame(main_frame)
            row.pack(fill=tk.X, pady=5)
            ttk.Label(row, text=name, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            res_lbl = ttk.Label(row, text=self.app.tr("ping_checking"), font=("Segoe UI", 9, "bold"))
            res_lbl.pack(side=tk.RIGHT)
            self.result_labels[name] = res_lbl

        self.run_btn = ttk.Button(main_frame, text=self.app.tr("ping_btn_run"), command=self.run_tests)
        self.run_btn.pack(fill=tk.X, pady=(15, 0), ipady=5)

    def apply_theme(self):
        t = THEMES[self.app.get_effective_theme()]
        self.configure(bg=t["bg"])

    def run_tests(self):
        self.run_btn.config(state=tk.DISABLED)
        t = THEMES[self.app.get_effective_theme()]
        for name in self.result_labels:
            self.result_labels[name].config(text=self.app.tr("ping_checking"), foreground=t["sub_fg"])
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        t = THEMES[self.app.get_effective_theme()]
        for name, mode, target in self.targets:
            if mode == "url":
                ok, ms = check_url_ping(target)
            else:
                ok, ms = check_tcp_ping(target, target)

            if ok:
                txt = self.app.tr("ping_ok").format(ms=ms)
                color = t["active_green"]
            else:
                txt = self.app.tr("ping_fail")
                color = t["stopped_red"]

            try:
                self.result_labels[name].config(text=txt, foreground=color)
            except Exception:
                return
        try:
            self.run_btn.config(state=tk.NORMAL)
        except Exception:
            pass
class ListsEditorWindow(tk.Toplevel):

    def __init__(self, parent, app, lists_dir):
        super().__init__(parent)
        self.app = app
        self.lists_dir = lists_dir
        self.title(self.app.tr("lists_title"))
        self.geometry("600x460")
        self.minsize(480, 350)
        self.transient(parent)
        self.grab_set()

        self.files = sorted([f for f in os.listdir(lists_dir) if f.lower().endswith(".txt")])
        self.setup_ui()
        self.apply_theme()
        if self.files:
            self.load_selected_file()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_row = ttk.Frame(main_frame)
        top_row.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(top_row, text=self.app.tr("lists_select")).pack(side=tk.LEFT, padx=(0, 8))
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(top_row, textvariable=self.file_var, state="readonly", values=self.files)
        self.file_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.files:
            self.file_combo.current(0)
        self.file_combo.bind("<<ComboboxSelected>>", lambda e: self.load_selected_file())

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 10), yscrollcommand=scrollbar.set, undo=True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        save_btn = ttk.Button(btn_frame, text=self.app.tr("lists_save"), command=self.save_selected_file)
        save_btn.pack(side=tk.LEFT, ipady=4)

        close_btn = ttk.Button(btn_frame, text=self.app.tr("hosts_close"), command=self.destroy)
        close_btn.pack(side=tk.RIGHT, ipady=4)

    def apply_theme(self):
        t = THEMES[self.app.get_effective_theme()]
        self.configure(bg=t["bg"])
        self.text_area.configure(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"])

    def load_selected_file(self):
        fname = self.file_var.get()
        if not fname:
            return
        fpath = os.path.join(self.lists_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
        except Exception as e:
            messagebox.showerror(self.app.tr("err_title"), str(e))

    def save_selected_file(self):
        fname = self.file_var.get()
        if not fname:
            return
        fpath = os.path.join(self.lists_dir, fname)
        content = self.text_area.get("1.0", tk.END)
        if content.endswith("\n"):
            content = content[:-1]

        try:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            if self.app.check_winws_running():
                self.app.start_strategy()
            messagebox.showinfo(self.app.tr("done_title"), self.app.tr("lists_saved_msg"))
        except Exception as e:
            messagebox.showerror(self.app.tr("err_title"), str(e))
class DnsSettingsWindow(tk.Toplevel):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(self.app.tr("dns_title"))
        self.geometry("450x340")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.adapters = []
        self.setup_ui()
        self.apply_theme()
        self.load_adapters()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.main_frame, text=self.app.tr("dns_step1"), font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.adapter_var = tk.StringVar()
        self.adapter_combo = ttk.Combobox(self.main_frame, textvariable=self.adapter_var, state="readonly")
        self.adapter_combo.pack(fill=tk.X, pady=(4, 12))
        self.adapter_combo.bind("<<ComboboxSelected>>", self.on_adapter_changed)

        ttk.Label(self.main_frame, text=self.app.tr("dns_step2"), font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(self.main_frame, textvariable=self.preset_var, state="readonly", values=list(DNS_PRESETS.keys()))
        self.preset_combo.current(0)
        self.preset_combo.pack(fill=tk.X, pady=(4, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_changed)

        ip_frame = ttk.Frame(self.main_frame)
        ip_frame.pack(fill=tk.X, pady=(0, 12))

        left_ip = ttk.Frame(ip_frame)
        left_ip.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Label(left_ip, text=self.app.tr("dns_primary")).pack(anchor=tk.W)
        self.dns1_var = tk.StringVar(value="94.140.14.14")
        dns1_entry = ttk.Entry(left_ip, textvariable=self.dns1_var)
        dns1_entry.pack(fill=tk.X, pady=(2, 0))
        dns1_entry.bind("<KeyRelease>", self.on_manual_edit)

        right_ip = ttk.Frame(ip_frame)
        right_ip.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Label(right_ip, text=self.app.tr("dns_secondary")).pack(anchor=tk.W)
        self.dns2_var = tk.StringVar(value="94.140.15.15")
        dns2_entry = ttk.Entry(right_ip, textvariable=self.dns2_var)
        dns2_entry.pack(fill=tk.X, pady=(2, 0))
        dns2_entry.bind("<KeyRelease>", self.on_manual_edit)

        self.current_dns_label = ttk.Label(self.main_frame, text=self.app.tr("dns_curr_check"))
        self.current_dns_label.pack(anchor=tk.W, pady=(0, 14))

        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(fill=tk.X)

        apply_btn = ttk.Button(btn_frame, text=self.app.tr("dns_apply"), command=self.apply_dns)
        apply_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=4)

        auto_btn = ttk.Button(btn_frame, text=self.app.tr("dns_reset"), command=self.reset_dns)
        auto_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=4)

    def apply_theme(self):
        t = THEMES[self.app.get_effective_theme()]
        self.configure(bg=t["bg"])
        self.current_dns_label.configure(foreground=t["sub_fg"])

    def load_adapters(self):
        active_adapters = []
        all_adapters = []

        ps_res = run_hidden(["powershell", "-NoProfile", "-Command", "Get-NetAdapter | Select-Object Name, Status | ConvertTo-Json -Compress"])
        try:
            raw = ps_res.stdout.strip()
            if raw:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for item in parsed:
                    name = item.get("Name", "").strip()
                    status = str(item.get("Status", "")).strip()
                    if name:
                        all_adapters.append(name)
                        if status == "Up":
                            active_adapters.append(name)
        except Exception:
            pass

        if not all_adapters:
            res = run_hidden(["netsh", "interface", "show", "interface"])
            for line in res.stdout.splitlines():
                parts = re.split(r"\s{2,}", line.strip())
                if len(parts) >= 4 and parts in ("Enabled", "Disabled", "Разрешен", "Запрещен"):
                    state = parts
                    name = parts
                    all_adapters.append(name)
                    if state in ("Connected", "Подключено"):
                        active_adapters.append(name)

        self.adapters = active_adapters if active_adapters else all_adapters
        if self.adapters:
            self.adapter_combo["values"] = self.adapters
            self.adapter_combo.current(0)
            self.update_current_dns_info()
        else:
            self.adapter_combo["values"] = [self.app.tr("dns_no_adapters")]
            self.adapter_combo.current(0)

    def on_adapter_changed(self, event=None):
        self.update_current_dns_info()

    def on_preset_changed(self, event=None):
        preset_name = self.preset_var.get()
        dns1, dns2 = DNS_PRESETS.get(preset_name, ("", ""))
        if dns1:
            self.dns1_var.set(dns1)
            self.dns2_var.set(dns2)

    def on_manual_edit(self, event=None):
        self.preset_var.set("Custom (Manual)")

    def update_current_dns_info(self):
        adapter = self.adapter_var.get()
        if not adapter or adapter == self.app.tr("dns_no_adapters"):
            return
        res = run_hidden(["netsh", "interface", "ip", "show", "dns", f"name={adapter}"])
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", res.stdout)
        if ips:
            self.current_dns_label.config(text=self.app.tr("dns_curr_val").format(ips=", ".join(ips)))
        else:
            self.current_dns_label.config(text=self.app.tr("dns_curr_auto"))

    def is_valid_ip(self, ip):
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False
        return True

    def apply_dns(self):
        adapter = self.adapter_var.get()
        if not adapter or adapter == self.app.tr("dns_no_adapters"):
            return

        dns1 = self.dns1_var.get().strip()
        dns2 = self.dns2_var.get().strip()

        if not self.is_valid_ip(dns1):
            messagebox.showerror(self.app.tr("err_title"), self.app.tr("dns_err_ip1"))
            return

        if dns2 and not self.is_valid_ip(dns2):
            messagebox.showerror(self.app.tr("err_title"), self.app.tr("dns_err_ip2"))
            return

        run_hidden(["netsh", "interface", "ip", "set", "dns", f"name={adapter}", "static", dns1])
        if dns2:
            run_hidden(["netsh", "interface", "ip", "add", "dns", f"name={adapter}", dns2, "index=2"])
            ps_cmd = f'Set-DnsClientServerAddress -InterfaceAlias "{adapter}" -ServerAddresses ("{dns1}","{dns2}")'
        else:
            ps_cmd = f'Set-DnsClientServerAddress -InterfaceAlias "{adapter}" -ServerAddresses ("{dns1}")'

        run_hidden(["powershell", "-NoProfile", "-Command", ps_cmd])
        run_hidden(["ipconfig", "/flushdns"])
        self.update_current_dns_info()
        messagebox.showinfo(self.app.tr("done_title"), self.app.tr("dns_applied_msg").format(adapter=adapter))

    def reset_dns(self):
        adapter = self.adapter_var.get()
        if not adapter or adapter == self.app.tr("dns_no_adapters"):
            return

        run_hidden(["netsh", "interface", "ip", "set", "dns", f"name={adapter}", "dhcp"])
        ps_cmd = f'Set-DnsClientServerAddress -InterfaceAlias "{adapter}" -ResetServerAddresses'
        run_hidden(["powershell", "-NoProfile", "-Command", ps_cmd])
        run_hidden(["ipconfig", "/flushdns"])
        self.update_current_dns_info()
        messagebox.showinfo(self.app.tr("done_title"), self.app.tr("dns_reset_msg").format(adapter=adapter))
class HostsEditorWindow(tk.Toplevel):

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title(self.app.tr("hosts_title"))
        self.geometry("620x460")
        self.minsize(500, 350)
        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.apply_theme()
        self.load_hosts()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        info_label = ttk.Label(main_frame, text=self.app.tr("hosts_path_info").format(path=HOSTS_PATH), font=("Segoe UI", 9))
        info_label.pack(anchor=tk.W, pady=(0, 8))

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(text_frame, wrap=tk.NONE, font=("Consolas", 10), yscrollcommand=scrollbar.set, undo=True)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        save_btn = ttk.Button(btn_frame, text=self.app.tr("hosts_save"), command=self.save_hosts)
        save_btn.pack(side=tk.LEFT, ipady=4, padx=(0, 8))

        reload_btn = ttk.Button(btn_frame, text=self.app.tr("hosts_reload"), command=self.load_hosts)
        reload_btn.pack(side=tk.LEFT, ipady=4, padx=(0, 8))

        close_btn = ttk.Button(btn_frame, text=self.app.tr("hosts_close"), command=self.destroy)
        close_btn.pack(side=tk.RIGHT, ipady=4)

    def apply_theme(self):
        t = THEMES[self.app.get_effective_theme()]
        self.configure(bg=t["bg"])
        self.text_area.configure(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"])

    def load_hosts(self):
        try:
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
        except Exception as e:
            messagebox.showerror(self.app.tr("err_title"), self.app.tr("hosts_err_read").format(err=e))

    def save_hosts(self):
        content = self.text_area.get("1.0", tk.END)
        if content.endswith("\n"):
            content = content[:-1]

        try:
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.write(content)
            run_hidden(["ipconfig", "/flushdns"])
            messagebox.showinfo(self.app.tr("done_title"), self.app.tr("hosts_saved_msg"))
        except PermissionError:
            messagebox.showerror(self.app.tr("err_title"), self.app.tr("hosts_err_perm"))
        except Exception as e:
            messagebox.showerror(self.app.tr("err_title"), self.app.tr("hosts_err_save").format(err=e))


class ZapretLauncherApp:

    def __init__(self, root):
        self.root = root
        self.root.title(f"Zapret Universal GUI v{APP_VERSION}")
        self.root.geometry("455x575")
        self.root.resizable(False, False)

        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(self.base_dir, "config.json")
        self.config = self.load_config()

        self.lang = self.config.get("lang", "ru")
        self.theme_mode = self.config.get("theme", "system")
        self.win_autostart_var = tk.BooleanVar(value=self.config.get("win_autostart", False))
        self.auto_bypass_var = tk.BooleanVar(value=self.config.get("auto_bypass", False))

        self.active_process = None
        self.is_running = True
        self.auto_searching = False
        self.strategies_list = []
        self.tray_icon = None
        self.last_tray_state = None
        self.latest_github_url = None

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.setup_ui()
        self.apply_theme()
        self.load_strategies()
        self.setup_tray_icon()

        if "--tray" in sys.argv:
            self.root.withdraw()

        if self.auto_bypass_var.get() and self.strategies_list:
            self.root.after(600, self.start_strategy)

        self.status_thread = threading.Thread(target=self.monitor_status, daemon=True)
        self.status_thread.start()

        threading.Thread(target=lambda: self.check_updates(silent=True), daemon=True).start()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        data = {
            "lang": self.lang,
            "theme": self.theme_mode,
            "last_strategy": self.strategy_var.get(),
            "win_autostart": self.win_autostart_var.get(),
            "auto_bypass": self.auto_bypass_var.get(),
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def tr(self, key):
        return LANGS[self.lang].get(key, key)

    def get_effective_theme(self):
        if self.theme_mode == "system":
            return get_system_theme()
        return self.theme_mode
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        self.lang_lbl = ttk.Label(top_bar, text=self.tr("lang_label"))
        self.lang_lbl.pack(side=tk.LEFT, padx=(0, 4))

        self.lang_var = tk.StringVar(value="English" if self.lang == "en" else "Русский")
        self.lang_combo = ttk.Combobox(top_bar, textvariable=self.lang_var, state="readonly", values=["Русский", "English"], width=9)
        self.lang_combo.pack(side=tk.LEFT)
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_lang_selected)

        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(top_bar, textvariable=self.theme_var, state="readonly", width=15)
        self.theme_combo.pack(side=tk.RIGHT)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_selected)

        self.theme_lbl = ttk.Label(top_bar, text=self.tr("theme_label"))
        self.theme_lbl.pack(side=tk.RIGHT, padx=(0, 4))

        self.update_theme_combo_values()

        self.status_frame = ttk.LabelFrame(main_frame, text=self.tr("status_box"), padding="10")
        self.status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_label = ttk.Label(self.status_frame, text=self.tr("status_checking"), font=("Segoe UI", 11, "bold"))
        self.status_label.pack(side=tk.LEFT)

        self.strat_frame = ttk.LabelFrame(main_frame, text=self.tr("strat_box"), padding="10")
        self.strat_frame.pack(fill=tk.X, pady=(0, 10))

        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(self.strat_frame, textvariable=self.strategy_var, state="readonly")
        self.strategy_combo.pack(fill=tk.X)
        self.strategy_combo.bind("<<ComboboxSelected>>", lambda e: self.save_config())

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 6))

        self.start_btn = ttk.Button(btn_frame, text=self.tr("btn_start"), command=self.start_strategy)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)

        self.stop_btn = ttk.Button(btn_frame, text=self.tr("btn_stop"), command=self.stop_zapret)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=5)

        diag_frame = ttk.Frame(main_frame)
        diag_frame.pack(fill=tk.X, pady=(0, 4))

        self.auto_btn = ttk.Button(diag_frame, text=self.tr("btn_auto"), command=self.toggle_auto_search)
        self.auto_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=4)

        self.ping_btn = ttk.Button(diag_frame, text=self.tr("btn_ping"), command=self.open_ping_window)
        self.ping_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=4)

        self.auto_status_lbl = ttk.Label(main_frame, text="", font=("Segoe UI", 9))
        self.auto_status_lbl.pack(anchor=tk.W, pady=(0, 6))

        self.auto_frame = ttk.LabelFrame(main_frame, text=self.tr("autostart_box"), padding="8")
        self.auto_frame.pack(fill=tk.X, pady=(0, 10))

        self.chk_win = ttk.Checkbutton(self.auto_frame, text=self.tr("chk_win_start"), variable=self.win_autostart_var, command=self.on_win_autostart_toggle)
        self.chk_win.pack(anchor=tk.W, pady=(0, 3))

        self.chk_bypass = ttk.Checkbutton(self.auto_frame, text=self.tr("chk_auto_bypass"), variable=self.auto_bypass_var, command=self.save_config)
        self.chk_bypass.pack(anchor=tk.W)

        self.tools_frame = ttk.LabelFrame(main_frame, text=self.tr("tools_box"), padding="10")
        self.tools_frame.pack(fill=tk.X)

        row1 = ttk.Frame(self.tools_frame)
        row1.pack(fill=tk.X, pady=(0, 6))

        self.lists_edit_btn = ttk.Button(row1, text=self.tr("btn_lists_edit"), command=self.open_lists_editor)
        self.lists_edit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.lists_dir_btn = ttk.Button(row1, text=self.tr("btn_lists_dir"), command=self.open_lists_dir)
        self.lists_dir_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        row2 = ttk.Frame(self.tools_frame)
        row2.pack(fill=tk.X, pady=(0, 6))

        self.hosts_btn = ttk.Button(row2, text=self.tr("btn_hosts"), command=self.open_hosts_editor)
        self.hosts_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.dns_btn = ttk.Button(row2, text=self.tr("btn_dns"), command=self.open_dns_settings)
        self.dns_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        row3 = ttk.Frame(self.tools_frame)
        row3.pack(fill=tk.X)

        self.service_btn = ttk.Button(row3, text=self.tr("btn_service"), command=self.open_service)
        self.service_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.update_btn = ttk.Button(row3, text=self.tr("btn_update"), command=lambda: threading.Thread(target=lambda: self.check_updates(silent=False), daemon=True).start())
        self.update_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    def update_theme_combo_values(self):
        options = [self.tr("theme_system"), self.tr("theme_classic"), self.tr("theme_light"), self.tr("theme_dark")]
        self.theme_combo["values"] = options
        mode_map = {"system": 0, "classic": 1, "light": 2, "dark": 3}
        self.theme_combo.current(mode_map.get(self.theme_mode, 0))

    def on_lang_selected(self, event=None):
        self.lang = "en" if self.lang_var.get() == "English" else "ru"
        self.save_config()
        self.update_texts()
        self.rebuild_tray_menu()

    def on_theme_selected(self, event=None):
        idx = self.theme_combo.current()
        modes = ["system", "classic", "light", "dark"]
        self.theme_mode = modes[idx] if 0 <= idx < len(modes) else "system"
        self.save_config()
        self.apply_theme()

    def on_win_autostart_toggle(self):
        set_windows_autostart(self.win_autostart_var.get())
        self.save_config()

    def update_texts(self):
        self.lang_lbl.config(text=self.tr("lang_label"))
        self.theme_lbl.config(text=self.tr("theme_label"))
        self.update_theme_combo_values()
        self.status_frame.config(text=self.tr("status_box"))
        self.strat_frame.config(text=self.tr("strat_box"))
        self.start_btn.config(text=self.tr("btn_start"))
        self.stop_btn.config(text=self.tr("btn_stop"))
        self.auto_btn.config(text=self.tr("btn_auto_stop" if self.auto_searching else "btn_auto"))
        self.ping_btn.config(text=self.tr("btn_ping"))
        self.auto_frame.config(text=self.tr("autostart_box"))
        self.chk_win.config(text=self.tr("chk_win_start"))
        self.chk_bypass.config(text=self.tr("chk_auto_bypass"))
        self.tools_frame.config(text=self.tr("tools_box"))
        self.lists_edit_btn.config(text=self.tr("btn_lists_edit"))
        self.lists_dir_btn.config(text=self.tr("btn_lists_dir"))
        self.hosts_btn.config(text=self.tr("btn_hosts"))
        self.dns_btn.config(text=self.tr("btn_dns"))
        self.service_btn.config(text=self.tr("btn_service"))
        if not self.latest_github_url:
            self.update_btn.config(text=self.tr("btn_update"))
        self.refresh_status_once()

    def apply_theme(self):
        effective = self.get_effective_theme()
        t = THEMES[effective]
        self.root.configure(bg=t["bg"])
        self.style.configure("TFrame", background=t["bg"])
        self.style.configure("TLabel", background=t["bg"], foreground=t["fg"])
        self.style.configure("TCheckbutton", background=t["bg"], foreground=t["fg"])
        self.style.map("TCheckbutton", background=[("active", t["bg"])])
        self.auto_status_lbl.configure(foreground=t["sub_fg"])
        self.style.configure("TLabelframe", background=t["bg"], foreground=t["fg"])
        self.style.configure("TLabelframe.Label", background=t["bg"], foreground=t["fg"])
        self.style.configure("TButton", background=t["btn_bg"], foreground=t["fg"], borderwidth=1)
        self.style.map("TButton", background=[("active", t["btn_active"])])
        self.style.configure("TCombobox", fieldbackground=t["entry_bg"], background=t["btn_bg"], foreground=t["entry_fg"])
        self.style.map("TCombobox", fieldbackground=[("readonly", t["entry_bg"])], foreground=[("readonly", t["entry_fg"])], selectbackground=[("readonly", t["entry_bg"])], selectforeground=[("readonly", t["entry_fg"])])
        self.style.configure("TEntry", fieldbackground=t["entry_bg"], foreground=t["entry_fg"])
        self.refresh_status_once()
    def load_strategies(self):
        strategies = []
        for file in os.listdir(self.base_dir):
            if file.lower().endswith((".bat", ".cmd")) and not file.lower().startswith(("service", "_temp")):
                strategies.append(file)

        strategies.sort()
        self.strategies_list = strategies

        if strategies:
            self.strategy_combo["values"] = strategies
            saved_strat = self.config.get("last_strategy", "")
            if saved_strat in strategies:
                self.strategy_var.set(saved_strat)
            else:
                self.strategy_combo.current(0)
        else:
            self.strategy_combo["values"] = [self.tr("no_scripts")]
            self.strategy_combo.current(0)
            self.start_btn.config(state=tk.DISABLED)
            self.auto_btn.config(state=tk.DISABLED)

    def check_winws_running(self):
        try:
            res = run_hidden(["tasklist"])
            out = res.stdout.lower()
            return "winws.exe" in out or "goodbyedpi.exe" in out
        except Exception:
            return False

    def refresh_status_once(self):
        t = THEMES[self.get_effective_theme()]
        active = self.check_winws_running()
        if active:
            self.status_label.config(text=self.tr("status_active"), foreground=t["active_green"])
        else:
            self.status_label.config(text=self.tr("status_stopped"), foreground=t["stopped_red"])
        if self.tray_icon and self.last_tray_state != active:
            self.last_tray_state = active
            self.tray_icon.icon = create_tray_icon_image(active)

    def monitor_status(self):
        while self.is_running:
            self.refresh_status_once()
            time.sleep(1.5)

    def _launch_bat_hidden(self, bat_path):
        self.stop_zapret(silent=True)
        time.sleep(0.5)

        with open(bat_path, "r", encoding="utf-8", errors="ignore") as f:
            bat_content = f.read()

        hidden_content = re.sub(r"(?i)\bstart\s+(?!/)", "start /B ", bat_content)

        temp_bat = os.path.join(self.base_dir, "_temp_hidden_run.bat")
        with open(temp_bat, "w", encoding="utf-8") as f:
            f.write(hidden_content)

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

        self.active_process = subprocess.Popen(["cmd.exe", "/c", temp_bat], cwd=self.base_dir, startupinfo=startupinfo, creationflags=0x08000000, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def start_strategy(self):
        selected = self.strategy_var.get()
        bat_path = os.path.join(self.base_dir, selected)

        if not os.path.exists(bat_path):
            messagebox.showerror(self.tr("err_title"), self.tr("err_file_not_found").format(file=selected))
            return

        self.save_config()
        try:
            self._launch_bat_hidden(bat_path)
        except Exception as e:
            messagebox.showerror(self.tr("err_start"), str(e))

    def toggle_auto_search(self):
        if self.auto_searching:
            self.auto_searching = False
            self.auto_btn.config(text=self.tr("btn_auto"))
            self.auto_status_lbl.config(text=self.tr("auto_stopped"))
            return

        if not self.strategies_list:
            return

        self.auto_searching = True
        self.auto_btn.config(text=self.tr("btn_auto_stop"))
        self.start_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._auto_search_worker, daemon=True).start()

    def _auto_search_worker(self):
        total = len(self.strategies_list)
        found = None

        for idx, name in enumerate(self.strategies_list, start=1):
            if not self.auto_searching or not self.is_running:
                break

            self.strategy_var.set(name)
            self.auto_status_lbl.config(text=self.tr("auto_testing").format(idx=idx, total=total, name=name))
            bat_path = os.path.join(self.base_dir, name)
            try:
                self._launch_bat_hidden(bat_path)
            except Exception:
                continue

            time.sleep(2.5)
            if not self.auto_searching:
                break

            ok_yt, _ = check_url_ping("https://youtube.com", timeout=3.0)
            ok_dc, _ = check_url_ping("https://discord.com", timeout=3.0)
            if ok_yt or ok_dc:
                found = name
                break

        was_running = self.auto_searching
        self.auto_searching = False
        try:
            self.auto_btn.config(text=self.tr("btn_auto"))
            self.start_btn.config(state=tk.NORMAL)
            if was_running:
                if found:
                    self.save_config()
                    self.auto_status_lbl.config(text=f"✅ {found}")
                    messagebox.showinfo(self.tr("done_title"), self.tr("auto_found").format(name=found))
                else:
                    self.stop_zapret(silent=True)
                    self.auto_status_lbl.config(text=self.tr("auto_not_found"))
                    messagebox.showwarning(self.tr("warn_title"), self.tr("auto_not_found"))
        except Exception:
            pass

    def stop_zapret(self, silent=False):
        self.auto_searching = False
        try:
            run_hidden(["sc", "stop", "zapret"])
            run_hidden(["sc", "stop", "GoodbyeDPI"])
            run_hidden(["taskkill", "/F", "/IM", "winws.exe"])
            run_hidden(["taskkill", "/F", "/IM", "goodbyedpi.exe"])
        except Exception as e:
            if not silent:
                messagebox.showerror(self.tr("err_stop"), str(e))

    def check_updates(self, silent=True):
        if self.latest_github_url and not silent:
            webbrowser.open(self.latest_github_url)
            return

        url = f"https://github.com{GITHUB_REPO}/releases/latest"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ZapretUniversalGUI"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name", "").lstrip("vV")
            html_url = data.get("html_url", f"https://github.com{GITHUB_REPO}/releases")
            if tag and tag != APP_VERSION:
                self.latest_github_url = html_url
                self.update_btn.config(text=self.tr("update_avail").format(ver=tag))
                if not silent:
                    if messagebox.askyesno(self.tr("done_title"), self.tr("update_ask").format(ver=tag)):
                        webbrowser.open(html_url)
            elif not silent:
                messagebox.showinfo(self.tr("done_title"), self.tr("update_latest").format(ver=APP_VERSION))
        except Exception:
            if not silent:
                messagebox.showwarning(self.tr("warn_title"), self.tr("update_err"))

    def open_ping_window(self):
        PingTestWindow(self.root, self)

    def _find_lists_folder(self):
        for folder in ("lists", "files", "ipset"):
            lists_path = os.path.join(self.base_dir, folder)
            if os.path.exists(lists_path):
                return lists_path
        return None

    def open_lists_editor(self):
        lists_path = self._find_lists_folder()
        if lists_path:
            ListsEditorWindow(self.root, self, lists_path)
        else:
            messagebox.showwarning(self.tr("warn_title"), self.tr("warn_no_lists"))

    def open_lists_dir(self):
        lists_path = self._find_lists_folder()
        if lists_path:
            os.startfile(lists_path)
        else:
            messagebox.showwarning(self.tr("warn_title"), self.tr("warn_no_lists"))

    def open_service(self):
        for name in ("service.bat", "service_install_russia_blacklist.cmd"):
            service_path = os.path.join(self.base_dir, name)
            if os.path.exists(service_path):
                subprocess.Popen(["cmd.exe", "/c", "start", "", service_path], cwd=self.base_dir)
                return
        messagebox.showwarning(self.tr("warn_title"), self.tr("warn_no_service"))

    def open_hosts_editor(self):
        HostsEditorWindow(self.root, self)

    def open_dns_settings(self):
        DnsSettingsWindow(self.root, self)

    def setup_tray_icon(self):
        active = self.check_winws_running()
        self.last_tray_state = active
        menu = self._build_tray_menu()
        self.tray_icon = pystray.Icon("ZapretGUI", create_tray_icon_image(active), "Zapret Universal GUI", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def _build_tray_menu(self):
        return pystray.Menu(
            pystray.MenuItem(self.tr("tray_open"), self.show_from_tray, default=True),
            pystray.MenuItem(self.tr("tray_start"), lambda: self.root.after(0, self.start_strategy)),
            pystray.MenuItem(self.tr("tray_stop"), lambda: self.root.after(0, self.stop_zapret)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self.tr("tray_exit"), lambda: self.root.after(0, self.quit_app)),
        )

    def rebuild_tray_menu(self):
        if self.tray_icon:
            self.tray_icon.menu = self._build_tray_menu()

    def hide_to_tray(self):
        self.root.withdraw()

    def show_from_tray(self):
        self.root.after(0, self._restore_window)

    def _restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self):
        self.is_running = False
        self.auto_searching = False
        self.save_config()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()


if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    root = tk.Tk()
    app = ZapretLauncherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.hide_to_tray)
    root.mainloop()
