# motor.py
from protocol import *
from convert import *

class Motor:
    def __init__(self, ser, addr):
        self.ser = ser
        self.addr = addr

    def enable(self):
        self.ser.write(enable(self.addr))

    def home(self):
        self.ser.write(home(self.addr))

    def move_single(self, speed_mm_s, dist_mm, acc=0, absolute=True):
        rpm = mmps_to_rpm(speed_mm_s)
        pulses = mm_to_pulse(dist_mm)
        pkt = multi_motor_move(self.addr, rpm, acc, pulses, absolute)
        self.ser.write(pkt)
        print("TX:", pkt.hex(" "))
        pkt_sync = trigger_synchronous_motion()
        self.ser.write(pkt_sync)

    def read_motor_position(self):
        """
        读取指定电机实时位置
        返回 mm 整数
        协议格式：
        Addr 36 Sign PosH PosL XX XX 6B
        """
        if not self.ser:
            return 0.0

        # ---------- 1. 清空旧缓存 ----------
        self.ser.reset_input_buffer()
        time.sleep(0.01)
        self.ser.reset_output_buffer()
        time.sleep(0.01)

        # ---------- 2. 发送指令 ----------
        cmd = bytes([self.addr, 0x36, 0x6B])
        print("[TX] ->", ' '.join(f"{b:02X}" for b in cmd))
        self.ser.write(cmd)

        # ---------- 3. 等待返回 ----------
        timeout = time.time() + 0.2
        buffer = b''

        while time.time() < timeout:
            if self.ser.in_waiting:
                buffer += self.ser.read(self.ser.in_waiting)

                print("[buffer] ->",
                            ' '.join(f"{b:02X}" for b in buffer))

                # 查找完整帧
                while True:
                    start = buffer.find(bytes([self.addr, 0x36]))
                    end   = buffer.find(bytes([0x6B]), start)

                    if start != -1 and end != -1:
                        frame = buffer[start:end+1]
                        buffer = buffer[end+1:]

                        print("[RX FRAME] ->",
                            ' '.join(f"{b:02X}" for b in frame))

                        # 至少包含：
                        # Addr 36 Sign PosH PosL ... 6B
                        if len(frame) == 8:
                            sign = frame[2]
                            #pos_bytes = frame[3:7]   # 前两个字节 = mm
                            int_mm = int.from_bytes(frame[3:5], 'big')     # D3 D2
                            frac   = int.from_bytes(frame[5:7], 'big')     # D1 D0
                            pos = int_mm + frac / 65536.0
                            if sign == 0x00:
                                pos = -pos

                            return pos
                    else:
                        break

            time.sleep(0.005)

        print("读取位置超时")
        return -9999
