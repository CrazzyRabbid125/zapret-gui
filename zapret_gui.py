import ctypes
import os
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"

DNS_PRESETS = {
    "AdGuard DNS (Без рекламы)": ("94.140.14.14", "94.140.15.15"),
    "AdGuard DNS (Семейный)": ("94.140.14.15", "94.140.15.16"),
    "Cloudflare (1.1.1.1)": ("1.1.1.1", "1.0.0.1"),
    "Google DNS (8.8.8.8)": ("8.8.8.8", "8.8.4.4"),
    "Яндекс.DNS (Базовый)": ("77.88.8.8", "77.88.8.1"),
    "Свой вариант (вручную)": ("", ""),
}


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )


def run_hidden(cmd_list):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.run(
        cmd_list,
        startupinfo=startupinfo,
        capture_output=True,
        text=True,
        encoding="cp866",
        errors="ignore",
    )


class DnsSettingsWindow(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Настройка DNS-серверов")
        self.geometry("450x340")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.adapters = []
        self.setup_ui()
        self.load_adapters()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text="1. Сетевое подключение (интерфейс):",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)
        self.adapter_var = tk.StringVar()
        self.adapter_combo = ttk.Combobox(
            main_frame, textvariable=self.adapter_var, state="readonly"
        )
        self.adapter_combo.pack(fill=tk.X, pady=(4, 12))
        self.adapter_combo.bind(
            "<<ComboboxSelected>>", self.on_adapter_changed
        )

        ttk.Label(
            main_frame,
            text="2. Выберите готовый DNS или введите свой:",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W)
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            main_frame,
            textvariable=self.preset_var,
            state="readonly",
            values=list(DNS_PRESETS.keys()),
        )
        self.preset_combo.current(0)
        self.preset_combo.pack(fill=tk.X, pady=(4, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_changed)

        ip_frame = ttk.Frame(main_frame)
        ip_frame.pack(fill=tk.X, pady=(0, 12))

        left_ip = ttk.Frame(ip_frame)
        left_ip.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Label(left_ip, text="Предпочитаемый DNS:").pack(anchor=tk.W)
        self.dns1_var = tk.StringVar(value="94.140.14.14")
        ttk.Entry(left_ip, textvariable=self.dns1_var).pack(
            fill=tk.X, pady=(2, 0)
        )

        right_ip = ttk.Frame(ip_frame)
        right_ip.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        ttk.Label(right_ip, text="Альтернативный DNS:").pack(anchor=tk.W)
        self.dns2_var = tk.StringVar(value="94.140.15.15")
        ttk.Entry(right_ip, textvariable=self.dns2_var).pack(
            fill=tk.X, pady=(2, 0)
        )

        self.current_dns_label = ttk.Label(
            main_frame, text="Текущий DNS: проверка...", foreground="#444444"
        )
        self.current_dns_label.pack(anchor=tk.W, pady=(0, 14))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        apply_btn = ttk.Button(
            btn_frame, text="✅ Применить DNS", command=self.apply_dns
        )
        apply_btn.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=4
        )

        auto_btn = ttk.Button(
            btn_frame,
            text="🔄 Сбросить на Авто (DHCP)",
            command=self.reset_dns,
        )
        auto_btn.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=4
        )

    def load_adapters(self):
        res = run_hidden(["netsh", "interface", "show", "interface"])
        lines = res.stdout.splitlines()
        active_adapters = []
        all_adapters = []

        for line in lines:
            parts = re.split(r"\s{2,}", line.strip())
            if len(parts) >= 4 and parts[0] in (
                "Enabled",
                "Disabled",
                "Разрешен",
                "Запрещен",
            ):
                state = parts[1]
                name = parts[3]
                all_adapters.append(name)
                if state in ("Connected", "Подключено"):
                    active_adapters.append(name)

        self.adapters = active_adapters if active_adapters else all_adapters
        if self.adapters:
            self.adapter_combo["values"] = self.adapters
            self.adapter_combo.current(0)
            self.update_current_dns_info()
        else:
            self.adapter_combo["values"] = ["Сетевые адаптеры не найдены"]
            self.adapter_combo.current(0)

    def on_adapter_changed(self, event=None):
        self.update_current_dns_info()

    def on_preset_changed(self, event=None):
        preset_name = self.preset_var.get()
        dns1, dns2 = DNS_PRESETS.get(preset_name, ("", ""))
        if dns1:
            self.dns1_var.set(dns1)
            self.dns2_var.set(dns2)

    def update_current_dns_info(self):
        adapter = self.adapter_var.get()
        if not adapter or adapter == "Сетевые адаптеры не найдены":
            return
        res = run_hidden(
            ["netsh", "interface", "ip", "show", "dns", f'name="{adapter}"']
        )
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", res.stdout)
        if ips:
            self.current_dns_label.config(
                text=f"Текущий DNS адаптера: {', '.join(ips)}"
            )
        else:
            self.current_dns_label.config(
                text="Текущий DNS адаптера: Автоматически (от провайдера)"
            )

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
        dns1 = self.dns1_var.get().strip()
        dns2 = self.dns2_var.get().strip()

        if not self.is_valid_ip(dns1):
            messagebox.showerror(
                "Ошибка", "Введите корректный IP для предпочитаемого DNS."
            )
            return

        if dns2 and not self.is_valid_ip(dns2):
            messagebox.showerror(
                "Ошибка", "Введите корректный IP для альтернативного DNS."
            )
            return

        run_hidden([
            "netsh",
            "interface",
            "ip",
            "set",
            "dns",
            f'name="{adapter}"',
            "static",
            dns1,
        ])
        if dns2:
            run_hidden([
                "netsh",
                "interface",
                "ip",
                "add",
                "dns",
                f'name="{adapter}"',
                dns2,
                "index=2",
            ])

        run_hidden(["ipconfig", "/flushdns"])
        self.update_current_dns_info()
        messagebox.showinfo(
            "Готово", f"DNS успешно применен для подключения «{adapter}»!"
        )

    def reset_dns(self):
        adapter = self.adapter_var.get()
        run_hidden([
            "netsh",
            "interface",
            "ip",
            "set",
            "dns",
            f'name="{adapter}"',
            "dhcp",
        ])
        run_hidden(["ipconfig", "/flushdns"])
        self.update_current_dns_info()
        messagebox.showinfo(
            "Готово",
            f"Для подключения «{adapter}» возвращено автоматическое получение DNS.",
        )


