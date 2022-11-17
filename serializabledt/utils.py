import linecache


def create_method(
    name, filename, script, args=None, _globals=None, _locals=None
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
