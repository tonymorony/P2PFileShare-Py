import tkinter as tk
from tkinter import ttk
from lib import sharelib
import threading

ac_name = "FILET1"

chain_proxy = sharelib.def_credentials(ac_name)
file_uploading_proxy = sharelib.def_credentials(ac_name, "uploading")


def update_progress_bar():

    # need separate rpc proxy because first one awaiting response from uploading command
    rpc_proxy = sharelib.def_credentials(ac_name)
    dex_stats = rpc_proxy.DEX_stats()
    # print(dex_stats)
    if "progress" in dex_stats.keys():
        uploading_progress = float(dex_stats["progress"])
        uploading_delta = uploading_progress - float(previous_uploading_progress.get())
        print(uploading_progress)
        uploading_progress_bar.step(uploading_delta)
        previous_uploading_progress.set(uploading_progress)
    else:
        pass
        # print("no uploading at the moment")

    root.after(100, update_progress_bar)


root = tk.Tk()
root.title("DEXP2P fileshare GUI")
root.geometry("1200x720")
root.resizable(False, False)

file_path_var = tk.StringVar()


previous_uploading_progress = tk.StringVar()
previous_uploading_progress.set(0.0)


file_select_button = tk.Button(root, text="Choose file to upload",
                               command=lambda: sharelib.select_file(file_path_var))
file_upload_button = tk.Button(root, text="Upload selected file",
                               command=lambda: sharelib.upload_file(file_path_var, file_uploading_proxy, previous_uploading_progress))


file_select_button.pack()
file_upload_button.pack()

uploading_progress_bar = ttk.Progressbar()
uploading_progress_bar.pack()


update_progress_bar()

root.mainloop()
