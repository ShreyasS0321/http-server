handlers = {}
path_dict = {}


def add_route(path, method, function) -> None:
    handlers[(path, method)] = function

    if path not in path_dict:
        path_dict[path] = set()
    path_dict[path].add(method)
