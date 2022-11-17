import io

from .utils import create_method


class TransformerBuilder:
    def __init__(self, name, write, read, size, args=None, variables=None):
        self._name = name
        self._write = write
        self._read = read
        self._size = size
        self._args = args
        self._variables = variables

        self._cls_dict = {}

    def _create_init_method(self):
        script = []

        # Initialize args & variables from template passed as paramaeter
        script.append("self._template = template")
        script.append("_builder = template.get_builder()")
        script.append("if _builder._args is not None:")
        script.append("\tfor argname in _builder._args.keys():")
        script.append("\t\tsetattr(self, argname, getattr(template, argname))")
        script.append("if _builder._variables is not None:")
        script.append("\tfor varname in _builder._variables.keys():")
        script.append("\t\tsetattr(self, varname, getattr(template, varname))")
        script.append("")

        # Initialize each arg
        if self._args is not None:
            for argname in self._args.keys():
                script.append(f"self.{argname} = {argname}")

        # Initialize variables setup
        if self._variables is not None and len(self._variables) != 0:
            script.append(f"self.{self._setup_variables_method_name}()")

        init_method = create_method(
            "__init__",
            f"{self._name}.__init__",
            script,
            ["template"]
            + (list(self._args.keys()) if self._args is not None else []),
        )
        return init_method

    def _create_setup_vars_method(self):
        script = []

        # Initialize variables
        for varname, varval in self.variables.items():
            if callable(varval):
                script.append(
                    f"self.{varname} = _extern_vars['{varname}'](self)"
                )
            else:
                script.append(f"self.{varname} = _extern_vars['{varname}']")

        setup_vars_method = create_method(
            self._setup_variables_method_name,
            f"{self.name}.{self._setup_variables_method_name}",
            script,
            _globals={"_extern_vars": self._variables},
        )
        return setup_vars_method

    def _create_write_method(self):
        script = []
        script.append("with _BytesIO() as _buffer:")
        script.append("\tself._template.write(_buffer, value, ctx)")
        script.append("\t_bytes = _buffer.getvalue()")
        script.append(
            "return buffer.write(_extern_transform_write(self, _bytes, ctx))"
        )

        write_method = create_method(
            "write",
            f"{self._name}.write",
            script,
            ["buffer", "value", "ctx"],
            _globals={
                "_extern_transform_write": self._write,
                "_BytesIO": io.BytesIO,
            },
        )
        return write_method

    def _create_read_method(self):
        script = []
        script.append(
            "_bytes = _extern_transform_read(self, buffer.read(self.get_size(ctx)), ctx)"
        )
        script.append("with _BytesIO(_bytes) as _buffer:")
        script.append("\treturn self._template.read(_buffer, ctx)")

        read_method = create_method(
            "read",
            f"{self._name}.read",
            script,
            ["buffer", "ctx"],
            _globals={
                "_extern_transform_read": self._read,
                "_BytesIO": io.BytesIO,
            },
        )
        return read_method

    def build(self):
        # Add __init__ & setup_vars method
        self._cls_dict["__init__"] = self._create_init_method()

        if self._variables is not None and len(self._variables) != 0:
            self._cls_dict[
                self._setup_variables_method_name
            ] = self._create_setup_vars_method()

        # Add write, read & get_size method
        self._cls_dict["write"] = self._create_write_method()
        self._cls_dict["read"] = self._create_read_method()
        self._cls_dict["get_size"] = self._size

        # Add get_builder class method
        self._cls_dict["get_builder"] = classmethod(
            create_method(
                "get_builder",
                f"{self._name}.get_builder",
                ["return _builder"],
                _globals={"_builder": self},
            )
        )

        _new = type(self._name, tuple(), self._cls_dict)
        return _new
