# AX.25 Telemetry Encoder 

import math
import time
import ax25
import crcmod
import crcmod.predefined
import numpy as np
from scipy.io.wavfile import write

SAMPLE_RATE = 48000

BIT_RATE = 1200

MARK = 1200
SPACE = 2200

SAMPLES_PER_BIT = SAMPLE_RATE // BIT_RATE


def bit_stuff(bits):

    result = ""
    count = 0

    for bit in bits:

        result += bit

        if bit == '1':
            count += 1
        else:
            count = 0

        if count == 5:
            result += '0'
            count = 0

    return result

def bit_destuff(bits):

    result = ""

    count = 0
    i = 0

    while i < len(bits):

        bit = bits[i]
        result += bit

        if bit == '1':
            count += 1
        else:
            count = 0

        if count == 5:
            i += 1
            count = 0

        i += 1

    return result

def nrzi_encode(bits):

    state = '1'

    result = ""

    for bit in bits:

        if bit == '0':

            state = (
                '0'
                if state == '1'
                else '1'
            )

        result += state

    return result

def nrzi_decode(encoded):

    previous = '1'

    result = ""

    for current in encoded:

        if current == previous:
            result += '1'
        else:
            result += '0'

        previous = current

    return result

def afsk_modulate(bits):

    phase = 0.0
    audio = []

    for bit in bits:

        freq = MARK if bit == '1' else SPACE

        for _ in range(SAMPLES_PER_BIT):

            audio.append(np.sin(phase))

            phase += (
                2*np.pi*freq
                / SAMPLE_RATE
            )

    return np.array(audio)




src = ax25.Address("AKISAT")
dst = ax25.Address("CQ")

frame = ax25.Frame(
    dst=dst,
    src=src,
    control=0x03,      # UI frame
    pid=0xF0,          # No Layer 3 protocol
    data=b"T# RF lab RF Lab"
)

print(frame)
raw = frame.pack()

print("HEX:")
print(raw.hex())

print("\nBYTES:")
print(raw)

crc16 = crcmod.predefined.mkCrcFun('x-25')

fcs = crc16(raw) & 0xFFFF

print(hex(fcs))

frame_with_fcs = raw + fcs.to_bytes(2, "little")

FLAG = bytes([0x7E])

packet = (
    FLAG
    + frame_with_fcs
    + FLAG
)

bits = ''.join(
    format(byte, '08b')[::-1]
    for byte in packet
)

FLAG = bits[:8]
BODY = bits[8:-8]
END_FLAG = bits[-8:]

stuffedbody = bit_stuff(BODY)
# Add a preamble/postamble of multiple flag bytes for reliable sync
preamble_flags = 50
result = FLAG * preamble_flags + stuffedbody + END_FLAG * preamble_flags
print(result)

flag = "01111110"


nrzi_bits = nrzi_encode(result)

recovered_bits = nrzi_decode(nrzi_bits)

print(len(nrzi_bits) == len(recovered_bits))

print("Bits:", len(nrzi_bits))
print("Duration:", len(nrzi_bits)/1200, "seconds")

audio = afsk_modulate(nrzi_bits)

audio = (
    audio / np.max(np.abs(audio))
    * 22000
).astype(np.int16)
print(np.max(audio))
print(np.min(audio))
write(
    "packet.wav",
    48000,
    audio
)






