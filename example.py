import io
import struct
import zlib

import dtstruct

struct_t = dtstruct.template(
    "struct_t",
    write=lambda self, buffer, value, ctx: buffer.write(self.fmt.pack(value)),
    read=lambda self, buffer, ctx: self.fmt.unpack(
        buffer.read(self.get_size(ctx))
    )[0],
    size=lambda self, ctx: self.fmt.size,
    args={"byteorder": str, "format": str},
    variables={
        "fmt": lambda self: struct.Struct(f"{self.byteorder}{self.format}")
    },
)

bytearray_t = dtstruct.template(
    "bytearray_t",
    write=lambda self, buffer, value, ctx: buffer.write(value),
    read=lambda self, buffer, ctx: buffer.read(self.get_size(ctx)),
    size=lambda self, ctx: ctx["len"],
)()

string_t = dtstruct.adapter(
    "string_t",
    template=bytearray_t,
    encode=lambda self, value, ctx: str(value).encode(self.encoding),
    decode=lambda self, value, ctx: bytes(value).decode(self.encoding),
    args={"encoding": str},
)

compressed_t = dtstruct.transformer(
    "compressed_t",
    write=lambda self, _bytes, ctx: zlib.compress(_bytes),
    read=lambda self, _bytes, ctx: zlib.decompress(_bytes),
    size=lambda self, ctx: ctx["len"],
)

int8be_t = struct_t(">", "b")
uint8be_t = struct_t(">", "B")

with io.BytesIO() as buffer:
    print("INT8BE", int8be_t.write(buffer, -30, None))
    print("UINT8BE", uint8be_t.write(buffer, 30, None))

    print("BYTES", bytearray_t.write(buffer, b"Hello World !", None))
    print("TEXT1", string_t("utf-8").write(buffer, "Hello World !", None))
    print("TEXT2", string_t("utf-16").write(buffer, "Hello World !", None))

    print(
        "ZLIB1",
        compressed_t(bytearray_t).write(buffer, b"Hello World !", None),
    )
    print(
        "ZLIB2",
        compressed_t(string_t("utf-8")).write(buffer, "Hello World !", None),
    )

    data = buffer.getvalue()
    print(data, len(data))

with io.BytesIO(data) as buffer:
    print("INT8BE", int8be_t.read(buffer, None))
    print("UINT8BE", uint8be_t.read(buffer, None))

    print("BYTES", bytearray_t.read(buffer, {"len": 13}))
    print("TEXT1", string_t("utf-8").read(buffer, {"len": 13}))
    print("TEXT1", string_t("utf-16").read(buffer, {"len": 28}))

    print("ZLIB1", compressed_t(bytearray_t).read(buffer, {"len": 21}))
    print("ZLIB2", compressed_t(string_t("utf-8")).read(buffer, {"len": 21}))
