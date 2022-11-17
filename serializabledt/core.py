import io
import linecache


class _BaseTemplate:
    _setup_variables_method_name = "_setup_variables"

    def __init__(self, name, args=None, variables=None) -> None:
        self._name = name
        self._args = args
        self._variables = variables

    def _get_method_filename(self, name):
        return f"{self._name}.{name}"

    def create_method(
        self, name, filename, script, args=None, _globals=None, _locals=None
    ):
        if _locals is None:
            _locals = {}

        if _globals is None:
            _globals = {}

        if args is None:
            args = []

        if len(script) == 0:
            script.append("pass")

        if len(args) > 0:
            code = "def {}(self, {}):\n\t{}".format(
                name, ", ".join(args), "\n\t".join(script)
            )
        else:
            code = "def {}(self):\n\t{}".format(name, "\n\t".join(script))

        bytecode = compile(code, filename, "exec")
        eval(bytecode, _globals, _locals)

        # inspect.getsource
        linecache_tuple = (
            len(code),
            None,
            code.splitlines(True),
            filename,
        )
        linecache.cache.setdefault(filename, linecache_tuple)

        return _locals[name]

    def _get_init_script(self):
        script = []

        # Initialize each arg
        if self._args is not None:
            for argname in self._args.keys():
                script.append(f"self.{argname} = {argname}")

        # Initialize variables setup
        if self._variables is not None and len(self._variables) != 0:
            script.append(f"self.{self._setup_variables_method_name}()")

        return script

    def _create_init_method(self):
        init_script = self._get_init_script()

        init_method = self.create_method(
            "__init__",
            self._get_method_filename("__init__"),
            init_script,
            self._args.keys() if self._args is not None else None,
        )
        return init_method

    def _create_setup_vars_method(self):
        script = []

        # Initialize variables
        for varname, varval in self._variables.items():
            if callable(varval):
                script.append(
                    f"self.{varname} = _extern_vars['{varname}'](self)"
                )
            else:
                script.append(f"self.{varname} = _extern_vars['{varname}']")

        setup_vars_method = self.create_method(
            self._setup_variables_method_name,
            self._get_method_filename(self._setup_variables_method_name),
            script,
            _globals={"_extern_vars": self._variables},
        )
        return setup_vars_method

    def _add_methods(self, cls_dict):
        pass

    def build(self):
        _cls_dict = {}

        # Add __init__ & setup_vars method
        _cls_dict["__init__"] = self._create_init_method()

        if self._variables is not None and len(self._variables) != 0:
            _cls_dict[
                self._setup_variables_method_name
            ] = self._create_setup_vars_method()

        # Add other methods
        self._add_methods(_cls_dict)

        # Add get_builder class method
        _cls_dict["get_builder"] = classmethod(
            self.create_method(
                "get_builder",
                self._get_method_filename("get_builder"),
                ["return _builder"],
                _globals={"_builder": self},
            )
        )

        _new = type(self._name, tuple(), _cls_dict)
        return _new


class TemplateBuilder(_BaseTemplate):
    def __init__(self, name, write, read, size, args=None, variables=None):
        super().__init__(name, args, variables)
        self._write = write
        self._read = read
        self._size = size

    def _add_methods(self, cls_dict):
        cls_dict["write"] = self._write
        cls_dict["read"] = self._read
        cls_dict["get_size"] = self._size


class AdapterBuilder(_BaseTemplate):
    def __init__(
        self, name, template, encode, decode, args=None, variables=None
    ):
        super().__init__(name, args, variables)
        self._template = template
        self._encode = encode
        self._decode = decode

    def _get_init_script(self):
        script = []

        # Initialize args & variables from given template
        template_builder = self._template.get_builder()
        if template_builder._args is not None:
            for argname in template_builder._args.keys():
                script.append(f"self.{argname} = _extern_template.{argname}")

        if template_builder._variables is not None:
            for varname in template_builder._variables.keys():
                script.append(f"self.{varname} = _extern_template.{varname}")

        return script + super()._get_init_script()

    def _create_init_method(self):
        init_script = self._get_init_script()

        init_method = self.create_method(
            "__init__",
            self._get_method_filename("__init__"),
            init_script,
            self._args.keys() if self._args is not None else None,
            _globals={"_extern_templates": self._template},
        )
        return init_method

    def _wrap_template_write(self):
        script = []
        script.append("encoded_value = _extern_encode(self, value, ctx)")
        script.append("return _extern_write(buffer, encoded_value, ctx)")

        write_method = self.create_method(
            "write",
            self._get_method_filename("write"),
            script,
            ["buffer", "value", "ctx"],
            _globals={
                "_extern_encode": self._encode,
                "_extern_write": self._template.write,
            },
        )
        return write_method

    def _wrap_template_read(self):
        script = []
        script.append("encoded_value = _extern_read(buffer, ctx)")
        script.append("return _extern_decode(self, encoded_value, ctx)")

        read_method = self.create_method(
            "read",
            self._get_method_filename("read"),
            script,
            ["buffer", "ctx"],
            _globals={
                "_extern_decode": self._decode,
                "_extern_read": self._template.read,
            },
        )
        return read_method

    def _add_methods(self, cls_dict):
        # Add write, read & get_size method
        cls_dict["write"] = self._wrap_template_write()
        cls_dict["read"] = self._wrap_template_read()
        cls_dict["get_size"] = self._template.get_size


class TransformerBuilder(_BaseTemplate):
    def __init__(self, name, write, read, size, args=None, variables=None):
        super().__init__(name, args, variables)
        self._write = write
        self._read = read
        self._size = size

    def _get_init_script(self):
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

        return script + super()._get_init_script()

    def _create_init_method(self):
        script = self._get_init_script()
        init_method = self.create_method(
            "__init__",
            self._get_method_filename("__init__"),
            script,
            ["template"]
            + (list(self._args.keys()) if self._args is not None else []),
        )
        return init_method

    def _create_write_method(self):
        script = []
        script.append("with _BytesIO() as _buffer:")
        script.append("\tself._template.write(_buffer, value, ctx)")
        script.append("\t_bytes = _buffer.getvalue()")
        script.append(
            "return buffer.write(_extern_transform_write(self, _bytes, ctx))"
        )

        write_method = self.create_method(
            "write",
            self._get_method_filename("write"),
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

        read_method = self.create_method(
            "read",
            self._get_method_filename("read"),
            script,
            ["buffer", "ctx"],
            _globals={
                "_extern_transform_read": self._read,
                "_BytesIO": io.BytesIO,
            },
        )
        return read_method

    def _add_methods(self, cls_dict):
        # Add write, read & get_size method
        cls_dict["write"] = self._create_write_method()
        cls_dict["read"] = self._create_read_method()
        cls_dict["get_size"] = self._size
