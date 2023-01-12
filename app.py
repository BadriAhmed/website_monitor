from fastapi import FastAPI
from uvicorn import Server, Config

from configuration.config import ServerConfig
from routers.website_monitor import website_monitor_router

app = FastAPI()
app.include_router(website_monitor_router)

if __name__ == '__main__':
    # Setting up uvicorn server
    server = Server(Config(app=app, host=ServerConfig.HOST, port=ServerConfig.PORT))
    server.run()
