from flask import Flask, session, abort, redirect, request

app = Flask("Composite Service")



if __name__ == "__main__":
    host = int(os.environ.get("HOST", "0.0.0.0"))
    port = int(os.environ.get("PORT", 5000))
    app.run(host, port)