"""

Using the struct module:
    In little/big-endian:

    # Fixed Size
    uint8  - int8  (byte)
    uin16  - int16 (short)
    uint32 - int32 (int / long)
    uint64 - int64 (long long)

    float16        (?)
    float32        (float)
    float64        (double)

    bool           (boolean)

    # Var Size
    varint         (int) - May be specific to minecraft
    varlong        (int) - May be specific to minecraft

    # Sequence
    bytearray      (bytes)
    string         (str)
    cstring        (str) - Null Terminated string

    array(T)       (T[])
"""
# import zlib
# import struct
# import dtstruct

# T ===> bytes
# K ===> T ===> bytes
# K ===> T ===> compress(bytes) ===> bytes

# bytes ===> T
# bytes ===> T ===> K
# bytes ===> uncompress(bytes) ===> T ===> K

# struct_t = dtstruct.template(
#     write=lambda val, ctx: this.fmt.pack(val),
#     read=lambda val, ctx: this.fmt.unpack(val)[0],
#     args={ 'byteorder': str, 'format': str },
#     variables={
#         'fmt': lambda: struct.Struct(f'{args.byteorder}{args.format}')
#     }
# )

# int8be_t = struct_t('>', 'b')
# uint8be_t = struct_t('>', 'B')

# bytearray_t = dtstruct.template(
#     write=lambda val, ctx: struct_t('>', 's' * len(val)).write(val),
#     read=lambda val, ctx: struct_t('>', 's' * ctx.len).read(val),
# )()

# string_t = dtstruct.template(
#     template=bytearray_t,
#     encode=lambda val, ctx: val.encode(args.encoding),
#     decode=lambda val, ctx: val.decode(args.encoding),
#     args={ 'encoding': (str, 'utf-8')}
# )()

# zlibcompressed_t = dtstruct.template(
#     template=bytearray_t,
#     tranform=lambda val: zlib.compress(val),
#     reform=lambda val: zlib.decompress(val),
# )()
