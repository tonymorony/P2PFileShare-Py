import tkinter as tk
from tkinter import ttk
from lib import sharelib
import threading

# TODO: make it as a setting?
ac_name = "FILET1"

chain_proxy = sharelib.def_credentials(ac_name)
file_uploading_proxy = sharelib.def_credentials(ac_name, "uploading")


def update_progress_bar():
    # separated rpc proxy because first one awaiting response from uploading command
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
    # .after is something like a tkinter "threads"
    root.after(100, update_progress_bar)


def update_files_list(files_table):
    print("updating files list")
    files_table.delete(*files_table.get_children())
    rpc_proxy = sharelib.def_credentials(ac_name)
    files_list_response = rpc_proxy.DEX_list("0", "0", "files")["matches"]
    print(files_list_response)
    for file in files_list_response:
        # TODO: convert file size to human readable
        files_table.insert("", "end", text=file["id"], values=[file["timestamp"], file["tagB"],
                                                               file["senderpub"], file["amountA"]])
    root.after(1000, lambda: update_files_list(files_table))


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
                               command=lambda: sharelib.upload_file(file_path_var, file_uploading_proxy,
                                                                    previous_uploading_progress))

# TODO: display the list of available to download files with download button + downloading progress bars
file_list_columns = ["Timestamp", "File name", "Publisher pubkey", "File size"]
files_list = ttk.Treeview(root, columns=file_list_columns, selectmode="browse")
files_list.heading('#0', text='File ID')
for i in range(1, len(file_list_columns)+1):
    files_list.heading("#"+str(i), text=file_list_columns[i-1])


file_select_button.pack()
file_upload_button.pack()

uploading_progress_bar = ttk.Progressbar()
uploading_progress_bar.pack()
files_list.pack()

update_progress_bar()
update_files_list(files_list)

# TODO: have to check if needed assetchain is started and assist user with it
root.mainloop()
