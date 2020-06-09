import asyncio
from aiohttp import web
import logging
import json
from aiohttp import web
from utils import validate_payload, CommentListConverter, PredictionConverter
from worker import predict_probability


class SiteHandler:
    def __init__(self, conf, executor, base_root):
        self._conf = conf
        self._executor = executor
        self._root = base_root
        self._loop = asyncio.get_event_loop()

    async def index(self, request):
        path = str(self._root / 'static' / 'index.html')
        return web.FileResponse(path)

    async def moderate(self, request):
        raw_data = await request.read()
        logging.debug(raw_data)
        data = validate_payload(raw_data, CommentListConverter)

        features = [d['comment_text'] for d in data]
        run = self._loop.run_in_executor
        results = await run(self._executor, predict_probability, features)

        payload = [{
            'toxic': i[0],
            'severe_toxic': i[1],
            'obscene': i[2],
            'insult': i[3],
            'identity_hate': i[4]
        } for i in results]
        return web.json_response(payload)
