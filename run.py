"""This file sets up the uvicorn server for us 
"""
import uvicorn
from config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run("simulation_api:app", host=HOST, port=int(PORT),
                reload=True, debug=True, workers=1)