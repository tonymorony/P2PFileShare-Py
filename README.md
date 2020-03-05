Simple GUI interface mockup to demonstrate Filesharing (based on dexp2p) Komodo technology.

Special thanks to https://github.com/theblackmallard for great UX theme

Dependencies:
```
python 3.7+ is needed (because of this bug https://stackoverflow.com/questions/52440314/ttk-spinbox-missing-in-tkinter-ttk/52440947)
sudo apt-get install python3-pip libgnutls28-dev python3-tk python3-pil python3-pil.imagetk
pip3 install setuptools wheel slick-bitcoinrpc ttkthemes
```


![screenshot](https://i.imgur.com/f3fE7Tb.png)

## To use:

### 1. Start assetchain chain in dexp2p mode (with dexp2p param)

For example testchain: 

```
./komodod -ac_name=FILET1 -dexp2p=2 -ac_supply=999999 -addnode=95.217.44.58
```

You can also use dexp2p network with any existing assetchain! Just start it with dexp2p param. Beauty is that for dexp2p no blocks are needed - only peers connections matters.

### 2. Start program as `python3 main.py` (or .\main.exe if you use precompiled bins)