class HostsEditorWindow(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Редактор системного файла hosts")
        self.geometry("620x460")
        self.minsize(500, 350)

        self.transient(parent)
        self.grab_set()

        self.setup_ui()
        self.load_hosts()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="12")
        main_frame.pack(fill=tk.BOTH, expand=True)

        info_label = ttk.Label(
            main_frame,
            text=f"Путь: {HOSTS_PATH} (изменения применяются сразу после сохранения)",
            font=("Segoe UI", 9),
        )
        info_label.pack(anchor=tk.W, pady=(0, 8))

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            undo=True,
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        save_btn = ttk.Button(
            btn_frame,
            text="💾 Сохранить и обновить DNS",
            command=self.save_hosts,
        )
        save_btn.pack(side=tk.LEFT, ipady=4, padx=(0, 8))

        reload_btn = ttk.Button(
            btn_frame, text="🔄 Обновить из файла", command=self.load_hosts
        )
        reload_btn.pack(side=tk.LEFT, ipady=4, padx=(0, 8))

        close_btn = ttk.Button(btn_frame, text="Закрыть", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, ipady=4)
    def load_hosts(self):
        try:
            with open(HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", content)
        except Exception as e:
            messagebox.showerror(
                "Ошибка чтения", f"Не удалось открыть файл hosts:\n{e}"
            )
    def save_hosts(self):
        content = self.text_area.get("1.0", tk.END)
        if content.endswith("\n"):
            content = content[:-1]

        try:
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                f.write(content)

            run_hidden(["ipconfig", "/flushdns"])
            messagebox.showinfo(
                "Готово", "Файл hosts успешно сохранен, а кэш DNS обновлен!"
            )
        except PermissionError:
            messagebox.showerror(
                "Ошибка доступа",
                "Недостаточно прав для записи в hosts. Проверьте, что антивирус не блокирует изменение файла.",
            )
        except Exception as e:
            messagebox.showerror(
                "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}"
            )


class ZapretLauncherApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Zapret Flowseal GUI")
        self.root.geometry("430x405")
        self.root.resizable(False, False)

        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.active_process = None
        self.is_running = True

        self.setup_ui()
        self.load_strategies()

        self.status_thread = threading.Thread(
            target=self.monitor_status, daemon=True
        )
        self.status_thread.start()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        status_frame = ttk.LabelFrame(
            main_frame, text="Состояние обхода", padding="10"
        )
        status_frame.pack(fill=tk.X, pady=(0, 12))

        self.status_label = ttk.Label(
            status_frame,
            text="Проверка статуса...",
            font=("Segoe UI", 11, "bold"),
        )
        self.status_label.pack(side=tk.LEFT)

        strat_frame = ttk.LabelFrame(
            main_frame, text="Выбор стратегии (.bat)", padding="10"
        )
        strat_frame.pack(fill=tk.X, pady=(0, 12))

        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(
            strat_frame, textvariable=self.strategy_var, state="readonly"
        )
        self.strategy_combo.pack(fill=tk.X)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 12))

        self.start_btn = ttk.Button(
            btn_frame, text="▶ Запустить", command=self.start_strategy
        )
        self.start_btn.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5
        )

        self.stop_btn = ttk.Button(
            btn_frame, text="⏹ Остановить", command=self.stop_zapret
        )
        self.stop_btn.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=5
        )

        tools_frame = ttk.LabelFrame(
            main_frame, text="Инструменты, DNS и файлы", padding="10"
        )
        tools_frame.pack(fill=tk.X)

        row1 = ttk.Frame(tools_frame)
        row1.pack(fill=tk.X, pady=(0, 6))

        service_btn = ttk.Button(
            row1, text="Открыть service.bat", command=self.open_service
        )
        service_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        lists_btn = ttk.Button(
            row1, text="Папка lists (домены)", command=self.open_lists
        )
        lists_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        hosts_btn = ttk.Button(
            tools_frame,
            text="📝 Редактор файла hosts (Windows)",
            command=self.open_hosts_editor,
        )
        hosts_btn.pack(fill=tk.X, pady=(0, 6), ipady=3)

        dns_btn = ttk.Button(
            tools_frame,
            text="🌐 Настройка DNS (AdGuard, Cloudflare и др.)",
            command=self.open_dns_settings,
        )
        dns_btn.pack(fill=tk.X, ipady=3)

    def load_strategies(self):
        strategies = []
        for file in os.listdir(self.base_dir):
            if file.lower().startswith("general") and file.lower().endswith(
                ".bat"
            ):
                strategies.append(file)

        strategies.sort()

        if strategies:
            self.strategy_combo["values"] = strategies
            self.strategy_combo.current(0)
        else:
            self.strategy_combo["values"] = ["Файлы general*.bat не найдены"]
            self.strategy_combo.current(0)
            self.start_btn.config(state=tk.DISABLED)

    def check_winws_running(self):
        try:
            res = run_hidden(["tasklist", "/FI", "IMAGENAME eq winws.exe"])
            return "winws.exe" in res.stdout.lower()
        except Exception:
            return False

    def monitor_status(self):
        while self.is_running:
            active = self.check_winws_running()
            if active:
                self.status_label.config(
                    text="● АКТИВЕН (winws.exe работает)", foreground="#1b8a2e"
                )
            else:
                self.status_label.config(
                    text="● ОСТАНОВЛЕН", foreground="#c92a2a"
                )
            time.sleep(1.5)

    def start_strategy(self):
        selected = self.strategy_var.get()
        bat_path = os.path.join(self.base_dir, selected)

        if not os.path.exists(bat_path):
            messagebox.showerror(
                "Ошибка", f"Файл {selected} не найден в папке программы."
            )
            return

        self.stop_zapret(silent=True)
        time.sleep(0.5)

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.active_process = subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                cwd=self.base_dir,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))

    def stop_zapret(self, silent=False):
        try:
            run_hidden(["sc", "stop", "zapret"])
            run_hidden(["taskkill", "/F", "/IM", "winws.exe"])
        except Exception as e:
            if not silent:
                messagebox.showerror("Ошибка остановки", str(e))

    def open_service(self):
        service_path = os.path.join(self.base_dir, "service.bat")
        if os.path.exists(service_path):
            subprocess.Popen(
                ["cmd.exe", "/c", "start", "", service_path], cwd=self.base_dir
            )
        else:
            messagebox.showwarning("Внимание", "Файл service.bat не найден.")

    def open_lists(self):
        lists_path = os.path.join(self.base_dir, "lists")
        if os.path.exists(lists_path):
            os.startfile(lists_path)
        else:
            messagebox.showwarning("Внимание", "Папка lists не найдена.")

    def open_hosts_editor(self):
        HostsEditorWindow(self.root)

    def open_dns_settings(self):
        DnsSettingsWindow(self.root)

    def on_closing(self):
        self.is_running = False
        self.root.destroy()
        
if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    root = tk.Tk()
    app = ZapretLauncherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    def start_strategy(self):
        selected = self.strategy_var.get()
        bat_path = os.path.join(self.base_dir, selected)

        if not os.path.exists(bat_path):
            messagebox.showerror(
                "Ошибка", f"Файл {selected} не найден в папке программы."
            )
            return

        self.stop_zapret(silent=True)
        time.sleep(0.5)

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE — полностью скрыть окно

            # Флаг CREATE_NO_WINDOW (0x08000000) запрещает создание консольного окна для дочерних процессов
            self.active_process = subprocess.Popen(
                ["cmd.exe", "/c", bat_path],
                cwd=self.base_dir,
                startupinfo=startupinfo,
                creationflags=0x08000000,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))


