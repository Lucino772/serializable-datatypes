from .utils import create_method


class TemplateBuilder:
    _setup_variables_method_name = "_setup_variables"

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

        setup_vars_method = create_method(
            self._setup_variables_method_name,
            f"{self._name}.{self._setup_variables_method_name}",
            script,
            _globals={"_extern_vars": self._variables},
        )
        return setup_vars_method

    def build(self):
        # Add __init__ & setup_vars method
        self._cls_dict["__init__"] = self._create_init_method()

        if self._variables is not None and len(self._variables) != 0:
            self._cls_dict[
                self._setup_variables_method_name
            ] = self._create_setup_vars_method()

        # Add write, read & get_size method
        self._cls_dict["write"] = self._write
        self._cls_dict["read"] = self._read
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
