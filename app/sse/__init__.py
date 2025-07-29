from queue import Queue
from threading import Lock
from flask import Blueprint, current_app, g
import json


def init_app(app):
    app.sse_channels = {}
    app.sse_lock = Lock()

    events_bp = Blueprint('events', __name__)

    @events_bp.route('/events')
    def events():
        empresa_id = g.user.empresa_id
        q = Queue()
        with app.sse_lock:
            app.sse_channels.setdefault(empresa_id, []).append(q)

        def gen():
            try:
                while True:
                    data = q.get()
                    yield f"data: {json.dumps(data)}\n\n"
            finally:
                with app.sse_lock:
                    app.sse_channels[empresa_id].remove(q)
        return app.response_class(gen(), mimetype='text/event-stream')

    app.register_blueprint(events_bp)


def publish_event(app, empresa_id, event):
    with app.sse_lock:
        queues = list(app.sse_channels.get(empresa_id, []))
    for q in queues:
        q.put(event)
