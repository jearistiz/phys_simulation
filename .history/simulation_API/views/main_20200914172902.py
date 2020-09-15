"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request

# This decorator tells us the route and method
# in this case route='domain.com/' and method='get'
@app.get("/")
# La definición async es la que hace a FastAPI realmetn
async def index(request: Request):
    return {"message": "Hello World"}