import sys

from httpserver.router import add_route


def home(request):
    return "<h1>Home</h1>"


def hello(request):
    name = request.query_params.get("name", "stranger")
    return f"Hello {name}"


def echo_agent(request):
    return request.headers.get("user-agent", "unknown")


def boom(request):
    raise ValueError("handler blew up on purpose")


add_route("/", "GET", home)
add_route("/hello", "GET", hello)
add_route("/agent", "GET", echo_agent)
add_route("/boom", "GET", boom)


def main():
    mode = sys.argv[1]
    port = int(sys.argv[2])
    if mode == "threaded":
        from httpserver.server import run
    else:
        from httpserver.server_async import run
    run(port=port)


if __name__ == "__main__":
    main()
