# protocol.py
import struct
import time

END = 0x6B  # 通讯结束符

def build_packet(addr, cmd, data=b''):
    """
    构造单机命令包
    addr: 电机地址
    cmd: 命令码
    data: 数据字节序列
    """
    packet = bytes([addr, cmd]) + data + bytes([END])
    print("[TX] ->", ' '.join(f"{b:02X}" for b in packet))
    return packet

def enable(addr):
    """
    使能电机
    """
    return build_packet(addr, 0xF3, bytes([0x01]))

def home(addr):
    """
    电机回零
    """
    return build_packet(addr, 0x0A, bytes([0x6D]))

def multi_motor_move(addr_move, rpm, acc, pulses, absolute=True):
    """
    构造多电机广播命令
    addr_move: 运动的电机地址
    rpm: 转速 (RPM)
    acc: 加速度
    pulses: 脉冲数
    absolute: True=绝对运动, False=相对运动
    addr_feedback: 另一台电机返回实时位置的地址
    """
    direction = 1 if pulses >= 0 else 0
    pulses = abs(int(pulses))
    absolute_flag = 1 if absolute else 0

    # -----------------------------
    # 运动电机命令数据部分（10字节）
    # -----------------------------
    data_move = struct.pack(">BHBIBB",
                            direction,    # 方向
                            rpm,          # 转速高低位合并
                            acc,          # 加速度
                            pulses,       # 脉冲数
                            absolute_flag,# 绝对/相对
                            1)            # 同步标志=0，立即运动

    # -----------------------------
    # 另一台电机返回信息命令
    # -----------------------------
    #data_feedback = bytes([addr_feedback, 0x36, END])

    # -----------------------------
    # 广播命令
    # -----------------------------
    # 数据长度 = len(data_move) + len(data_feedback)
    #data_len = len(data_move) + len(data_feedback)
    # if data_len > 0xFF:
    #     raise ValueError("数据太长，需要调整总字节长度")

    # 构造最终广播命令包
    # 00 = 广播地址
    # AA = 功能码
    # 0015 = 数据长度
     #bytes([0x00, 0xAA, 0x00, 0x15]) + \
    packet =bytes([addr_move, 0xFD]) + data_move + bytes([END])
             
    
  
    #+bytes([0x00, 0xFF, 0x66, 0x6B])
    
    #data_feedback+bytes([END]) 

    # 打印命令用于调试
    print("[MULTI MOTOR TX] ->", ' '.join(f"{b:02X}" for b in packet))

    return packet

def trigger_synchronous_motion():
    """
    延迟50ms后触发广播同步运动
    """
    time.sleep(0.05)  # 50ms延迟
    packet_sync = bytes([0x00, 0xFF, 0x66, 0x6B])
    print("[SYNC TX] ->", ' '.join(f"{b:02X}" for b in packet_sync))
    
    return packet_sync