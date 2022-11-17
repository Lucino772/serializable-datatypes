from struct import Struct

import dtstruct

struct_t = dtstruct.template(
    "struct_t",
    write=lambda self, buffer, value, _: buffer.write(self.fmt.pack(value)),
    read=lambda self, buffer, ctx: self.fmt.unpack(
        buffer.read(self.get_size(ctx))
    )[0],
    size=lambda self, _: self.fm.size,
    args={"byteorder": str, "format": str},
    variables={"fmt": lambda self: Struct(f"{self.byteorder}{self.format}")},
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
