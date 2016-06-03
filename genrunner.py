import random
import time
import functools
import threading
import json
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib2 import Path
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado import gen
from tornado.websocket import WebSocketHandler


executor = ThreadPoolExecutor(5)


class GeneratorRunner(object):
    def __init__(self, func):
        self.stop_event = threading.Event()
        self.future = None
        self.func = func

    def cancel(self):
        self.stop_event.set()

    def done(self):
        return self.stop_event.is_set()

    def run(self):
        """
        Run the generator function synchronously.

        """
        def noop(*args, **kwargs):
            pass
        for _ in self.func(noop):
            pass

    def run_web(self, port=8000):
        loop = IOLoop.current()
        # Open the web browser after waiting a second for the server to start up.
        loop.call_later(1.0, webbrowser.open, 'http://localhost:%s' % port)
        start_server()

    def start(self):
        """
        Run the generator function in a separate thread.

        """
        self.future = executor.submit(self._stoppable_run)
        self.add_done_callback(self._done_callback)

    def add_done_callback(self, callback):
        if self.future:
            self.future.add_done_callback(callback)

    def _stoppable_run(self):
        for obj in self.func():
            if self.stop_event.is_set():
                break
            self.log(obj)
        self.stop_event.set()

    def _done_callback(self, future):
        # If there was an exception inside of self._stoppable_run, then it won't
        # be raised until you call future.result().
        try:
            future.result()
        except Exception as ex:
            self.log('Error: %s' % ex)


class WebSocketLoggingTask(GeneratorTask):
    def __init__(self, func, logger):
        super(WebSocketLoggingTask, self).__init__(func)
        loop = IOLoop.current()
        self.log = functools.partial(loop.add_callback, logger.info)


# class MainHandler(RequestHandler):
#     def get(self):
#         self.render('index.html')


class StartHandler(RequestHandler):
    def get(self):
        count = int(self.get_query_argument('count', 5))
        app = self.application
        if not app.current_task:
            app.current_task = WebSocketLoggingTask(
                functools.partial(generate_chinese_characters, count),
                app.logger)
            app.current_task.start()
            self.write('Started background task')
            # Set app.current_task to None when task finishes.
            def done_callback(future):
                app.current_task = None
            app.current_task.add_done_callback(done_callback)


class StopHandler(RequestHandler):
    def get(self):
        app = self.application
        if app.current_task:
            app.current_task.cancel()
            self.write('Stopping background task...')
            app.logger.info('Stopping background task...')


class StatusHandler(WebSocketHandler):
    def open(self):
        print('WebSocket opened')
        self.application.sockets.add(self)

    def on_close(self):
        print('WebSocket closed')
        self.application.sockets.remove(self)


class WebSocketWriter:
    def __init__(self, sockets):
        self.sockets = sockets

    def send(self, obj):
        if isinstance(obj, basestring):
            obj = dict(type='message', value=obj)
        data = json.dumps(obj)
        for socket in self.sockets:
            socket.write_message(data)


class NoCacheStaticFileHandler(StaticFileHandler):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            path=str(Path(__file__).parent.absolute()),
            default_filename='index.html',
        )
        super(NoCacheStaticFileHandler, self).__init__(*args, **kwargs)

    def set_extra_headers(self, path):
        self.set_header('Cache-control', 'no-cache')


def start_server(port):
    settings = dict(
        debug=True,
        autoreload=True,
    )
    app = Application([
        (r'/start/', StartHandler),
        (r'/stop/', StopHandler),
        (r'/status/', StatusHandler),
        (r'/(.*)', NoCacheStaticFileHandler),
    ], **settings)
    app.sockets = set()
    app.current_task = None
    app.ws_writer = WebSocketWriter(app.sockets)

    app.listen(port)
    loop = IOLoop.current()
    loop.start()
