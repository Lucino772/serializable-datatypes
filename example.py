# import io
# import struct
# from serializabledt.template import template

# struct_t = template(
#     name='struct_t',
#     write=lambda buffer, val, args, ctx: buffer.write(args['fmt'].pack(val)),
#     read=lambda buffer, args, ctx: args['fmt'].unpack(buffer.read(args['fmt'].size))[0],
#     args={ 'byteorder': str, 'format': str },
#     variables={
#         'fmt': lambda args: struct.Struct('{}{}'.format(args['byteorder'], args['format']))
#     },
#     size=lambda self, ctx: self.fmt.size
# )
import io
import struct
import zlib

from serializabledt.builder import TemplateBuilder

struct_t = TemplateBuilder(
    name="struct_t",
    args={"byteorder": str, "format": str},
    variables={
        "fmt": lambda self: struct.Struct(
            f"{self.args.byteorder}{self.args.format}"
        )
    },
    size=lambda self, ctx: self.fmt.size,
    write=lambda self, buffer, val, ctx: buffer.write(self.fmt.pack(val)),
    read=lambda self, buffer, ctx: self.fmt.unpack(
        buffer.read(self.get_size(ctx))
    )[0],
).build()


int8be_t = struct_t(">", "b")
uint8be_t = struct_t(">", "B")

bytearray_t = TemplateBuilder(
    name="bytearray_t",
    write=lambda self, buffer, val, ctx: buffer.write(val),
    read=lambda self, buffer, ctx: buffer.read(self.get_size(ctx)),
    size=lambda self, ctx: ctx["len"],
).build()()

string_t = TemplateBuilder(
    name="string_t",
    template=bytearray_t,
    encode=lambda self, val, ctx: str(val).encode(self.encoding),
    decode=lambda self, val, ctx: bytes(val).decode(self.encoding),
    args={"encoding": str},
).build()

compressed_string_t = TemplateBuilder(
    name="string_t",
    template=string_t,
    deform=lambda self, val, ctx: zlib.compress(val),
    reform=lambda self, val, ctx: zlib.decompress(val),
).build()


with io.BytesIO() as buffer:
    print("INT8BE", int8be_t.write(buffer, -30, None))
    print("UINT8BE", uint8be_t.write(buffer, 30, None))
    print("BYTES", bytearray_t.write(buffer, b"Hello World !", None))
    print("UTF-8", string_t("utf-8").write(buffer, "Hello World !", None))
    print("UTF-16", string_t("utf-16").write(buffer, "Hello World !", None))
    print(
        "ZLIB",
        compressed_string_t("utf-8").write(buffer, "Hello World !", None),
    )

    data = buffer.getvalue()
    print(data, len(data))

with io.BytesIO(data) as buffer:
    print("INT8BE", int8be_t.read(buffer, None))
    print("UINT8BE", uint8be_t.read(buffer, None))
    print("BYTES", bytearray_t.read(buffer, {"len": 13}))
    print("UTF-8", string_t("utf-8").read(buffer, {"len": 13}))
    print("UTF-16", string_t("utf-16").read(buffer, {"len": 28}))
    print("ZLIB", compressed_string_t("utf-8").read(buffer, {"len": 21}))
