from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

CAPACITY = 20

INITIAL_DATA = [
    19, 15, 29, 25, 33, 35, 49,
    42, 50, 55, 62, 66, 77, 80
]


class FixedSizeQueue:

    def __init__(self, capacity=20):
        self.capacity = capacity
        self.data = [None] * capacity
        self.front_index = 0
        self.count = 0

    def init(self, values=None):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        if values is not None:
            for value in values:
                self.push(value)

        return self.dump()

    def push(self, value):
        if self.is_full():
            raise ValueError("Queue is full")

        rear_index = (
            self.front_index + self.count
        ) % self.capacity

        self.data[rear_index] = value
        self.count += 1

        return self.dump()

    def pop(self):
        if self.is_empty():
            raise ValueError("Queue is empty")

        removed_value = self.data[self.front_index]
        self.data[self.front_index] = None

        self.front_index = (
            self.front_index + 1
        ) % self.capacity

        self.count -= 1

        if self.count == 0:
            self.front_index = 0

        return removed_value

    def size(self):
        return self.count

    def is_full(self):
        return self.count == self.capacity

    def is_empty(self):
        return self.count == 0

    def state(self):
        return {
            "full": self.is_full(),
            "empty": self.is_empty()
        }

    def front(self):
        if self.is_empty():
            return None

        return self.data[self.front_index]

    def clear(self):
        self.data = [None] * self.capacity
        self.front_index = 0
        self.count = 0

        return self.dump()

    def index(self, value):
        items = self.dump()

        for i, item in enumerate(items):
            if item == value:
                return i

        return -1

    def value_count(self, value):
        items = self.dump()

        return sum(
            1 for item in items
            if item == value
        )

    def contains(self, value):
        return self.index(value) != -1

    def dump(self):
        result = []

        for i in range(self.count):
            index = (
                self.front_index + i
            ) % self.capacity

            result.append(self.data[index])

        return result

    def status(self):
        return {
            "capacity": self.capacity,
            "size": self.size(),
            "full": self.is_full(),
            "empty": self.is_empty(),
            "front": self.front(),
            "items": self.dump()
        }


queue = FixedSizeQueue(CAPACITY)
queue.init(INITIAL_DATA)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Fixed-Size Queue Server",
        "status": "running",
        "capacity": CAPACITY
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/queue", methods=["GET", "POST", "OPTIONS"])
def queue_api():

    if request.method == "OPTIONS":
        return "", 204

    if request.method == "GET":
        return jsonify({
            "ok": True,
            "status": queue.status()
        })

    payload = request.get_json(silent=True) or {}
    action = payload.get("action", "status")

    try:
        if action == "init":
            values = payload.get("values", INITIAL_DATA)
            result = queue.init(values)
            message = "Queue initialized"

        elif action == "push":
            value = payload.get("value")

            if value is None:
                raise ValueError("Введите значение")

            result = queue.push(value)
            message = "Push completed"

        elif action == "pop":
            result = queue.pop()
            message = "Pop completed"

        elif action == "size":
            result = queue.size()
            message = "Current queue size"

        elif action == "state":
            result = queue.state()
            message = "Queue state checked"

        elif action == "front":
            result = queue.front()
            message = "Front value checked"

        elif action == "clear":
            result = queue.clear()
            message = "Queue cleared"

        elif action == "index":
            value = payload.get("value")

            if value is None:
                raise ValueError("Введите значение для поиска")

            result = queue.index(value)
            message = "Index search completed"

        elif action == "count":
            value = payload.get("value")

            if value is None:
                raise ValueError("Введите значение для подсчёта")

            result = queue.value_count(value)
            message = "Value count completed"

        elif action == "contains":
            value = payload.get("value")

            if value is None:
                raise ValueError("Введите значение для проверки")

            result = queue.contains(value)
            message = "Contains check completed"

        elif action == "dump":
            result = queue.dump()
            message = "Queue dump completed"

        else:
            raise ValueError("Unknown action: " + action)

        return jsonify({
            "ok": True,
            "action": action,
            "message": message,
            "result": result,
            "status": queue.status()
        })

    except (ValueError, TypeError) as error:
        return jsonify({
            "ok": False,
            "action": action,
            "error": str(error),
            "status": queue.status()
        }), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port
    )
