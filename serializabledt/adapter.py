from .utils import create_method


class AdapterBuilder:
    def __init__(
        self, name, template, encode, decode, args=None, variables=None
    ):
        self._name = name
        self._template = template
        self._encode = encode
        self._decode = decode

        self._args = args
        self._variables = variables

        self._cls_dict = {}

    def _create_init_method(self):
        script = []

        # Initialize args & variables from given template
        template_builder = self._template.get_builder()
        if template_builder._args is not None:
            for argname in template_builder._args.keys():
                script.append(f"self.{argname} = _extern_template.{argname}")

        if template_builder._variables is not None:
            for varname in template_builder._variables.keys():
                script.append(f"self.{varname} = _extern_template.{varname}")

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
            self._args.keys() if self._args is not None else [],
            _globals={"_extern_template": self._template},
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
            f"{self._name}.{self._setup_variables_method_name}",
            script,
            _globals={"_extern_vars": self._variables},
        )
        return setup_vars_method

    def _wrap_template_write(self):
        script = []
        script.append("encoded_value = _extern_encode(self, value, ctx)")
        script.append("return _extern_write(buffer, encoded_value, ctx)")

        write_method = create_method(
            "write",
            f"{self._name}.write",
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

        read_method = create_method(
            "read",
            f"{self._name}.read",
            script,
            ["buffer", "ctx"],
            _globals={
                "_extern_decode": self._decode,
                "_extern_read": self._template.read,
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
        self._cls_dict["write"] = self._wrap_template_write()
        self._cls_dict["read"] = self._wrap_template_read()
        self._cls_dict["get_size"] = self._template.get_size

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
