from flask import jsonify
from flask import request
from flask import Blueprint
from models import Todo, db
import requests
from . import api


@api.route('/todos', methods=['GET', 'POST'])
def todos():
    if request.method == 'POST':
        res = requests.post('https://hooks.slack.com/services/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', json={
            'text': 'Hello world'
        }, headers={ 'Content-Type': 'application/json' })
    elif request.method == 'GET':
        pass


    data = request.get_json()
    return jsonify(data)



@api.route('/slack/todos', methods=['POST'])
def slack_todos():
    # 명령어 구분 띄어쓰기
    # /flasktodo create aaaa
    # /flasktodo list
    res = request.form['text'].split(' ')
    # 첫번째 변수는 cmd, 나머지는 *args
    cmd, *args = res

    ret_msg = ''
    if cmd == 'create':
        todo_name = args[0]

        todo = Todo()
        todo.title = todo_name

        db.session.add(todo)
        db.session.commit()
        ret_msg = 'todo가 생성되었습니다'

    elif cmd == 'list':
        todos = Todo.query.all()
        for idx, todo in enumerate(todos):
            ret_msg += '%d. %s (~ %s)\n'%(idx+1, todo.title, str(todo.tstamp))
        

    return ret_msg