from construct import Bytes, Const, Hex, Int8ub, Struct

GCD_MARKER = b"\x01\x00\x01\x00"
GCD_MAGIC = b"GARMINd\x00"

GCD_RECORD_HEADER = Struct(
    "marker" / Const(GCD_MARKER),
    "type" / Hex(Int8ub),
    "field_a" / Bytes(2),  # unknown meaning
    "field_b" / Bytes(2),  # LE uint16 length for types 0x4C, 0x67 only
)

GCD_FILE_HEADER = Struct(
    "magic" / Const(GCD_MAGIC),
    "raw_header_rest" / Bytes(0x1000 - len(GCD_MAGIC)),
)
