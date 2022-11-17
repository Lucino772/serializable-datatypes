import json
from struct import Struct

import dtstruct

struct_t = dtstruct.template(
    "struct_t",
    write=lambda self, buffer, value, _: buffer.write(self.fmt.pack(value)),
    read=lambda self, buffer, ctx: self.fmt.unpack(
        buffer.read(self.get_size(ctx))
    )[0],
    size=lambda self, _: self.fmt.size,
    args={"byteorder": str, "format": str},
    variables={"fmt": lambda self: Struct(f"{self.byteorder}{self.format}")},
)

# bytearray
bytearray_t = dtstruct.template(
    "bytearray_t",
    write=lambda self, buffer, value, _: buffer.write(value),
    read=lambda self, buffer, ctx: buffer.read(self.get_size(ctx)),
    size=lambda self, ctx: ctx["len"],
)()

# string
string_t = dtstruct.adapter(
    "string_t",
    template=bytearray_t,
    encode=lambda self, value, ctx: str(value).encode(self.encoding),
    decode=lambda self, value, ctx: bytes(value).decode(self.encoding),
    args={"encoding": str},
)

# json
json_t = dtstruct.adapter(
    "json_t",
    template=bytearray_t,
    encode=lambda self, value, ctx: json.dumps(value).encode(self.encoding),
    decode=lambda self, value, ctx: json.loads(value.decode(self.encoding)),
    args={"encoding": str},
)

# byte
int8be_t = struct_t(">", "b")
uint8be_t = struct_t(">", "B")
int8le_t = struct_t("<", "b")
uint8le_t = struct_t("<", "B")

# short
int16be_t = struct_t(">", "h")
uint16be_t = struct_t(">", "H")
int16le_t = struct_t("<", "h")
uint16le_t = struct_t("<", "H")

# long
int32be_t = struct_t(">", "l")
uint32be_t = struct_t(">", "L")
int32le_t = struct_t("<", "l")
uint32le_t = struct_t("<", "L")

# long long
int64be_t = struct_t(">", "q")
uint64be_t = struct_t(">", "Q")
int64le_t = struct_t("<", "q")
uint64le_t = struct_t("<", "Q")

# float 16bit
float16be_t = struct_t(">", "e")
float16le_t = struct_t("<", "e")

# float 32bit
float32be_t = struct_t(">", "f")
float32le_t = struct_t("<", "f")

# float 64bit
float64be_t = struct_t(">", "d")
float64le_t = struct_t("<", "d")

# boolean
boolbe_t = struct_t(">", "?")
boolle_t = struct_t("<", "?")
