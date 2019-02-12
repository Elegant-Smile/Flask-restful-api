from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'Build an Api'},
    'todo2': {'task': '??????'},
    'todo3': {'task': 'profit!'}
}


def abort_if_todo_doesnot_exists(todo_id):
    if todo_id not in TODOS:
        abort(404, message='todo {} does not exists.'.format(todo_id))


parse = reqparse.RequestParser()
parse.add_argument('task', type=str)


# Todo
# show a single todo item and lets you delete them
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnot_exists(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnot_exists(todo_id)
        del TODOS[todo_id]
        return TODOS

    def put(self, todo_id):
        args = parse.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parse.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = "todo%i" % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id]


##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')

if __name__ == '__main__':
    app.run(debug=True)
