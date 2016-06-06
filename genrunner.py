import functools
import threading
import json
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib2 import Path
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler


executor = ThreadPoolExecutor(5)


class GeneratorRunner(object):
    def __init__(self, func):
        self.stop_event = threading.Event()
        self.future = None
        self.func = func
        self.send = None

    def cancel(self):
        self.stop_event.set()

    def done(self):
        return self.stop_event.is_set()

    def running(self):
        if self.future:
            return self.future.running()
        else:
            return False

    def run(self, port=8000):
        loop = IOLoop.current()
        # Open the web browser after waiting a second for the server to start up.
        loop.call_later(1.0, webbrowser.open, 'http://localhost:%s' % port)
        self.send = init_server(self, port)
        loop.start()

    def start(self):
        """
        Run the generator function in a separate thread.

        """
        self.stop_event.clear()
        self.future = executor.submit(self._stoppable_run)
        self.future.add_done_callback(self._done_callback)

    def _stoppable_run(self):
        for _ in self.func(self.send):
            if self.stop_event.is_set():
                break
        self.stop_event.set()

    def _done_callback(self, future):
        # If there was an exception inside of self._stoppable_run, then it won't
        # be raised until you call future.result().
        try:
            future.result()
        except Exception as ex:
            self.send('Error: %s' % ex)


class WebSocketWriter:
    def __init__(self, sockets):
        self.sockets = sockets

    def send(self, obj):
        if isinstance(obj, basestring):
            obj = dict(type='console', value=obj)
        data = json.dumps(obj)
        for socket in self.sockets:
            socket.write_message(data)


class StartHandler(RequestHandler):
    def get(self):
        app = self.application
        if not app.runner.running():
            print('Starting...')
            app.runner.start()


class StopHandler(RequestHandler):
    def get(self):
        app = self.application
        if app.runner.running():
            print('Stopping...')
            app.runner.stop()


class StatusHandler(WebSocketHandler):
    def open(self):
        self.application.sockets.add(self)

    def on_close(self):
        self.application.sockets.remove(self)


class NoCacheStaticFileHandler(StaticFileHandler):
    def __init__(self, *args, **kwargs):
        static_dir = Path(__file__).parent / 'static'
        kwargs.update(
            path=str(static_dir.absolute()),
            default_filename='index.html',
        )
        super(NoCacheStaticFileHandler, self).__init__(*args, **kwargs)

    def set_extra_headers(self, path):
        self.set_header('Cache-control', 'no-cache')


def init_server(runner, port):
    settings = dict(
        debug=True,
        # autoreload=True,
    )
    app = Application([
        (r'/start/', StartHandler),
        (r'/stop/', StopHandler),
        (r'/status/', StatusHandler),
        (r'/(.*)', NoCacheStaticFileHandler),
    ], **settings)
    app.runner = runner
    app.sockets = set()
    ws_writer = WebSocketWriter(app.sockets)
    app.ws_writer = ws_writer

    app.listen(port)
    loop = IOLoop.current()

    # Make a send function that can be safely called from other threads.
    thread_safe_send = functools.partial(loop.add_callback, ws_writer.send)
    return thread_safe_send
