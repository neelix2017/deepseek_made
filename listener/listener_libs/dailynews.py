import subprocess
import feedparser

def start():
    data = feedparser.parse("https://podcast.rtvslo.si/radijski_dnevnik.xml")
    link = data.entries[0].links[0].href
    print(link)

    prog = "c:/Program Files/VideoLAN/VLC/vlc"
    guid = "8fb5c852-5c8e-442d-9411-6fac2a1fb498"
    #     guid = "8fb5c852-5c8e-442d-9411-6fac2a1fb498" --> SPEAKER
    #     guid = "3504486b-d61a-400a-973e-dd47d1b78526"
    vol = 10
    #prog = f"{prog} -I null --play-and-exit --no-loop --no-repeat --aout=directsound --directx-audio-device={guid} --gain={vol} {mp3}"

    #subprocess.Popen([prog,   link , "-I null", "--play-and-exit", "--no-loop","--aout=directsound","--directx-audio-device="+guid])

    requests.post("http://192.168.0.111:9091/jsonrpc", json = {"jsonrpc":"2.0","id":1,"method":"Player.Open","params":{    "item": {
            "file": link
        }}})