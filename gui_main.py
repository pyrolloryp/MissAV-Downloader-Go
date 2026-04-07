from datetime import date
import customtkinter as ctk
from tkinter import filedialog, END, Menu
import tkinter
import threading
import queue
import sys
import os
import re
from urllib.parse import urlparse, unquote

import hls_downloader
import actress_crawler

APP_VERSION = "1.0.0"
COMPILE_DATE = "20260407"  # 編譯日期
MAX_DOWNLOAD_WORKERS = 1
MAX_CONVERT_WORKERS = 1
HLS_SEGMENT_WORKERS = 32


class TextboxRedirector:
    def __init__(self, queue):
        self.queue = queue

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"MissAV Downloader v{APP_VERSION} ({COMPILE_DATE})")
        self.geometry("800x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.hls_downloader = hls_downloader
        self.actress_crawler = actress_crawler
        self.log_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.progress_widgets = {}
        self.create_widgets()
        self.process_log_queue()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.log_queue.put("\n>>> 偵測到關閉視窗指令...\n")
        self.stop_event.set()
        self.pause_event.set()
        self.destroy()

    def _generate_paths_from_url(self, url):
        try:
            path = urlparse(url).path
            name_encoded = os.path.basename(path)
            name_decoded = unquote(name_encoded)
            safe_name = re.sub(r'[\\/*?:"<>|]', "", name_decoded)
            clean_folder_name = (
                safe_name.replace("-chinese-subtitle", "")
                .replace("-uncensored-leak", "")
                .strip()
            )
            return f"{safe_name}.txt", clean_folder_name
        except Exception:
            return "crawled_urls.txt", "default_folder"

    def _create_and_warmup_scraper(self, base_url):
        try:
            print("[*] 正在建立新的 Scraper 實例...")
            scraper = self.hls_downloader.cloudscraper.create_scraper()
            print(f"[*] 正在對 {base_url} 進行連線預熱...")
            scraper.get(base_url, timeout=30).raise_for_status()
            print(" -> 連線預熱成功。")
            return scraper
        except Exception as e:
            print(f"[!] Scraper 建立或預熱失敗: {e}")
            return None

    def create_widgets(self):
        url_frame = ctk.CTkFrame(self)
        url_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        url_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(url_frame, text="目標網址:").grid(
            row=0, column=0, padx=10, pady=10
        )
        self.url_entry = ctk.CTkEntry(
            url_frame, placeholder_text="請貼上單一影片或演員/系列頁面網址..."
        )
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkButton(
            url_frame, text="貼上", width=80, command=self.paste_from_clipboard
        ).grid(row=0, column=2, padx=(0, 10), pady=10)
        self._create_url_entry_context_menu()
        path_frame = ctk.CTkFrame(self)
        path_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        path_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(path_frame, text="URL 列表檔:").grid(
            row=0, column=0, padx=10, pady=10
        )
        self.batch_file_entry = ctk.CTkEntry(path_frame)
        self.batch_file_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.batch_file_entry.insert(0, "urls.txt")
        ctk.CTkButton(
            path_frame, text="瀏覽...", width=80, command=self.browse_batch_file
        ).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkLabel(path_frame, text="儲存資料夾:").grid(
            row=1, column=0, padx=10, pady=10
        )
        self.output_dir_entry = ctk.CTkEntry(path_frame)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.output_dir_entry.insert(0, "downloads")
        ctk.CTkButton(
            path_frame, text="瀏覽...", width=80, command=self.browse_output_dir
        ).grid(row=1, column=2, padx=10, pady=10)
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=2, column=0, padx=10, pady=5)
        self.crawl_button = ctk.CTkButton(
            action_frame,
            text="爬取此演員/系列頁面的所有影片",
            command=self.start_crawl_task,
        )
        # self.crawl_button.grid(row=0, column=0, padx=10, pady=10)
        self.download_button = ctk.CTkButton(
            action_frame,
            text="開始批量下載",
            command=self.start_batch_download_task,
        )
        self.download_button.grid(row=0, column=0, padx=10, pady=10)
        self.pause_button = ctk.CTkButton(
            action_frame,
            text="暫停",
            width=110,
            command=self.toggle_pause,
            state="disabled",
        )
        self.pause_button.grid(row=0, column=2, padx=(10, 5), pady=10)
        self.stop_button = ctk.CTkButton(
            action_frame,
            text="停止當前任務",
            width=110,
            command=self.request_stop,
            state="disabled",
            fg_color="red",
            hover_color="#C00000",
        )
        self.stop_button.grid(row=0, column=3, padx=(5, 10), pady=10)

        self.log_switch_var = ctk.StringVar(value="off")
        self.log_switch = ctk.CTkSwitch(
            action_frame,
            text="顯示日誌",
            command=self.toggle_log_window,
            variable=self.log_switch_var,
            onvalue="on",
            offvalue="off",
        )
        self.log_switch.grid(row=0, column=4, padx=(10, 10), pady=10)

        progress_area_frame = ctk.CTkFrame(self)
        progress_area_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        progress_area_frame.grid_columnconfigure(0, weight=1)
        progress_area_frame.grid_rowconfigure(1, weight=1)
        self.main_progress_container = ctk.CTkFrame(
            progress_area_frame, fg_color="transparent"
        )
        self.main_progress_container.grid(
            row=0, column=0, padx=10, pady=(10, 5), sticky="ew"
        )
        self.main_progress_container.grid_columnconfigure(0, weight=1)
        self.main_progressbar = ctk.CTkProgressBar(self.main_progress_container)
        self.main_progressbar.grid(row=0, column=0, sticky="ew")
        self.main_progress_label = ctk.CTkLabel(
            self.main_progress_container, text="0/0"
        )
        self.main_progress_label.grid(row=0, column=0)
        self.main_progress_container.grid_remove()
        self.individual_progress_frame = ctk.CTkScrollableFrame(
            progress_area_frame, label_text="下載進度"
        )
        self.individual_progress_frame.grid(
            row=1, column=0, padx=10, pady=5, sticky="nsew"
        )
        self.individual_progress_frame.grid_columnconfigure(0, weight=1)
        self.individual_progress_frame.grid_remove()

        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        self.log_textbox = ctk.CTkTextbox(self.log_frame, state="disabled")
        self.log_textbox.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    def toggle_log_window(self):
        if self.log_switch_var.get() == "on":
            self.log_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")
            self.grid_rowconfigure(4, weight=1)
        else:
            self.log_frame.grid_remove()
            self.grid_rowconfigure(4, weight=0)

    def set_ui_state(self, is_running):
        state = "disabled" if is_running else "normal"
        stop_state = "normal" if is_running else "disabled"
        self.crawl_button.configure(state=state)
        self.download_button.configure(state=state)
        self.pause_button.configure(state=stop_state)
        self.stop_button.configure(state=stop_state)
        self.url_entry.configure(state=state)
        self.batch_file_entry.configure(state=state)
        self.output_dir_entry.configure(state=state)
        if not is_running:
            self.pause_button.configure(text="暫停")
            self.pause_event.set()
            self.stop_button.configure(text="停止當前任務")
            self.main_progress_container.grid_remove()
            self.individual_progress_frame.grid_remove()
            for task_id in list(self.progress_widgets.keys()):
                self.remove_progress_bar(task_id)

    def add_progress_bar(self, task_id, title):
        if task_id in self.progress_widgets:
            return
        row_frame = ctk.CTkFrame(self.individual_progress_frame)
        row_frame.grid(sticky="ew", padx=5, pady=2)
        row_frame.grid_columnconfigure(0, weight=1)
        title_label = ctk.CTkLabel(
            row_frame, text=f"{title[:45]}..." if len(title) > 45 else title, anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", padx=5)
        progress_bar = ctk.CTkProgressBar(row_frame)
        progress_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        progress_bar.set(0)
        percentage_label = ctk.CTkLabel(
            row_frame, text="0.00%", font=ctk.CTkFont(size=12)
        )
        percentage_label.grid(row=1, column=0)
        self.progress_widgets[task_id] = {
            "frame": row_frame,
            "bar": progress_bar,
            "percentage": percentage_label,
        }

    def update_download_progress(self, task_id, progress, eta=None):
        if task_id in self.progress_widgets:
            widgets = self.progress_widgets[task_id]
            widgets["bar"].set(progress)
            percentage_text = f"{progress * 100:.2f}%"
            if eta:
                percentage_text += f" ({eta})"
            widgets["percentage"].configure(text=percentage_text)

    def remove_progress_bar(self, task_id):
        if task_id in self.progress_widgets:
            widgets = self.progress_widgets.pop(task_id)
            widgets["frame"].destroy()

    def process_log_queue(self):
        try:
            while not self.log_queue.empty():
                message = self.log_queue.get_nowait()
                if isinstance(message, tuple):
                    command = message[0]
                    if command == "ADD_PROGRESS_BAR":
                        self.add_progress_bar(task_id=message[1], title=message[2])
                    elif command == "UPDATE_DOWNLOAD_PROGRESS":
                        # 嘗試解包 4 個參數 (包含 ETA)，如果舊版只有 3 個也能相容
                        if len(message) >= 4:
                            _, task_id, progress, eta = message[:4]
                            self.update_download_progress(task_id, progress, eta)
                        elif len(message) >= 3:
                            _, task_id, progress = message[:3]
                            self.update_download_progress(task_id, progress)
                    elif command == "CRAWL_SUCCESS":
                        self.last_crawl_count = message[1]
                    elif command == "REMOVE_PROGRESS_BAR":
                        self.remove_progress_bar(task_id=message[1])
                    elif command == "UPDATE_MAIN_PROGRESS":
                        current, total = message[1], message[2]
                        progress = current / total if total > 0 else 0
                        self.main_progressbar.set(progress)
                        self.main_progress_label.configure(text=f"{current}/{total}")
                    elif command in ("TASK_COMPLETE", "TASK_STOPPED", "TASK_FAILED"):
                        self.set_ui_state(False)
                        task_type = message[1]
                        if task_type == "CRAWL" and command == "TASK_COMPLETE":
                            if hasattr(self, "last_crawl_count"):
                                self.main_progress_container.grid()  # 強制再次顯示
                                # 更新標籤文字，顯示總數
                                self.main_progress_label.configure(
                                    text=f"已找到 {self.last_crawl_count} 個影片 (準備下載)"
                                )
                                self.main_progressbar.set(0)  # 進度條歸零
                                # 清除暫存變數
                                del self.last_crawl_count
                        if command == "TASK_STOPPED":
                            self.log_queue.put("\n--- 任務已被手動停止 ---\n")
                        elif command == "TASK_FAILED":
                            self.log_queue.put("\n--- 任務因錯誤而終止 ---\n")
                        if task_type == "DOWNLOAD":
                            self.log_queue.put("-> 下載任務結束，還原介面。\n")
                    elif command == "SET_PATHS":
                        txt_path, folder_path = message[1], message[2]
                        self.batch_file_entry.configure(state="normal")
                        self.output_dir_entry.configure(state="normal")
                        self.batch_file_entry.delete(0, END)
                        self.batch_file_entry.insert(0, txt_path)
                        self.output_dir_entry.delete(0, END)
                        self.output_dir_entry.insert(0, folder_path)
                        self.log_queue.put(f"-> 已自動設定列表檔: {txt_path}\n")
                        self.log_queue.put(f"-> 已自動設定儲存資料夾: {folder_path}\n")
                else:
                    self.log_textbox.configure(state="normal")
                    self.log_textbox.insert(END, str(message))
                    self.log_textbox.see(END)
                    self.log_textbox.configure(state="disabled")
        finally:
            self.after(100, self.process_log_queue)

    def start_task(self, task_function, *args):
        self.main_progress_container.grid()
        self.individual_progress_frame.grid()
        self.stop_event.clear()
        self.pause_event.set()
        self.set_ui_state(True)
        self.main_progressbar.set(0)
        self.main_progress_label.configure(text="0/0")
        threading.Thread(target=task_function, args=args, daemon=True).start()

    def paste_from_clipboard(self):
        try:
            clipboard_content = self.clipboard_get()
            self.url_entry.delete(0, END)
            self.url_entry.insert(0, clipboard_content)
            if clipboard_content:
                self.log_queue.put(
                    f"-> 偵測到貼上動作，自動開始分析: {clipboard_content}\n"
                )
                # 延遲一點點執行，確保介面已更新
                self.after(200, self.start_crawl_task)
        except tkinter.TclError:
            self.log_queue.put("-> 剪貼簿中沒有文字內容可供貼上。\n")

    def _create_url_entry_context_menu(self):
        self.url_context_menu = Menu(self.url_entry, tearoff=0)
        self.url_context_menu.add_command(
            label="貼上", command=self.paste_from_clipboard
        )
        self.url_entry.bind("<Button-3>", self._show_url_entry_context_menu)

    def _show_url_entry_context_menu(self, event):
        self.url_context_menu.tk_popup(event.x_root, event.y_root)

    def browse_batch_file(self):
        filepath = filedialog.askopenfilename(
            title="選擇 URL 列表檔",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if filepath:
            self.batch_file_entry.delete(0, END)
            self.batch_file_entry.insert(0, filepath)
            dir_path, filename = os.path.split(filepath)
            folder_name, _ = os.path.splitext(filename)
            output_dir = os.path.join(dir_path, folder_name)
            self.output_dir_entry.delete(0, END)
            self.output_dir_entry.insert(0, output_dir)
            self.log_queue.put(f"-> 已自動設定儲存資料夾: {output_dir}\n")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    # 計算非空行且非註解(#)的行數
                    count = sum(
                        1
                        for line in f
                        if line.strip() and not line.strip().startswith("#")
                    )

                # 強制顯示進度條區域，並更新文字
                self.main_progress_container.grid()
                self.main_progress_label.configure(
                    text=f"已載入列表：共 {count} 個影片 (準備下載)"
                )
                self.main_progressbar.set(0)

            except Exception as e:
                self.log_queue.put(f"-> 讀取列表檔數量失敗: {e}\n")

    def browse_output_dir(self):
        dirpath = filedialog.askdirectory(title="選擇影片儲存資料夾")
        if dirpath:
            self.output_dir_entry.delete(0, END)
            self.output_dir_entry.insert(0, dirpath)

    def toggle_pause(self):
        if self.pause_event.is_set():
            self.pause_event.clear()
            self.pause_button.configure(text="繼續")
            self.log_queue.put("-> 任務已暫停...\n")
        else:
            self.pause_event.set()
            self.pause_button.configure(text="暫停")
            self.log_queue.put("-> 任務已繼續。\n")

    def request_stop(self):
        self.log_queue.put(" -> 收到停止訊號，將完成當前處理中的項目後停止...\n")
        self.stop_event.set()
        self.pause_event.set()
        self.stop_button.configure(state="disabled", text="停止中...")

    def start_crawl_task(self):
        url = self.url_entry.get()
        if not url:
            self.log_queue.put("錯誤：目標網址不能為空！\n")
            return
        self.start_task(self.crawl_task, url)

    def crawl_task(self, url):
        original_stdout = sys.stdout
        sys.stdout = TextboxRedirector(self.log_queue)
        task_result = "TASK_COMPLETE"
        try:
            links = self.actress_crawler.find_all_video_urls(url, self.stop_event)
            if not self.stop_event.is_set() and links:
                final_links = self.actress_crawler.filter_and_prioritize_urls(links)
                txt_filename, folder_name = self._generate_paths_from_url(url)
                absolute_txt_filepath = os.path.abspath(txt_filename)
                base_output_dir = "downloads"
                new_output_dir = os.path.join(base_output_dir, folder_name)
                self.log_queue.put(("SET_PATHS", absolute_txt_filepath, new_output_dir))
                with open(txt_filename, "w", encoding="utf-8") as f:
                    for link in reversed(final_links):
                        f.write(link + "\n")
                print(f">>> 所有連結已成功儲存至 {absolute_txt_filepath}！")
                self.log_queue.put(("CRAWL_SUCCESS", len(final_links)))
            if self.stop_event.is_set():
                task_result = "TASK_STOPPED"
        except Exception as e:
            print(f"爬取過程中發生錯誤: {e}")
            task_result = "TASK_FAILED"
        finally:
            sys.stdout = original_stdout
            self.log_queue.put((task_result, "CRAWL"))

    def start_batch_download_task(self):
        url_file = self.batch_file_entry.get()
        output_dir = self.output_dir_entry.get()
        if not os.path.exists(url_file):
            self.log_queue.put(f"錯誤：找不到 URL 列表檔 '{url_file}'\n")
            return
        self.start_task(self.batch_download_task, url_file, output_dir)

    def batch_download_task(self, url_file, output_dir):
        original_stdout = sys.stdout
        sys.stdout = TextboxRedirector(self.log_queue)
        download_queue = queue.Queue()
        conversion_queue = queue.Queue()
        urls = []
        try:
            with open(url_file, "r", encoding="utf-8") as f:
                urls = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.strip().startswith("#")
                ]
                if not urls:
                    self.log_queue.put(("TASK_COMPLETE", "DOWNLOAD"))
                    return
                for url in urls:
                    download_queue.put(url)
            base_url = f"{urlparse(urls[0]).scheme}://{urlparse(urls[0]).netloc}/"
        except (FileNotFoundError, IndexError):
            self.log_queue.put(("TASK_FAILED", "DOWNLOAD"))
            return

        successful_urls = set()
        processed_count = 0
        total_tasks = len(urls)

        self.log_queue.put(("UPDATE_MAIN_PROGRESS", 0, total_tasks))
        os.makedirs(output_dir, exist_ok=True)
        self.hls_downloader._clear_temp_directory()
        scraper = self._create_and_warmup_scraper(base_url)
        if not scraper:
            self.log_queue.put(("TASK_FAILED", "DOWNLOAD"))
            return

        def downloader_worker():
            while not download_queue.empty():
                if self.stop_event.is_set():
                    break
                try:
                    page_url = download_queue.get_nowait()
                    ts_path, title = self.hls_downloader.download_and_merge_to_ts(
                        page_url,
                        output_dir,
                        HLS_SEGMENT_WORKERS,
                        self.stop_event,
                        self.pause_event,
                        self.log_queue,
                    )
                    conversion_queue.put((ts_path, page_url, title))
                    download_queue.task_done()
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"下載執行緒發生錯誤: {e}")
                    if "page_url" in locals():
                        conversion_queue.put((None, page_url, "下載失敗"))
                    download_queue.task_done()

        def converter_worker():
            nonlocal processed_count
            while True:
                try:
                    item = conversion_queue.get(timeout=1)
                    ts_path, task_id, title = item

                    is_successful = False
                    if ts_path == "ALREADY_EXISTS":
                        is_successful = True
                    elif ts_path:
                        if self.hls_downloader._convert_ts_to_mp4(ts_path):
                            is_successful = True

                    if is_successful:
                        successful_urls.add(task_id)

                    processed_count += 1
                    self.log_queue.put(
                        ("UPDATE_MAIN_PROGRESS", processed_count, total_tasks)
                    )

                    if ts_path is not None:
                        self.log_queue.put(("REMOVE_PROGRESS_BAR", task_id))

                    conversion_queue.task_done()
                except queue.Empty:
                    if all(not t.is_alive() for t in download_threads):
                        break
                except Exception as e:
                    print(f"轉檔執行緒發生錯誤: {e}")
                    if "item" in locals():
                        conversion_queue.task_done()

        download_threads = [
            threading.Thread(target=downloader_worker, daemon=True)
            for _ in range(MAX_DOWNLOAD_WORKERS)
        ]
        convert_threads = [
            threading.Thread(target=converter_worker, daemon=True)
            for _ in range(MAX_CONVERT_WORKERS)
        ]
        for t in download_threads:
            t.start()
        for t in convert_threads:
            t.start()

        for t in download_threads:
            t.join()
        for t in convert_threads:
            t.join()

        if scraper:
            scraper.close()
        sys.stdout = original_stdout

        urls_to_keep = [url for url in urls if url not in successful_urls]
        final_task_state = "TASK_COMPLETE"

        if self.stop_event.is_set():
            final_task_state = "TASK_STOPPED"
            print(f"\n--- 已將 {len(urls_to_keep)} 個未完成的 URL 更新回列表檔 ---")
        elif not urls_to_keep:
            print("\n--- 所有批量任務已成功完成！ ---")
            print("--- 已清空 URL 列表檔 ---")
        else:
            final_task_state = "TASK_FAILED"
            print(f"\n--- {len(urls_to_keep)} 個任務未成功。 ---")
            print("--- 已將未完成的 URL 更新回列表檔 ---")

        try:
            if urls_to_keep:
                with open(url_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(urls_to_keep) + "\n")
            else:
                os.remove(url_file)
        except Exception as e:
            print(f"錯誤：無法寫入 URL 列表檔 {url_file}: {e}")

        self.log_queue.put((final_task_state, "DOWNLOAD"))


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
