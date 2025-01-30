from flask import Flask
from time import sleep

app = Flask(__name__)

def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)


@app.route("/")
def root():
    return {"Hello": "World"}

@app.route("/cpu-bound")
def cpu_bound():
    return {"Fibonacci": fibonacci(30)}

@app.route("/io-bound")
def io_bound():
    sleep(.5)
    return {"Sleep": 0.5}

