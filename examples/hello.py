from httpserver.server import add_route, run


def home(request):
    return "<h1>Home</h1><p>Welcome to the custom HTTP server.</p>"


def hello(request):
    name = request.query_params.get("name", "stranger")
    agent = request.headers.get("user-agent", "unknown")
    return f"<h1>Hello {name}</h1><p>You asked for {request.path} using {agent}.</p>"


def about(request):
    return "<h1>About</h1><p>Built from scratch on raw TCP sockets, no framework.</p>"


add_route("/", "GET", home)
add_route("/hello", "GET", hello)
add_route("/about", "GET", about)


if __name__ == "__main__":
    run()
