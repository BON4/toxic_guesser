from concurrent.futures import ProcessPoolExecutor
from formencode import Schema, validators as v
import asyncio
import logging
from worker import warm
from constants import *
import yaml
import json
from exeptions import JsonValidaitonError, TooMuchCommentsError
import formencode
import signal

# Formencode forms


class RequiredString(v.UnicodeString):
    not_empty = True


class RequiredFloat(v.Number):
    not_empty = True


class RequiredSet(v.Set):
    not_empty = True


class ListCommentMapFields(v.FormValidator):
    _fields_mapping = {'comments': [
        {'comment_text': 'comment_text'}
    ]
    }

    def _to_python(self, fields, state):
        result = {}
        result_list = []
        for list_val in self._fields_mapping:
            if len(fields[list_val]) > MAX_COMMENTS:
                raise TooMuchCommentsError
            else:
                for comment in fields[list_val]:
                    for key, value in comment.items():
                        result[key] = comment[key]
                        result_list.append(result)
                    result = {}
        return result_list


class PredictionsMapFields(v.FormValidator):
    _fields_mapping = [{
        'toxic': 'toxic',
        'severe_toxic': 'severe_toxic',
        'obscene': 'obscene',
        'insult': 'insult',
        'identity_hate': 'identity_hate',
    }
    ]

    def _to_python(self, fields, state):
        result = {}
        for key, value in self._fields_mapping.iteritems():
            result[value] = fields[key]
        return result


class CommentListConverter(Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    comments = RequiredSet
    chained_validators = [ListCommentMapFields]


class PredictionConverter(Schema):
    allow_extra_fields = True
    filter_extra_fields = True

    predict_toxic = RequiredFloat
    predict_severe_toxic = RequiredFloat
    predict_obscene = RequiredFloat
    predict_insult = RequiredFloat
    predict_identity_hate = RequiredFloat

    chained_validators = [PredictionsMapFields]


def validate_payload(raw_payload, converter):
    payload = raw_payload.decode('UTF-8')
    try:
        parsed = json.loads(payload)
    except ValueError:
        raise JsonValidaitonError('Error in json serializer')
    try:
        data = converter.to_python(parsed)
    except formencode.Invalid as e:
        raise JsonValidaitonError(e)
    return data

# Load config from yaml file


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    # TODO: add config validation
    return data


async def setup_executor(app, conf):
    workers = conf['max_workers_executor']
    path = BASE_ROOT / conf['model_path']
    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(max_workers=workers)
    fs = [loop.run_in_executor(
        executor, warm, path) for i in range(0, workers)]
    await asyncio.gather(*fs)  # gather for Futures wait for Tasks

    async def close_executor(app):
        # TODO: figureout timeout for shutdown
        await asyncio.sleep(5)
        executor.shutdown(wait=True)

    # Setup signal to end executor process on closing app
    app.on_cleanup.append(close_executor)

    app['executor'] = executor
    return executor
