from fastapi import FastAPI
from time import sleep
import asyncio

app = FastAPI()


def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/cpu-bound")
async def cpu_bound():
    return {"Fibonacci": fibonacci(30)}

@app.get("/io-bound")
async def io_bound():
    value = await asyncio.sleep(0.5, result=0.5)
    return {"Sleep": value}


