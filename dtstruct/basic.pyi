from dtstruct.core import DataType

# byte
int8be_t: DataType[int] = ...
uint8be_t: DataType[int] = ...
int8le_t: DataType[int] = ...
uint8le_t: DataType[int] = ...

# short
int16be_t: DataType[int] = ...
uint16be_t: DataType[int] = ...
int16le_t: DataType[int] = ...
uint16le_t: DataType[int] = ...

# long
int32be_t: DataType[int] = ...
uint32be_t: DataType[int] = ...
int32le_t: DataType[int] = ...
uint32le_t: DataType[int] = ...

# long long
int64be_t: DataType[int] = ...
uint64be_t: DataType[int] = ...
int64le_t: DataType[int] = ...
uint64le_t: DataType[int] = ...

# float 16bit
float16be_t: DataType[int] = ...
float16le_t: DataType[int] = ...

# float 32bit
float32be_t: DataType[int] = ...
float32le_t: DataType[int] = ...

# float 64bit
float64be_t: DataType[int] = ...
float64le_t: DataType[int] = ...

# boolean
boolbe_t: DataType[bool] = ...
boolle_t: DataType[bool] = ...