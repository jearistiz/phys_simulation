"""This file will do background tasks e.g. the simulation
"""
import time
from datetime import datetime

from fastapi import Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from simulation_API import app, templates


def _run_task(name: str, id: int):
    time.sleep(3)
    with open("tasks_out.txt", mode="a") as file:
        now = datetime.now()