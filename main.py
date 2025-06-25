import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import json
from urllib.parse import urljoin
import os
import zipfile
import shutil
import sys
import threading
import subprocess

app_ver = "0.3.0-preview.4"



# 実行ファイルの場所を基準にする
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_PATH, "diffcheck")
MODS_DIR = os.path.join(BASE_PATH, "mods")
TMP_DIR = os.path.join(DATA_DIR, "tmp")

# diffcheckフォルダがなければ作成
os.makedirs(DATA_DIR, exist_ok=True)

# version.txt がなければ初期化
version_file_path = os.path.join(DATA_DIR, "version.txt")
if not os.path.exists(version_file_path):
    with open(version_file_path, "w", encoding="utf-8") as f:
        f.write("N/A")

def start_dl_file():
    progressber.grid()
    is_progressber_show = True
    progressber.start()
    thread = threading.Thread(target=DL_file)
    thread.start()

def DL_file():
    global global_ver
    url = url_entry.get()
    file_name = "mods.zip"
    full_url = urljoin(url, file_name)
    try:
        # ダウンロード
        r = requests.get(full_url)
        r.raise_for_status()
        with open(os.path.join(DATA_DIR, "mods.zip"), "wb") as f:
            f.write(r.content)
        

        # 解凍先初期化
        if os.path.exists(TMP_DIR):
            shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR)

        # 解凍
        with zipfile.ZipFile(os.path.join(DATA_DIR, "mods.zip"), "r") as zip_ref:
            zip_ref.extractall(TMP_DIR)

                # mods/ にコピー
        if os.path.exists(MODS_DIR):
            shutil.rmtree(MODS_DIR)
        os.makedirs(MODS_DIR)

        # TMP_DIRの中身を確認
        items = os.listdir(TMP_DIR)
        if len(items) == 1 and os.path.isdir(os.path.join(TMP_DIR, items[0])):
            inner = os.path.join(TMP_DIR, items[0])
            if os.path.basename(inner).lower() == "mods":
                # TMP_DIR/mods の中身を MODS_DIR へコピー
                copy_source = inner
            else:
                copy_source = TMP_DIR
        else:
            copy_source = TMP_DIR

        for item in os.listdir(copy_source):
            src_path = os.path.join(copy_source, item)
            dst_path = os.path.join(MODS_DIR, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        with open(version_file_path, "w", encoding="utf-8") as f:
            f.write(global_ver)
        root.after(0, lambda: messagebox.showinfo("成功", "同期成功"))

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("error", f"同期失敗:\n{e}"))
    finally:
        root.after(0,progressber.stop)
        root.after(0,progressber.grid_remove)

def ver_check():
    global global_ver
    url = url_entry.get()
    file_name = "version.json"
    full_url = urljoin(url, file_name)
    try:
        r = requests.get(full_url)
        r.raise_for_status()
        data = r.json()
        version = data.get("version", "N/A")
        mc_ver = data.get("mc_ver", "N/A")
        forge_ver = data.get("forge_ver", "N/A")
        note = data.get("note", "")

        with open(version_file_path, "r", encoding="utf-8") as f:
            lastest_ver = f.read()

        version_label.config(text=f"modsバージョン:{version}")
        mc_ver_label.config(text=f"minecraftバージョン:{mc_ver}")
        forge_ver_label.config(text=f"forgeバージョン:{forge_ver}")
        note_label.config(text=f"備考:{note}")

        if version == lastest_ver:
            version_condition.config(text="最新です", fg="green")
        else:
            version_condition.config(text="同期が必要です", fg="red")

        global_ver = version

    except Exception as e:
        messagebox.showerror("error", f"バージョン情報取得失敗:\n{e}")

def check_update():
    global lastest_ver
    url = url_entry.get()
    file_name = "version.json"
    full_url = urljoin(url, file_name)
    try:
        r = requests.get(full_url)
        r.raise_for_status()
        result = r.json()
        lastest_ver = result.get("app_ver")
        if lastest_ver != app_ver:
            result = messagebox.askyesno("アップデート",f"新しいアップデートがあります。(version:{lastest_ver})\nアップデートを実行しますか？")
        if result:
            update_app()
    except Exception as e:
        messagebox.showerror("error", f"アップデート情報取得失敗:\n{e}")

def update_app():
    global lastest_ver
    url = url_entry.get()
    file_name = "version.json"
    full_url = urljoin(url, file_name)
    try:
        json_result = requests.get(full_url).json()
        github_url = json_result.get("github_url")
        EXE_DL_PATH = os.path.join(os.getcwd(), f"modsync{lastest_ver}.exe")
        try:
            github_response = requests.get(github_url)
            github_response.raise_for_status()
            with open(EXE_DL_PATH,"wb") as f:
                for chunk in github_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            messagebox.showerror("error", f"更新のダウンロードに失敗しました:\n{e}")
    except Exception as e:
        messagebox.showerror("error", f"情報取得に失敗しました:\n{e}")
    finally:
        updater = f"""@echo off
timeout /t 2 > nul
start "" "modsync{lastest_ver}.exe"
timeout /t 5 > nul
del "modsync{app_ver}.exe"
"""
        with open("update.bat", "w", encoding="utf-8") as f:
            f.write(updater)
            subprocess.Popen(["update.bat"], shell=True)
            root.destroy()




# GUI構築
root = tk.Tk()
root.title(f"modsync | {app_ver}")
root.geometry("400x250")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

entry_text = tk.Label(root, text="同期を押下する前に、必ずバージョンチェックを実行してください。\n特段の事情がない場合は下記のurlを変更しないでください。",justify="left")
entry_text.grid(row=0, column=0, sticky="w", padx=(10, 0), pady=(10, 0))

url_entry = tk.Entry(root)
url_entry.insert(0, "http://haskyblog.net/mc/mods1/")
url_entry.grid(row=1, column=0, columnspan=2, sticky="we", padx=(10, 0), pady=(0, 0))

DL_button = tk.Button(root, text="同期", command=start_dl_file)
DL_button.grid(row=2, column=0, columnspan=2, rowspan=2, sticky="we", padx=(10, 10), pady=(10, 0))

ver_check_button = tk.Button(root, text="バージョンチェック", command=ver_check)
ver_check_button.grid(row=2, column=2, sticky="we", padx=(0, 10), pady=(10, 0))

version_label = tk.Label(root, text="modsバージョン:N/A")
version_condition = tk.Label(root, text="")
mc_ver_label = tk.Label(root,text="minecraftバージョン:N/A")
forge_ver_label = tk.Label(root,text="forgeバージョン:N/A")
note_label = tk.Label(root, text="備考:",wraplength=350,justify="left")

version_label.grid(row=4, column=0,columnspan=3, sticky="w", padx=(10, 0))
version_condition.grid(row=5,column=0,columnspan=3,sticky="w", padx=(10,0))
mc_ver_label.grid(row=6, column=0,columnspan=3, sticky="w", padx=(10, 0))
forge_ver_label.grid(row=7, column=0,columnspan=3, sticky="w", padx=(10, 0))
note_label.grid(row=8, column=0,columnspan=3,rowspan=3, sticky="w", padx=(10, 0))

progressber = ttk.Progressbar(root, orient="horizontal",length=350,mode="indeterminate")
progressber.stop()
progressber.grid(row=11, column=0,columnspan=3)
progressber.grid_remove()



root.after(100,check_update)

root.mainloop()