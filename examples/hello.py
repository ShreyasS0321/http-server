from httpserver.server import add_route, run


def home():
    return "<h1>Home</h1><p>Welcome to the custom HTTP server.</p>"


def hello():
    return "<h1>Hello</h1>"


def about():
    return "<h1>About</h1><p>Built from scratch on raw TCP sockets, no framework.</p>"


add_route("/", "GET", home)
add_route("/hello", "GET", hello)
add_route("/about", "GET", about)


if __name__ == "__main__":
    run()
