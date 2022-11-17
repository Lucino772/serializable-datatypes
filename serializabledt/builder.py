"""
class TemplateClass:
    def __init__(self, arg0: type0, arg1: type1, ...):
        self.arg0 = arg0
        self.arg1 = arg1
        ...

        self.var0 = ...

    @staticmethod
    def get_builder():
        return ...

    @property
    def args(self):
        "Usage: self.args.arg0"
        return ...

    @propery
    def vars(self):
        "Usage: self.vars.var0"
        return ...

    def get_size(self, ctx: dict):
        # if the data type has a fixed length simply return it,
        # if size of the data type is dynamic (ex: string),
        # return it from the context.

        # When using transform methods (deform, reform), a length
        # must be passed in the context, it's the only way to know
        return ...

    def write(self, buffer: BinaryIO, value: T, ctx: dict) -> int:
        # if encode function is present
        encoded_value = self.encode(value, ctx)

        with io.Bytes() as buffer:
            _write_function(self, buffer, encoded_value, ctx)
            written_data = buffer.getvalue()

        # if deform function is present
        deformed_data = self.deform(written_data, ctx)
        return buffer.write(deformed_data)

    def read(self, buffer: BinaryIO, ctx: dict) -> T:
        # if reform function is present
        deformed_data = buffer.read(self.get_size(ctx))
        reformed_data = self.reform(buffer, ctx)

        with io.Bytes(reformed_data) as buffer:
            encoded_value = _read_function(self, buffer, ctx)

        # if decode function is present
        decoded_value = self.decode(encoded_value, ctx)
        return decoded_value

    def encode(self, value: T, ctx: dict) -> K:
        pass

    def decode(self, value: K, ctx: dict) -> T:
        pass

    def deform(self, value: bytes, ctx: dict) -> bytes:
        pass

    def reform(self, value: bytes, ctx: dict) -> bytes:
        pass

"""
import io
import linecache
from typing import BinaryIO


class ArgsProxy:
    def __init__(self, obj: object, args: list):
        self.__obj = obj
        self.__args = args

    def __getattr__(self, argname):
        if argname not in self.__args:
            raise ValueError(f"Invalid argument {argname}")

        return getattr(self.__obj, argname)


