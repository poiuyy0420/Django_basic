from flask import jsonify
from flask import request
from flask import Blueprint
from flask import session
from models import Todo, db, Fcuser
import datetime
import requests
from . import api


def send_slack(msg):
    res = requests.post('https://hooks.slack.com/services/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', json={
            'text': msg
        }, headers={ 'Content-Type': 'application/json' })


@api.route('/todos/done', methods=['PUT'])
def todos_done():
    userid = session.get('userid', None)
    if not userid:
        return jsonify(), 401

    data = request.get_json()
    todo_id = data.get('todo_id')

    todo = Todo.query.filter_by(id=todo_id).first()
    fcuser = Fcuser.query.filter_by(userid=userid).first()

    if todo.fcuser_id != fcuser.id:
        return jsonify(), 400

    todo.status = 1

    db.session.commit()

    return jsonify()




@api.route('/todos', methods=['GET', 'POST', 'DELETE'])
def todos():

    userid = session.get('userid', 1)
    if not userid:
        return jsonify(), 401

    if request.method == 'POST':
        data = request.get_json()
        todo = Todo()
        todo.title = data.get('title')

        fcuser = Fcuser.query.filter_by(userid=userid).first()
        todo.fcuser_id = fcuser.id

        todo.due = data.get('due')
        todo.status = 0

        db.session.add(todo)
        db.session.commit()

        send_slack('TODO가 생성되었습니다')
        return jsonify(), 201

    elif request.method == 'GET':
        todos = Todo.query.filter_by(fcuser_id=userid)
        return jsonify([t.serialize for t in todos])

    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('todo_id')

        todo = Todo.query.filter_by(id=todo_id).first()
        
        db.session.delete(todo)
        db.session.commit()

        return jsonify(), 203
    
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

        send_slack('[%s] "%s" 할일을 만들었습니다.'%(str(datetime.datetime.now()), todo_name))
    
    elif cmd == 'list':
        todos = Todo.query.all()
        for idx, todo in enumerate(todos):
            ret_msg += '%d. %s (~ %s)\n'%(idx+1, todo.title, str(todo.tstamp))
        

    return ret_msg