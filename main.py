import logging
import asyncio
from constants import *
from routes import setup_routes
from handlers import SiteHandler
from utils import setup_executor, load_config
from aiohttp import web


async def init(loop, conf):
    app = web.Application(loop=loop)
    executor = await setup_executor(app, conf)
    handler = SiteHandler(conf, executor, BASE_ROOT)
    setup_routes(app, handler, BASE_ROOT)
    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    conf = load_config(BASE_ROOT / 'config' / 'config.yml')
    app = loop.run_until_complete(init(loop, conf))
    host = conf['host']
    port = conf['port']
    web.run_app(app, host=host, port=port)

if __name__ == "__main__":
    main()