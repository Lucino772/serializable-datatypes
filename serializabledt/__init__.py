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
from .core import adapter, template, transformer

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


#### EXAMPLE 2 ####
# import zlib
# import struct
# import dtstruct


# bytearray_t = dtstruct.template(
#     name='bytearray_t',
#     write=...,
#     read=...,
#     size=lambda self, ctx: ctx['len']
# )

# string_t = dtstruct.adapter(
#     name='string_t',
#     template=bytearray_t,
#     encode=...,
#     decode=...,
#     args={ 'encoding': str }
# )

# compressed_t = dtstruct.transformer(
#     write=...,
#     read=...,
#     args={ 'level': int }
# )

# packet_t = dtstruct.compose(
#     # TODO: lenght must be given too
#     raw=bytearray_t,
#     text=string_t('utf-8'),
#     raw_zlib=compressed_t(bytearray_t),
#     text_zlib=compressed_t(string_t('utf-8'))
# )

# buffer = ...

# bytearray_t.write(buffer, b'Hello World !')
# string_t('utf-8').write(buffer, 'Hello World !')
# compressed_t(bytearray_t).write(buffer, b'Hello World !')
# compressed_t(string_t('utf-8')).write(buffer, 'Hello World !')

# packet_t.write(buffer,
#     raw=b'Hello World !',
#     text='Hello World !',
#     raw_zlib=b'Hello World !',
#     text_zlib='Hello World !'
# )

# bytearray_t.read(buffer, len=13)
# string_t('utf-8').read(buffer, len=13)
# compressed_t(bytearray_t).read(buffer, len=21)
# compressed_t(string_t('utf-8')).read(buffer, len=21)

# packet = packet_t.read(buffer)
