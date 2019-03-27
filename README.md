# Flask-restful-api
Flask-restful 用法练习总结笔记

[![Build Status](https://travis-ci.org/mgw2168/testdriven-app.svg?branch=master)](https://travis-ci.org/mgw2168/testdriven-app)


# Flask-Restful

## 一、安装：

```python
pip install flask-restful
```

完成安装后就可以引入常用类或模块

` from flask_restful import Api, Resource， reqparse, abort ` 

## 二、案例：

```python
from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# 定义一个全局字典
USER_LIST = {
    '1': {'name': 'Tom'},
    '2': {'name': 'Candy'}
}


class HelloWorld(Resource):

    def get(self):
        return USER_LIST

    def post(self):
        # 添加数据
        user_id = int(max(USER_LIST.keys())) + 1
        # 将 int 类型 user_id 转为 str
        user_id = '%i' % user_id
        USER_LIST[user_id] = {'name': request.form['name']}
        return USER_LIST


api.add_resource(HelloWorld, '/users')

if __name__ == '__main__':
    app.run(debug=True)

```

从案例可以看出，Restful 扩展通过 ` api.add_resource() ` 方法来添加路由，其中方法的第一个参数是视图类名（该类继承自Resource类），其函数成员函数定义了不同的 HTTP 请求方法的逻辑；第二个参数定义了 URL 路径。

运行上面案例，可以通过 ` http://127.0.0.1:5000/users ` 来访问，GET 请求时会显示全局变量 `USER_LIST` 中的内容，`POST` 请求时会在` USER_LIST` 中添加一项，并返回刚添加的项。如果在` POST` 请求中找不到 ` name` 字段，则返回` 400 Bad Request` 错误。由于类` UserList` 没有定义` put` 和` delete` 函数，所以在` PUT ` 或` DELETE` 请求时会返回` 405 Method Not Allowed` 错误。

另外，路由支持多路径：

` api.add_resource(HelloWorld, '/userlist', '/users')` 

这样访问 ` http://127.0.0.1:5000/userlist` 和 ` http://127.0.0.1:5000/users` 效果是一样的。

## 三、 带参数的请求

```python
class HelloWorld(Resource):

    def get(self, user_id):
        return USER_LIST[user_id]

    def put(self, user_id):
        USER_LIST[user_id] = {'name': request.form['name']}
        return USER_LIST[user_id]

    def delete(self, user_id):
        del USER_LIST[user_id]
        return USER_LIST

api.add_resource(HelloWorld, '/users/<user_id>', '/userlist')
```

## 四、参数解析

在 POST 和 PUT 请求中，直接访问 form 表单并验证的工作有些麻烦，Flask-RESTful 提供了 reqparse 库来简化：

```python
parse = reqparse.RequestParser()
parse.add_argument('name', type=str)


class HelloWorld(Resource):

    def put(self, user_id):
        # 使用 strict=True 调用 parse_args 能够确保当请求包含你的解析器中未定义的参数的时候会抛出一个异常。
        args = parse.parse_args(strict=True)
        USER_LIST[user_id] = {'name': args['name']}
        return USER_LIST[user_id]
    
api.add_resource(HelloWorld, '/users/<user_id>', '/userlist')
```

**`reqparse.RequestParser.parse_args()` 返回一个 Python 字典而不是一个自定义的数据结构。**

可以通过”parser.add_argument()”方法来定义form表单字段，并指定其类型（本例中是字符型str）。然后在PUT函数中，就可以调用”parser.parse_args()”来获取表单内容，并返回一个字典，该字典就包含了表单的内容。”parser.parse_args()”方法会自动验证数据类型，并在类型不匹配时，返回400错误。你还可以添加”strict”参数，如”parser.parse_args(strict=True)”，此时如果请求中出现未定义的参数，也会返回400错误。

## 五、类视图方法返回值

Flask-RESTful 支持视图方法多种类型的返回值。同 Flask 一样，你可以返回任一迭代器，它将会被转换成一个包含原始 Flask 响应对象的响应。Flask-RESTful 也支持使用多个返回值来设置响应代码和响应头，如下所示:

```python
class Todo1(Resource):
    def get(self):
        # Default to 200 OK
        return {'task': 'Hello world'}

class Todo2(Resource):
    def get(self):
        # Set the response code to 201
        return {'task': 'Hello world'}, 201

class Todo3(Resource):
    def get(self):
        # Set the response code to 201 and return custom headers
        return {'task': 'Hello world'}, 201, {'Etag': 'some-opaque-string'}
```

## 六、 数据格式化

默认情况下，在你的返回迭代中所有字段将会原样呈现。尽管当你刚刚处理 Python 数据结构的时候，觉得这是一个伟大的工作，但是当实际处理它们的时候，会觉得十分沮丧和枯燥。为了解决这个问题，Flask-RESTful 提供了 `fields` 模块和 [`marshal_with()`](http://www.pythondoc.com/Flask-RESTful/api.html#flask.ext.restful.marshal_with) 装饰器。类似 Django ORM 和 WTForm，你可以使用 fields 模块来在你的响应中格式化结构。

```python
from collections import OrderedDict
from flask_restful import fields, marshal_with

resource_fields = {
    'task':   fields.String,
    'uri':    fields.Url('todo_ep')
}

class TodoDao(object):
    def __init__(self, todo_id, task):
        self.todo_id = todo_id
        self.task = task

        # This field will not be sent in the response
        self.status = 'active'

class Todo(Resource):
    # 我们使用marshal_with来将输出的内容格式化
    @marshal_with(resource_fields)
    def get(self, **kwargs):
        return TodoDao(todo_id='my_todo', task='Remember the milk')
```

上面的例子接受一个 python 对象并准备将其序列化。[`marshal_with()`](http://www.pythondoc.com/Flask-RESTful/api.html#flask.ext.restful.marshal_with) 装饰器将会应用到由 `resource_fields` 描述的转换。从对象中提取的唯一字段是 `task`。`fields.Url` 域是一个特殊的域，它接受端点（endpoint）名称作为参数并且在响应中为该端点生成一个 URL。许多你需要的字段类型都已经包含在内。请参阅 `fields` 指南获取一个完整的列表。

### 完整案例

```python
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

```

#### 用法示例：

```python
# 获取列表：
http://127.0.0.1:5000/todos

# 获取单个
http://127.0.0.1:5000/todos/todo1
   
# 删除单个
http://127.0.0.1:5000/todos/todo1
        
# 增加一个新的任务
http://127.0.0.1:5000/todos/todo4
        
# 更新一个任务
http://127.0.0.1:5000/todos/todo3
```









