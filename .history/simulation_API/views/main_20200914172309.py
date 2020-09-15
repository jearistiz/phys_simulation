"""This file manages all requests that are made to our app
"""
from simulation_API import app, templates 
from fastapi import Request

@app.get("/")