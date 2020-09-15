"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request

# Este decorador nos dice la ruta y el método de acceso a la aplicación
# En este caso, el método es get y la ruta es http://0.0.0.0/
@app.get("/")
async def index(request: Request):
    pass