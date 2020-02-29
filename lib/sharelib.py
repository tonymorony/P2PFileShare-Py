import platform
import os
import re
import slickrpc
import shutil
import time
import threading
from tkinter.filedialog import askopenfilename


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


# that's temporary stub to not take control during file uploading
class FileUploadingProxy(slickrpc.Proxy):
    def __init__(self,
                 service_url=None,
                 service_port=None,
                 conf_file=None,
                 timeout=2):
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


def select_file(file_path_var):
    # TODO: check if filename is < 15 symbols
    filename = askopenfilename(initialdir="/", title="Select A File")
    print(filename)
    file_path_var.set(filename)


# TODO: progress bar stop to update if user upload >1 file per session
def upload_file(file_path, rpc_proxy, uploading_delta):
    path_string = file_path.get()
    file_name = path_string.split("/")[-1:][0]
    # copying file to temp directory
    # TODO: different directory for Windows
    try:
        shutil.copy(path_string, '/usr/local/dexp2p/'+file_name)
    except FileNotFoundError:
        # TODO: it's quite tricky now if not script executor now owner of /usr/bin
        os.mkdir("/usr/local/dexp2p/")
        shutil.copy(path_string, '/usr/local/dexp2p/'+file_name)
    print("Uploading file " + path_string)
    rpc_proxy.DEX_publish(file_name)
    # TODO: removing file from temp dir after successful uploading - now it non-det because we not tracking uploading finishing
    # os.remove('/usr/local/dexp2p/'+file_name)
    # uploading_delta.set(0.0)
