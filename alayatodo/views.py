from alayatodo import app
import json
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    jsonify
    )

TODO_STATUS_COL=3

@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        #readme = "".join(l.decode('utf-8') for l in f)
        readme = "".join(l for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    cur = g.db.execute(sql % (username, password))
    user = cur.fetchone()
    if user:
        session['user'] = dict(user)
        session['logged_in'] = True
        return redirect('/todo')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    sql = "SELECT * FROM todos WHERE user_id = '%s' and id = '%s'";
    cur = g.db.execute(sql % (session['user']['id'],id))
    todo = cur.fetchone()
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    sql = "SELECT * FROM todos WHERE user_id = '%s'";
    cur = g.db.execute(sql % session['user']['id'])
    todos = cur.fetchall()
    return render_template('todos.html', todos=todos)


def addTODO():
    #print('Add btn pressed')
    #Task 1: Check for empty description or only containing spaces.
    description = request.form.get('description', '')
    if description.strip() != '':
        g.db.execute("INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"% (session['user']['id'],request.form.get('description', '')))
        g.db.commit()
        flash('TODO successfully added.',category='success')


def updateStatus():
    #print('Status btn pressed')
    #Task 2: Adding status functionality
    sql = "SELECT * FROM todos WHERE user_id = '%s'";
    cur = g.db.execute(sql % session['user']['id'])
    todos = cur.fetchall()
    statusBtnID=int(request.form['statusBtn'])
    COLUMN = 0 # id column
    column=[elt[COLUMN] for elt in todos]
    #statusBtn was clicked
    if statusBtnID in column:
        index=column.index(statusBtnID)
        COLUMN = TODO_STATUS_COL
        column=[elt[COLUMN] for elt in todos]
        if int(column[index])==0:
            g.db.execute("UPDATE todos SET status=1 where id = '%s'"% statusBtnID)
            g.db.commit()
        else:
            g.db.execute("UPDATE todos SET status=0 where id = '%s'"% statusBtnID)
            g.db.commit()

@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    
    if 'addBtn' in request.form:
        addTODO()
    if 'statusBtn' in request.form:
        updateStatus()
    return redirect('/todo')

@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    g.db.commit()
    flash('TODO successfully deleted.',category='success')
    return redirect('/todo')

@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_view_json(id):
    if not session.get('logged_in'):
        return redirect('/login')

    sql = "SELECT * FROM todos WHERE user_id = '%s' and id = '%s'";
    cur = g.db.execute(sql % (session['user']['id'],id))
    todo = cur.fetchone()
    value_list=[]
    for item in todo:
        value_list.append(item)

    table_cols = [description[0] for description in cur.description]

    json_dict=dict(zip(table_cols, value_list))
    json_str = json.dumps(json_dict,indent=4)
    return jsonify(json_dict)
#return render_template('todo_json.html', json_str=json_str)
