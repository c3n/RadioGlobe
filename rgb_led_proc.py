import subprocess

class RGBLeds():
    def __init__(self):
        self.sp=subprocess.Popen(["sudo","./rgb_led.py"],stdin=subprocess.PIPE,universal_newlines=True)

    def volume(self,volume):
        self.sp.stdin.write(f"volume {volume}\n")
        self.sp.stdin.flush()

    def jogged(self,direction):
        self.sp.stdin.write(f"jogged {direction}\n")
        self.sp.stdin.flush()

    def calibrate(self):
        self.sp.stdin.write("calibrate\n")
        self.sp.stdin.flush()

    def tuning(self):
        self.sp.stdin.write("tuning\n")
        self.sp.stdin.flush()

    def playing(self):
        self.sp.stdin.write("playing\n")
        self.sp.stdin.flush()

    def paused(self):
        self.sp.stdin.write("paused\n")
        self.sp.stdin.flush()

