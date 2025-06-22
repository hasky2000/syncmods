import tkinter as tk
from tkinter import messagebox
import requests
import json
from urllib.parse import urljoin
import os
import zipfile
import shutil

os.makedirs("diffcheck", exist_ok=True)

file_path = "diffcheck/version.txt"
if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("N/A")

def DL_file():
    global global_ver
    url = url_entry.get()
    file_name = "mods.zip"
    url = urljoin(url,file_name)
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open("./diffcheck/mods.zip","wb") as f:
            f.write(r.content)
        messagebox.showinfo("成功","同期成功")
        if os.path.exists("./diffcheck/tmp/"):
            shutil.rmtree("./diffcheck/tmp/")
        os.makedirs("./diffcheck/tmp/")
        
        with zipfile.ZipFile("./diffcheck/mods.zip", "r") as zip_ref:
            zip_ref.extractall("./diffcheck/tmp/")
        
        if os.path.exists("./mods"):
            shutil.rmtree("./mods")
        os.makedirs("./mods")
        
        for item in os.listdir("./diffcheck/tmp/"):
            src_path = os.path.join("./diffcheck/tmp/",item)
            dst_path = os.path.join("./mods",item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        
        with open("./diffcheck/version.txt","w",encoding="utf-8") as f:
            f.write(global_ver)
    except Exception as e:
        messagebox.showerror("error",f"同期失敗:\n{e}")

def ver_check():
    global global_ver
    url = url_entry.get()
    file_name = "version.json"
    url = urljoin(url,file_name)
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        version = data.get("version","N/A")
        note = data.get("note","")
        
        with open("./diffcheck/version.txt","r",encoding="utf-8") as f:
            lastest_ver = f.read()
            
        version_label.config(text=f"バージョン:{version}")
        note_label.config(text=f"備考:{note}")
        
        if version == lastest_ver:
            version_condition.config(text="最新です",fg="green")
        else:
            version_condition.config(text="同期が必要です",fg="red")
        
        global_ver = version
        
        
    except Exception as e:
        messagebox.showerror("error",f"バージョン情報取得失敗:\n{e}")
        return None

root = tk.Tk()
root.title("")
root.geometry("400x600")


root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

entry_text = tk.Label(root,text="特段の事情がない場合は変更しないでください。")
entry_text.grid(row=0,column=0,sticky="w",padx=(10,0),pady=(10,0))
url_entry = tk.Entry(root)
url_entry.insert(0,"http://haskyblog.net/mc/mods1/")
url_entry.grid(row=1,column=0,columnspan=2,sticky="we",padx=(10,0),pady=(0,0))

DL_button = tk.Button(root,text="同期",command=DL_file)
DL_button.grid(row=2,column=0,columnspan=2,rowspan=2,sticky="we",padx=(10,0),pady=(10,0))
ver_check_button = tk.Button(root,text="バージョンチェック",command=ver_check)
ver_check_button.grid(row=2,column=3,sticky="we",padx=(0,10),pady=(10,0))

version_label = tk.Label(root,text="バージョン:N/A")
version_condition = tk.Label(root,text="")
note_label = tk.Label(root,text="備考:")
version_label.grid(row=4,column=0,sticky="w",padx=(10,0))
version_condition.grid(row=5,column=0,sticky="w",padx=(10,0))
note_label.grid(row=6,column=0,sticky="w",padx=(10,0))

root.mainloop()