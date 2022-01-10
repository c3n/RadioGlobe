#! /usr/bin/python3
import time
import threading
import spidev

BUS = 0
ENCODER_RESOLUTION = 1024
STICKY = 2
STAY_STUCK_THRESH = 10

def check_parity(reading:int):
  # The parity bit is bit 0 (note the reading is most-significant-bit first)
  reading_without_parity_bit = reading >> 1
  parity_bit = reading & 0b1

  computed_parity = 0
  while reading_without_parity_bit:
    # XOR with the first bit
    computed_parity ^= (reading_without_parity_bit & 0b1)

    # Shift the bits right
    reading_without_parity_bit >>= 1

  return (parity_bit == computed_parity)


class Encoders(threading.Thread):
  def __init__(self, q, offset=[0,0]):
    threading.Thread.__init__(self)
    self.daemon=True
    self.q = q
    self.offset=offset
    self.stuckat=[0,0]
    self.stayed=0
    self.stuck=False
    self.last=None
    self.spis=[spidev.SpiDev(BUS,i) for i in range(2)]
    for s in self.spis:
      s.max_speed_hz=100000
      s.mode=1
    self.start()

  def read_spi(self):
    rr=[s.readbytes(2) for s in self.spis]
    rr=[x[0]<<8|x[1] for x in rr]
    if all(check_parity(x) for x in rr):
      return [ENCODER_RESOLUTION-1-(rr[1]>>6),rr[0]>>6]

  def zero(self):
    self.offset=[x for x in self.last]
    self.stuck=False
    return self.offset

  def run(self):
    while True:
      time.sleep(0.1)
      r=self.read_spi()
      if not r:
        continue
      sameexactvalue=self.last==r
      self.last=r
      moved=any(STICKY<(self.stuckat[i]-r[i])%ENCODER_RESOLUTION<1024-STICKY for i in range(2))
      if moved:
        if self.stuck:
          print("unstuck")
        self.stuck=False
        self.stayed=0
        self.stuckat=r
      if self.stuck:
        continue
      latlon=[((r[i]-self.offset[i])*360/ENCODER_RESOLUTION+180)%360-180 for i in range(2)]
      if not moved:
        self.stayed+=1
        if self.stayed>STAY_STUCK_THRESH:
          self.stuck=True
          self.stuckat=r
          self.q.put(("lat_lon_stuck",latlon))
          print("stuck",r)
          continue
      if not sameexactvalue:
        self.q.put(("lat_lon_moved",latlon))

if __name__=="__main__":
  import queue
  q=queue.Queue()
  pe=Encoders(q)
  while True:
    print(q.get())