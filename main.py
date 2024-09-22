from app import app
import asyncio

server = app.WebApp()

if __name__ == "__main__":
    
    server.run("localhost",3030)