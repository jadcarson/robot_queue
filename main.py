from flask import Flask, _app_ctx_stack, jsonify, request
from flask_cors import CORS
from sqlalchemy import func
from sqlalchemy.orm import scoped_session
import models
from database import Session, engine
import sqlite3

models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
CORS(app)
app.session = scoped_session(Session, scopefunc=_app_ctx_stack.__ident_func__)

# Update Tasks Route requires a body with a json object with the following parameters:
# task_name, priority_level (integer, lower the higher priority), and length (integer like number of seconds)
@app.route('/update_tasks', methods=['POST'])
def update():
    try:
        new_task = request.json
        task = models.Tasks()
        task.task_name = new_task['task_name']
        task.priority_level = new_task['priority_level']
        task.length = new_task['length']
        app.session.add(task)
        app.session.commit()
        return ({
            'task_updated':True
        })
    except:
        return {
            'task_updated': False
        }

# this route is a get request that returns all the tasks
@app.route('/task_list', methods=['GET'])
def task_list():  
    record_dict = {}
    records = app.session.query(models.Tasks).all()
    for record in records:
        record_dict[record.id] = {
            'task_name':record.task_name,
            'priority_level':record.priority_level,
            'task_length':record.length
        }
    return record_dict

# this route adds a task to the queue.  The body requires a json object with:
# task_id
@app.route('/add_to_queue', methods=['POST'])
def add_to_queue():
    try:
        new_queue_task = request.json
        queue = models.PriorityQueue()
        queue.status = 'O'
        queue.task_id = new_queue_task['task_id']
        app.session.add(queue)
        app.session.commit()
        return {
            'queue_task_added':True
        }
    except:
        return {'queue_task_added': False}

# This gets the next queue.  it requires the robot to put it's id number in the request string
# If it doesn't find an open task, it returns saying no task.  If it finds one, it returns with the task.
# The while loop is there so that even though we are using transactions, if it finds an open task but the task isn't
# open by the time it checks it out, it'll try finding another open task until it can check one out or there are no
# open tasks.
@app.route('/get_next_queue/<robot_id>', methods=['GET'])
def get_next_queue(robot_id):
    try:
        con = sqlite3.connect('diligent.db')
        cur = con.cursor()
        while True:
            cur.execute("BEGIN")
            cur.execute("SELECT * FROM priority_queue")
            cur.execute("""SELECT priority_queue.id, tasks.id, task_name, priority_level, min(length) FROM tasks INNER JOIN priority_queue ON 
                        tasks.id = priority_queue.task_id where status = 'O' AND priority_level = (SELECT min(priority_level) 
                        from tasks INNER JOIN priority_queue ON tasks.id = priority_queue.task_id WHERE status='O')""")
            open_task = cur.fetchone()
            if not open_task[0]:
                con.close()
                return (
                    {'has_task': False, 
                    'task':None,
                    'error': False
                    }
                )

            cur.execute("""UPDATE priority_queue SET status='R', robot_id = ? WHERE id = ? AND status='O'""", (robot_id,open_task[0]))
            updated_queue = cur.rowcount
            if updated_queue:
                con.commit()
                con.close()
                return (
                    {
                        'has_task': True,
                        'task':{
                            'name':open_task[2],
                            'task_id':open_task[1],
                            'queue_id':open_task[0]
                        },
                        'error':False
                    }
                )
    except:
        return {
            'has_task':False,
            'task': None,
            'error': True
        }

# this requires a json with queue_id
@app.route('/finish_task', methods=['POST'])
def finish_task():
    try:
        finished_task = request.json
        con = sqlite3.connect('diligent.db')
        cur = con.cursor()
        cur.execute("""UPDATE priority_queue SET status='C' WHERE id = ?""", (finished_task['queue_id'],))
        con.commit()
        con.close()
        return {'task_checked_in':True}
    except:
        return {'task_checked_in': False}

#this just gets the whole queue
@app.route('/get_queue', methods=['GET'])
def get_queue():
    queue_dict = {}
    queue = app.session.query(models.PriorityQueue).all()
    for record in queue:
        queue_dict[record.id] = {
            'task_id':record.task_id,
            'robot_id':record.robot_id,
            'status':record.status
        }
    return queue_dict

if __name__ == "__main__":
    app.run(debug=True)





