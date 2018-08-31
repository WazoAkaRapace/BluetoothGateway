""" This file contains the protocol structures. """
from construct import (Struct, Int8ub, Int16ub, Const, Padded, Byte, Enum,
                       Embedded, PascalString,
                       BytesInteger,
                       Mapping)


# Some help from https://github.com/Marcocanc/node-mi-lamp/blob/master/notes.md

PairingStatus = "status" / Struct(
    "pairing_status" / Enum(Byte,
                            PairRequest=0x01,
                            PairSuccess=0x02,
                            PairFailed=0x03,
                            PairedDevice=0x04,
                            UnknownState=0x06,
                            Disconnected=0x07)  # not documented?
)

# Name doesn't fit to one element, so there's an index I assume..
# >>> x = bytes.fromhex("43 51 01 00 0d 5965656c696768742042656473")
# >>> x
# b'CQ\x01\x00\rYeelight Beds'
# >>> x = bytes.fromhex("43 51 01 01 08 696465204c616d700000000000")
# >>> x
# b'CQ\x01\x01\x08ide Lamp\x00\x00\x00\x00\x00'

Name = "name" / Struct(
    "id" / Byte,
    "index" / Byte,  # convert greeedystring to use this
    "text" / PascalString(Byte, "ascii"),
)

Version = "version" / Struct(
    "currentrunning" / Enum(Byte, App1=0x01, App2=0x02, Candela=0x31),
    "hw_version" / Int16ub,
    "sw_version_app1" / Int16ub,
    "sw_version_app2" / Int16ub,
    "beacon_version" / Int16ub,
)

SerialNumber = "serialno" / BytesInteger(12)

OnOff = "OnOff" / Struct(
    "state" / Mapping(Byte, {True: 0x01, False: 0x02})
)

# brightness max
# 4342 64 000000000000000000000000000000
# brightness min
# 4342 01 000000000000000000000000000000
# brightness middle
# 4342 31 000000000000000000000000000000

# 1-100
Brightness = "brightness" / Struct(
    "brightness" / Int8ub,
)

# Note, requests with (mostly) even, responses with odd

RequestType = "reqtype" / Mapping(Byte, {
    "SetOnOff": 0x40,
    "SetBrightness": 0x42}
                                  )


def getrequest(reqtype):
    payload = None

    if reqtype == "SetOnOff":
        payload = OnOff
    elif reqtype == "SetBrightness":
        payload = Brightness

    return "msg" / Padded(18, Struct(
        Const(0x43, Int8ub),
        "type" / RequestType,
        "payload" / Embedded(payload)))