class TemplateBuilder:
    def __init__(
        self,
        name=None,
        args=None,
        variables=None,
        write=None,
        read=None,
        size=None,
        encode=None,
        decode=None,
        deform=None,
        reform=None,
        template=None,
    ):
        self.name = name
        self.args = args if args is not None else {}
        self.variables = variables if variables is not None else {}
        self.write = write
        self.read = read
        self.size = size
        self.encode = encode
        self.decode = decode
        self.deform = deform
        self.reform = reform

        self.template = template

        self._cls_dict = {}

        if self.template is not None:
            self._init_template()

    def _create_init_script(self):
        lines = []

        # Initialize arguments
        for key in self.args.keys():
            lines.append(f"self.{key} = {key}")

        # Call function to initialize variables
        if self.variables is not None:
            lines.append("self._setup_variables()")

        if len(lines) == 0:
            lines.append("pass")

        return lines

    def _create_setup_variables_script(self):
        lines = []

        for varname in self.variables.keys():
            lines.append(
                f"self.{varname} = _extern_variables['{varname}'](self)"
            )

        if len(lines) == 0:
            lines.append("pass")

        return lines

    def _create_write_method(self):
        script = []
        if self.encode is not None:
            script.append("value = self.encode(value, ctx)")
        if self.deform is not None:
            script.append("with _BytesIO() as _buffer:")
            script.append("\t_write_function(self, _buffer, value, ctx)")
            script.append("\twritten_data = _buffer.getvalue()")
            script.append(
                "return buffer.write(self.deform(written_data, ctx))"
            )
        else:
            script.append("return _write_function(self, buffer, value, ctx)")

        write_method = self._create_method(
            "write",
            {"buffer": BinaryIO, "value": int, "ctx": dict},
            script,
            {
                "_write_function": self.write,
                "BinaryIO": BinaryIO,
                "_BytesIO": io.BytesIO,
            },
        )

        return write_method

    def _create_read_method(self):
        script = []

        if self.reform is not None:
            script.append(
                "written_value = self.reform(buffer.read(self.get_size(ctx)), ctx)"
            )
            script.append("with _BytesIO(written_value) as _buffer:")
            script.append("\tvalue = _read_function(self, _buffer, ctx)")
        else:
            script.append("value = _read_function(self, buffer, ctx)")

        if self.decode is not None:
            script.append("return self.decode(value, ctx)")
        else:
            script.append("return value")

        read_method = self._create_method(
            "read",
            {"buffer": BinaryIO, "ctx": dict},
            script,
            {
                "_read_function": self.read,
                "BinaryIO": BinaryIO,
                "_BytesIO": io.BytesIO,
            },
        )

        return read_method

    def _create_encode_method(self):
        lines = []
        if self.encode is not None:
            lines.append("return _extern_encode(self, value, ctx)")
        else:
            lines.append("return value")

        method = self._create_method(
            "encode",
            {"value": int, "ctx": dict},
            lines,
            {"_extern_encode": self.encode},
        )
        return method

    def _create_decode_method(self):
        lines = []
        if self.decode is not None:
            lines.append("return _extern_decode(self, value, ctx)")
        else:
            lines.append("return value")

        method = self._create_method(
            "decode",
            {"value": int, "ctx": dict},
            lines,
            {"_extern_decode": self.decode},
        )
        return method

    def _create_deform_method(self):
        lines = []
        if self.deform is not None:
            lines.append("return _extern_deform(self, value, ctx)")
        else:
            lines.append("return value")

        method = self._create_method(
            "deform",
            {"value": bytes, "ctx": dict},
            lines,
            {"_extern_deform": self.deform},
        )
        return method

    def _create_reform_method(self):
        lines = []
        if self.reform is not None:
            lines.append("return _extern_reform(self, value, ctx)")
        else:
            lines.append("return value")

        method = self._create_method(
            "reform",
            {"value": bytes, "ctx": dict},
            lines,
            {"_extern_reform": self.reform},
        )
        return method

    def _create_method(
        self,
        name: str,
        args: dict,
        script: list,
        _globals: dict = None,
        _locals: dict = None,
    ):
        if _locals is None:
            _locals = {}

        if _globals is None:
            _globals = {}

        args_str = ", ".join(
            [f"{key}: {value.__name__}" for key, value in args.items()]
        )
        method_template = "def {}(self, {}):\n\t{}".format(
            name, args_str, "\n\t".join(script)
        )
        print(method_template)

        filename = f"{self.name}-{name}"
        bytecode = compile(method_template, filename, "exec")
        eval(bytecode, _globals, _locals)

        # inspect.getsource
        linecache_tuple = (
            len(method_template),
            None,
            method_template.splitlines(True),
            filename,
        )
        linecache.cache.setdefault(filename, linecache_tuple)

        return _locals[name]

    def build(self):
        init_script = self._create_init_script()
        init_method = self._create_method("__init__", self.args, init_script)
        self._cls_dict["__init__"] = init_method

        if self.variables is not None:
            setup_vars_script = self._create_setup_variables_script()
            setup_vars_method = self._create_method(
                "_setup_variables",
                {},
                setup_vars_script,
                {"_extern_variables": self.variables},
            )
            self._cls_dict["_setup_variables"] = setup_vars_method

        if self.encode is not None:
            self._cls_dict["encode"] = self._create_encode_method()
        if self.decode is not None:
            self._cls_dict["decode"] = self._create_decode_method()

        if self.deform is not None:
            self._cls_dict["deform"] = self._create_deform_method()
        if self.reform is not None:
            self._cls_dict["reform"] = self._create_reform_method()

        if self.write is not None:
            self._cls_dict["write"] = self._create_write_method()

        if self.read is not None:
            self._cls_dict["read"] = self._create_read_method()

        self._cls_dict["args"] = property(
            fget=self._create_method(
                "get_args",
                {},
                ["return ArgsProxy(self, _arg_names)"],
                {"ArgsProxy": ArgsProxy, "_arg_names": self.args.keys()},
            ),
            doc="Usage: self.args.[arg_name]",
        )

        self._cls_dict["vars"] = property(
            fget=self._create_method(
                "get_vars",
                {},
                ["return ArgsProxy(self, _var_names)"],
                {"ArgsProxy": ArgsProxy, "_var_names": self.variables.keys()},
            ),
            doc="Usage: self.vars.[var_name]",
        )

        self._cls_dict["get_builder"] = classmethod(
            self._create_method(
                "get_builder", {}, ["return _builder"], {"_builder": self}
            )
        )

        self._cls_dict["get_size"] = self._create_method(
            "get_size",
            {"ctx": dict},
            ["return _extern_get_size(self, ctx)"],
            {"_extern_get_size": self.size},
        )

        _new = type(self.name, tuple(), self._cls_dict)
        return _new

    def _init_template(self):
        builder = self.template.get_builder()
        if isinstance(self.template, type):
            # __init__ was not called yet,we must inherit
            # the args and the variables
            self.args.update(builder.args)
            self.variables.update(builder.variables)
        else:
            for arg in builder.args:
                self.variables[arg] = lambda self: getattr(builder.args, arg)

        if self.write is None:
            self.write = builder.write

        if self.read is None:
            self.read = builder.read

        if self.size is None:
            self.size = builder.size

        if self.encode is None:
            self.encode = builder.encode

        if self.decode is None:
            self.decode = builder.decode

        if self.deform is None:
            self.deform = builder.deform

        if self.reform is None:
            self.reform = builder.reform
