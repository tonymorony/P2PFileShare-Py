import tkinter as tk
from tkinter import ttk
import ttkthemes as tkT
from lib import sharelib
from PIL import ImageTk
import time
import datetime



ac_name = sharelib.connnection_popup()

chain_proxy = sharelib.def_credentials(ac_name)
file_uploading_proxy = sharelib.def_credentials(ac_name, mode="fileuploading")

root = tkT.ThemedTk()
frame = ttk.Frame(root)
root.title("DEXP2P fileshare GUI")
root.geometry("1200x720")
root.resizable(False, False)
style = ttk.Style()

root.set_theme('equilux', themebg=True)
style.map("TButton", foreground=[("active", "darkslategray4")], background=[('pressed', 'darkslategray4')])
style.configure("TButton", foreground="grey60", background="grey25")

file_path_var = tk.StringVar()

previous_uploading_progress = tk.StringVar()
previous_uploading_progress.set(0.0)

file_select_button = ttk.Button(frame, text="Choose file to upload",
                               command=lambda: sharelib.select_file(file_path_var, selected_file_label))

file_upload_button = ttk.Button(frame, text="Upload selected file",
                               command=lambda: sharelib.upload_file(file_path_var, file_uploading_proxy,
                                                                    previous_uploading_progress))
force_list_refresh_button = ttk.Button(frame, text="Refresh now",
                                      command=lambda: update_files_list(files_list, last_updated_label))

download_selected_file_button = ttk.Button(frame, text="Download selected file",
                                          command=lambda: sharelib.download_file(files_list.item(files_list.focus()),
                                                                                 chain_proxy))

selected_file_label = ttk.Label(frame, text="Please select file to upload")

uploading_progress_label = ttk.Label(text="")

last_updated_label = ttk.Label(frame)

file_list_columns = ["Timestamp", "File name", "Publisher pubkey", "File size"]
files_list = ttk.Treeview(frame, columns=file_list_columns, selectmode="browse")
files_list.heading('#0', text='File ID')
for i in range(1, len(file_list_columns) + 1):
    files_list.heading("#" + str(i), text=file_list_columns[i - 1])

root.columnconfigure(0, weight=1)
frame.grid(row=0, column=0)
img = ImageTk.PhotoImage(file="kmd_logo_50.png")
img_label = ttk.Label(frame, image=img)
img_label.grid(row=0, column=1, pady=(25,25))
file_select_button.grid(row=2, column=0, sticky="nw", padx=(10,10), pady=(10,10))
selected_file_label.grid(row=2, column=1)
file_upload_button.grid(row=2, column=2, sticky="ne", padx=(10,10), pady=(10,10))

uploading_progress_label = ttk.Label(frame, text="")
uploading_progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate")
uploading_progress_bar.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=(10,10), pady=(10,10))
uploading_progress_label.grid(row=5, column=1, pady=(5,5))
force_list_refresh_button.grid(row=6, column=0, columnspan=3, sticky="nsew", padx=(10,10), pady=(5,5))
last_updated_label.grid(row=7, column=0, columnspan=3, padx=(10,10))

files_list.grid(row=8, column=0, columnspan=3, padx=(10,10), pady=(10,10))
download_selected_file_button.grid(row=9, column=0, columnspan=3, sticky="nsew", padx=(10,10), pady=(5,5))


def update_progress_bar(progress_label):
    # separated rpc proxy because first one awaiting response from uploading command
    rpc_proxy = sharelib.def_credentials(ac_name)
    dex_stats = rpc_proxy.DEX_stats()
    # print(dex_stats)
    if "progress" in dex_stats.keys():
        uploading_progress = float(dex_stats["progress"])
        progress_label["text"] = str(round(uploading_progress,2)) + " %"
        uploading_delta = uploading_progress - float(previous_uploading_progress.get())
        print(uploading_progress)
        uploading_progress_bar.step(uploading_delta)
        previous_uploading_progress.set(uploading_progress)
    else:
        pass
        # print("no uploading at the moment")
    # .after is something like a tkinter "threads"
    root.after(100, lambda: update_progress_bar(progress_label))


def update_files_list(files_table, update_status_label):
    print("updating files list")
    files_table.delete(*files_table.get_children())
    rpc_proxy = sharelib.def_credentials(ac_name, mode="test")
    files_list_response = rpc_proxy.DEX_list("0", "0", "files")["matches"]
    print(files_list_response)
    for file in files_list_response:
        file_size = sharelib.convert_size(float(file["amountA"]) * (10**8))
        readable_date = datetime.datetime.fromtimestamp(file["timestamp"]).isoformat()
        files_table.insert("", "end", text=file["id"], values=[readable_date, file["tagB"],
                                                               file["senderpub"], file_size])
    update_status_label['text'] = "Last update: " + time.ctime() + " (auto-update each 30s)"
    root.after(30000, lambda: update_files_list(files_table, update_status_label))


update_progress_bar(uploading_progress_label)
update_files_list(files_list, last_updated_label)

root.mainloop()
