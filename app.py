import time
import redis
from flask import Flask, request,render_template, redirect

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import jsonify

app = Flask(__name__,static_folder='static')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
db = SQLAlchemy(app)
cache = redis.Redis(host='redis', port=6379)  


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    checked = db.Column(db.Boolean, default=False) 

def get_hit_count():
    with app.app_context():
        key = 'hits:{}'.format(time.strftime('%Y-%m-%d'))
        
        retry = 10
        while True:
            try:
                count = cache.incr(key)
                cache.expire(key, 86400)
                return count
            except redis.exceptions.ConnectionError as exc:
                if retry == 0:
                    raise exc
                retry -= 1
                time.sleep(0.5)

@app.route('/')
def initial():
    count = get_hit_count()
    todos = TodoList.query.all()
    return render_template('index.html', count=count, todos=todos)

@app.route('/add', methods=['POST'])
def add_todo():  
    content = request.form['content']
    new_todo = TodoList(content=content)

    try:
        db.session.add(new_todo)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue adding your task'

@app.route('/update_checkbox', methods=['POST'])
def update_checkbox():
    data = request.get_json()  
    try:
        todo_id = data.get('todoId')
        is_checked = data.get('isChecked')

        todo = TodoList.query.get(todo_id)
        todo.checked = is_checked

        db.session.commit()  
        return jsonify({'success': True}) 
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
        app.run(host='0.0.0.0', port=8081,debug=True,threaded=True)
    