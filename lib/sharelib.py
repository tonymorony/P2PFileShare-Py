import platform
import os
import re
import slickrpc
import shutil
import math
from tkinter.filedialog import askopenfilename
import ttkthemes as tkT
import tkinter as tk
from tkinter import ttk
import pprint


# just to set custom timeout
class CustomProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=30000):
        config = dict()
        if conf_file:
            config = slickrpc.ConfigObj(conf_file)
        if service_url:
            config.update(self.url_to_conf(service_url))
        if service_port:
            config.update(rpcport=service_port)
        elif not config.get('rpcport'):
            config['rpcport'] = 7771
        self.conn = self.prepare_connection(config, timeout=timeout)


# TODO: that's temporary stub to not take control during file uploading
class FileUploadingProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=1):
        config = dict()
        if conf_file:
            config = slickrpc.ConfigObj(conf_file)
        if service_url:
            config.update(self.url_to_conf(service_url))
        if service_port:
            config.update(rpcport=service_port)
        elif not config.get('rpcport'):
            config['rpcport'] = 7771
        self.conn = self.prepare_connection(config, timeout=timeout)


def def_credentials(chain, mode="usual"):
    rpcport = ''
    ac_dir = ''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Win64' or operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    if chain == 'KMD':
        coin_config_file = str(ac_dir + '/komodo.conf')
    else:
        coin_config_file = str(ac_dir + '/' + chain + '/' + chain + '.conf')
    with open(coin_config_file, 'r') as f:
        for line in f:
            l = line.rstrip()
            if re.search('rpcuser', l):
                rpcuser = l.replace('rpcuser=', '')
            elif re.search('rpcpassword', l):
                rpcpassword = l.replace('rpcpassword=', '')
            elif re.search('rpcport', l):
                rpcport = l.replace('rpcport=', '')
    if len(rpcport) == 0:
        if chain == 'KMD':
            rpcport = 7771
        else:
            print("rpcport not in conf file, exiting")
            print("check "+coin_config_file)
            exit(1)
    if mode == "usual":
        return CustomProxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))
    else:
        return FileUploadingProxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)))


def select_file(file_path_var, selected_file_label):
    path_to_file = askopenfilename(initialdir="/", title="Select A File")
    file_name = path_to_file.split("/")[-1:][0]
    print(path_to_file)
    if len(file_name) < 16:
        file_path_var.set(path_to_file)
        selected_file_label["text"] = path_to_file
    else:
        error_message = "File name > 15 symbols. Please rename it or use different file."
        file_path_var.set(error_message)
        selected_file_label["text"] = error_message


# TODO: progress bar stop to update if user upload >1 file per session
# upd: it's actual on Linux only - on Windows works like a charm
def upload_file(file_path, rpc_proxy, uploading_delta):
    path_string = file_path.get()
    operating_system = platform.system()
    file_name = path_string.split("/")[-1:][0]
    # copying file to temp directory
    if operating_system == 'Win64' or operating_system == 'Windows':
        print(file_name)
        try:
            shutil.copyfile(path_string, os.getenv('APPDATA') + "/dexp2p/" + file_name)
        except FileNotFoundError:
            os.mkdir(os.getenv('APPDATA') + "/dexp2p")
            shutil.copyfile(path_string, os.getenv('APPDATA') + "/dexp2p/" + file_name)
    else:
        try:
            shutil.copy(path_string, os.getenv('HOME')+'/dexp2p/'+file_name)
        except FileNotFoundError:
            os.mkdir(os.getenv('HOME')+'/dexp2p/')
            shutil.copy(path_string, os.getenv('HOME')+'/dexp2p/'+file_name)
    print("Uploading file " + path_string)
    print(rpc_proxy.DEX_publish(file_name))
    # TODO: removing file from temp dir after successful uploading -
    #  now it non-det because we not tracking uploading finishing
    # os.remove('/usr/local/dexp2p/'+file_name)
    # uploading_delta.set(0.0)


def download_file(selected_file, rpc_proxy):
    download_command_result = rpc_proxy.DEX_subscribe(selected_file["values"][1], "0", "0", selected_file["values"][2])
    popup = tkT.ThemedTk()
    popup.title("DEXP2P fileshare GUI")
    popup.set_theme('equilux', themebg=True)
    downloading_info_mesasge = "Downloaded files saving to the same folder with daemon as filiename.publisherpubkey\n"
    downloading_result_text = tk.Text(popup)
    downloading_result_text.pack()
    downloading_result_text.configure(state='normal')
    downloading_result_text.replace("1.0", "100.0", downloading_info_mesasge + pprint.pformat(download_command_result))
    downloading_result_text.configure(state='disabled')


# https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python <3
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def connnection_popup():
    connection_popup = tkT.ThemedTk()
    ac_name_var = tk.StringVar()
    connection_popup.geometry("400x400")
    connection_popup.title("DEXP2P fileshare GUI")
    connection_popup.set_theme('equilux', themebg=True)
    ticker_input_label = ttk.Label(text="Please input chain ticker: ")
    ticker_input_entry = ttk.Entry(connection_popup)
    ticker_input_entry.insert(tk.END, 'FILET1')
    try_to_connect_button = ttk.Button(connection_popup, text="Start GUI",
                                       command= lambda: connect_gui_to_daemon(ticker_input_entry.get(),
                                                                                      down_daemon_message_label, connection_popup, ac_name_var))
    down_daemon_message_label = tk.Label(connection_popup, width=100,
                                         height=10, font=("Helvetica", 16))
    ticker_input_label.pack()
    ticker_input_entry.pack()
    try_to_connect_button.pack()
    down_daemon_message_label.pack(padx=(10,10), pady=(50,50))
    connection_popup.mainloop()
    return ac_name_var.get()


def connect_gui_to_daemon(ac_name_ticker, text_label, root_window, ac_name_app_var):
    try:
        chain_proxy = def_credentials(ac_name_ticker)
        file_uploading_proxy = def_credentials(ac_name_ticker, "uploading")
        print("Connected to " + ac_name_ticker)
        ac_name_app_var.set(ac_name_ticker)
        root_window.destroy()
    except Exception as e:
        print(e)
        down_daemon_message = "Can't connect to " + ac_name_ticker + " daemon.\n Please start it with dexp2p param first!"
        print(down_daemon_message)
        text_label["text"] = down_daemon_message

