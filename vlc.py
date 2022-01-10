import re
import time
import subprocess
from threading import Thread,Lock

#statusere=re.compile(r"\( state (.+) \)")
statsre=re.compile(r".*buffers played *: *([^ ]+)")

class VLCStateThread(Thread):
    def __init__(self,f,q):
        Thread.__init__(self)
        self.daemon=True
        self.f=f
        self.state="?"
        self.q=q
        self.start()
    def run(self):
        for line in self.f:
            line=line.strip()
            if line=="( state stopped )":
                self.q.put(("vlc","stopped"))
            else:
                m=statsre.match(line)
                if m:
                    if m[1]=="0":
                        self.q.put(("vlc","trying"))
                    else:
                        self.q.put(("vlc","playing"))
                #else:
                #    print(line.strip())

class VLC(Thread):
    def __init__(self,q):
        Thread.__init__(self)
        self.daemon=True
        self.vlcproc=subprocess.Popen(["vlc"],universal_newlines=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        self.lock=Lock()
        self.killed=False
        self.state=VLCStateThread(self.vlcproc.stdout,q)
        self.lasturl=""
        self.play_start_at=None
        self.start()
    def run(self):
        while not self.killed:
            time.sleep(0.5)
            with self.lock:
                self.vlcproc.stdin.write("status\nstats\n")
                self.vlcproc.stdin.flush()
    def play(self,url):
        print("vlc:",url)
        with self.lock:
            self.vlcproc.stdin.write(f"stop\nclear\nadd {url}\n")
            self.vlcproc.stdin.flush()
        self.play_start_at=time.time()
    def stop(self):
        self.play_start_at=None
        with self.lock:
            self.vlcproc.stdin.write(f"stop\nclear\n")
            self.vlcproc.stdin.flush()
