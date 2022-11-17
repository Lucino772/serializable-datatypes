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
