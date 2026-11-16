import ctypes
import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )


class ZapretLauncherApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Zapret Flowseal GUI")
        self.root.geometry("420x320")
        self.root.resizable(False, False)

        # Определяем рабочую директорию (папка со скриптом)
        if getattr(sys, "frozen", False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.active_process = None
        self.is_running = True

        self.setup_ui()
        self.load_strategies()

        # Запуск фоновой проверки статуса winws.exe
        self.status_thread = threading.Thread(
            target=self.monitor_status, daemon=True
        )
        self.status_thread.start()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Блок статуса
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

        # Блок выбора стратегии
        strat_frame = ttk.LabelFrame(
            main_frame, text="Выбор стратегии (.bat)", padding="10"
        )
        strat_frame.pack(fill=tk.X, pady=(0, 12))

        self.strategy_var = tk.StringVar()
        self.strategy_combo = ttk.Combobox(
            strat_frame, textvariable=self.strategy_var, state="readonly"
        )
        self.strategy_combo.pack(fill=tk.X)

        # Основные кнопки управления
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

        # Дополнительные инструменты
        tools_frame = ttk.LabelFrame(
            main_frame, text="Инструменты и файлы", padding="10"
        )
        tools_frame.pack(fill=tk.X)

        service_btn = ttk.Button(
            tools_frame, text="Открыть service.bat", command=self.open_service
        )
        service_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        lists_btn = ttk.Button(
            tools_frame, text="Папка lists (домены)", command=self.open_lists
        )
        lists_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

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
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq winws.exe"',
                startupinfo=startupinfo,
                text=True,
                encoding="cp866",
                errors="ignore",
            )
            return "winws.exe" in output.lower()
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

        # Сначала останавливаем старые процессы, чтобы не было конфликта WinDivert
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
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            # Останавливаем службу, если она была установлена через service.bat
            subprocess.run(
                ["sc", "stop", "zapret"],
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Принудительно завершаем процесс winws.exe
            subprocess.run(
                ["taskkill", "/F", "/IM", "winws.exe"],
                startupinfo=startupinfo,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
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

    def on_closing(self):
        self.is_running = False
        self.root.destroy()


if __name__ == "__main__":
    # Запрашиваем права администратора (необходимы для драйвера WinDivert)
    if not is_admin():
        run_as_admin()
        sys.exit(0)

    root = tk.Tk()
    app = ZapretLauncherApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
