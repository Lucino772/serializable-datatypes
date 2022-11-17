from typing import (
    Any,
    BinaryIO,
    Callable,
    Mapping,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    Union,
)

T = TypeVar("T")
K = TypeVar("K")
Context = Mapping[str, Any]
ComposeDataType = Union[
    DataType,
    Tuple[DataType, Callable[[Context], Any]],
    Tuple[
        DataType, Callable[[Context], Context], Callable[[Context], Context]
    ],
]

class _BaseTemplate:
    _setup_variables_method_name: str = ...

    def __init__(
        self,
        name: str,
        args: Mapping[str, Any] = None,
        variables: Mapping[str, Callable[["_BaseTemplate"], Any]] = None,
    ) -> None: ...

class TemplateBuilder(_BaseTemplate): ...
class AdapterBuilder(_BaseTemplate): ...
class TransformerBuilder(_BaseTemplate): ...
class ComposeBuilder: ...

class DataType(Protocol[T]):
    def write(self, buffer: BinaryIO, value: T, ctx: Context) -> int: ...
    def read(self, buffer: BinaryIO, ctx: Context) -> T: ...

def template(
    name: str,
    write: Callable[["TemplateBuilder", BinaryIO, T, Context], int],
    read: Callable[["TemplateBuilder", BinaryIO, Context], T],
    size: Callable[["TemplateBuilder", Context], int],
    args: Mapping[str, Any] = ...,
    variables: Mapping[str, Callable[[_BaseTemplate], Any]] = ...,
) -> Type[DataType[T]]: ...
def adapter(
    name: str,
    template: DataType[K],
    encode: Callable[["AdapterBuilder", T, Context], K],
    decode: Callable[["AdapterBuilder", K, Context], T],
    args: Mapping[str, Any] = ...,
    variables: Mapping[str, Callable[[_BaseTemplate], Any]] = ...,
) -> Type[DataType[T]]: ...
def transformer(
    name: str,
    write: Callable[["TransformerBuilder", bytes, Context], bytes],
    read: Callable[["TransformerBuilder", bytes, Context], bytes],
    size: Callable[["TransformerBuilder", Context], int],
    args: Mapping[str, Any] = ...,
    variables: Mapping[str, Callable[[_BaseTemplate], Any]] = ...,
) -> Type[DataType[Any]]: ...
def compose(
    __name: str, **kwargs: Mapping[str, ComposeDataType]
) -> Type[DataType]: ...
