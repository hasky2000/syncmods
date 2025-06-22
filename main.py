import tkinter as tk
from tkinter import messagebox
import requests

def DL_file():
    url = url_entry.get()
    try:
        r = requests.get(url)
        with open("mods.zip","wb") as f:
            f.write(r.content)
        messagebox.showinfo("success","Download success.")
    except Exception as e:
        messagebox.showinfo("error",f"Download failure:\n{e}")


root = tk.Tk()
root.title("")
root.geometry("400x600")


root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

entry_text = tk.Label(root,text="特段の事情がない場合は変更しないでください。")
entry_text.grid(row=0,column=0,sticky="w",padx=(10,0),pady=(10,0))
url_entry = tk.Entry(root)
url_entry.insert(0,"http://haskyblog.net/mc/mods1/mods.zip")
url_entry.grid(row=1,column=0,columnspan=2,sticky="we",padx=(10,0),pady=(0,0))

DL_button = tk.Button(root,text="Download",command=DL_file)
DL_button.grid(row=2,column=0,columnspan=2,rowspan=2,sticky="we",padx=(10,0),pady=(10,0))

root.mainloop()