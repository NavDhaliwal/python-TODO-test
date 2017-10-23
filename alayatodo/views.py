from alayatodo import app
import json, math, os, sys
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
NUM_TODOS_PER_PAGE=2

resource_path = os.path.abspath(os.path.join('..', 'resources'))
sys.path.append(resource_path)

from sqlalchemy.inspection import inspect
from resources.sqlalchemy_declarative import usersTB, Base, todosTB
from sqlalchemy import create_engine, and_, or_, not_
engine = create_engine('sqlite:///sqlalchemy_todo.db')
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
dbsession = DBSession()

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

    user = dbsession.query(usersTB).filter(and_(usersTB.username.like(username), usersTB.password.like(password))).one()
    #sql = "SELECT * FROM users WHERE username = '%s' AND password = '%s'";
    #cur = g.db.execute(sql % (username, password))
    #user = cur.fetchone()
    if user:
        dictret = dict(user.__dict__)
        dictret.pop('_sa_instance_state', None)
        session['user'] = dictret
        session['logged_in'] = True
        session['current_page']=1
        return redirect('/todo/page/1')

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('current_page', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    #sql = "SELECT * FROM todos WHERE user_id = '%s' and id = '%s'";
    #cur = g.db.execute(sql % (session['user']['id'],id))
    #todo = cur.fetchone()
    todo = dbsession.query(todosTB).filter(todosTB.id == id).one()
    return render_template('todo.html', todo=todo)


@app.route('/todo/page/<int:page_num>', methods=['POST'])
@app.route('/todo/page/<int:page_num>/', methods=['POST'])
def todos_navigation(page_num):

    if 'Previous' in request.form:
        page_num=page_num-1
    elif 'Next' in request.form:
        page_num=page_num+1

    if page_num<=0:
        page_num=1
    return redirect('/todo/page/'+str(page_num))


@app.route('/todo/page/<int:page_num>', methods=['GET'])
@app.route('/todo/page/<int:page_num>/', methods=['GET'])
def todos(page_num):
    if not session.get('logged_in'):
        return redirect('/login')

    todos = dbsession.query(todosTB).filter(todosTB.user_id == session['user']['id']).all()
    #sql = "SELECT * FROM todos WHERE user_id = '%s'";
    #cur = g.db.execute(sql % session['user']['id'])
    #todos = cur.fetchall()

    max_page_num=math.ceil(len(todos)/NUM_TODOS_PER_PAGE)
    if page_num<=0:
        page_num=1
    elif page_num>max_page_num:
        page_num=max_page_num
    session['current_page']=page_num
    start_idx=NUM_TODOS_PER_PAGE*(session['current_page']-1)
    end_idx=start_idx+NUM_TODOS_PER_PAGE

    return render_template('todos.html', todos=todos[start_idx:end_idx],page_num=page_num)


def addTODO():
    #print('Add btn pressed')
    #Task 1: Check for empty description or only containing spaces.
    description = request.form.get('description', '')
    if description.strip() != '':
        #g.db.execute("INSERT INTO todos (user_id, description) VALUES ('%s', '%s')"% (session['user']['id'],request.form.get('description', '')))
        #g.db.commit()
        user=dbsession.query(usersTB).filter(usersTB.id == session['user']['id']).one()
        new_todo = todosTB(description=description.strip(), users=user)
        dbsession.add(new_todo)
        dbsession.commit()
        flash('TODO successfully added.',category='success')


def updateStatus():
    #print('Status btn pressed')
    #Task 2: Adding status functionality
    #sql = "SELECT * FROM todos WHERE user_id = '%s'";
    #cur = g.db.execute(sql % session['user']['id'])
    #todos = cur.fetchall()
    statusBtnID=int(request.form['statusBtn'])
    todo_sel = dbsession.query(todosTB).filter(and_(todosTB.user_id.like(session['user']['id']),todosTB.id.like(statusBtnID))).one()
    #COLUMN = 0 # id column
    #column=[elt[COLUMN] for elt in todos]
    #statusBtn was clicked
    #if statusBtnID in column:
    #    index=column.index(statusBtnID)
    #    COLUMN = TODO_STATUS_COL
    #    column=[elt[COLUMN] for elt in todos]
    if todo_sel.status==0:
        #g.db.execute("UPDATE todos SET status=1 where id = '%s'"% statusBtnID)
        #g.db.commit()
        todo_sel.status=1
    else:
        #g.db.execute("UPDATE todos SET status=0 where id = '%s'"% statusBtnID)
        #g.db.commit()
        todo_sel.status=0
    dbsession.commit()
                                            

@app.route('/todo/<int:page_num>', methods=['POST'])
@app.route('/todo/<int:page_num>/', methods=['POST'])
def todos_POST(page_num):
    if not session.get('logged_in'):
        return redirect('/login')
    
    if 'addBtn' in request.form:
        addTODO()
    if 'statusBtn' in request.form:
        updateStatus()
    if 'deleteBtn' in request.form:
        deleteBtnID=int(request.form['deleteBtn'])
        #print('DELETING'+str(deleteBtnID))
        dbsession.query(todosTB).filter(todosTB.id == deleteBtnID).delete()
        dbsession.commit()
        flash('TODO successfully deleted.',category='success')
    return redirect('/todo/page/'+str(page_num))

@app.route('/todo/<int:page_num>', methods=['POST'])
@app.route('/todo/<int:page_num>/', methods=['POST'])
def todo_delete(page_num):
    if not session.get('logged_in'):
        return redirect('/login')
    #g.db.execute("DELETE FROM todos WHERE id ='%s'" % id)
    #g.db.commit()
    deleteBtnID=-1
    if 'deleteBtn' in request.form:
        deleteBtnID=int(request.form['deleteBtn'])
    print('DELETING'+str(deleteBtnID))
    dbsession.query(todosTB).filter(todosTB.id.like(deleteBtnID)).delete()
    dbsession.commit()
    flash('TODO successfully deleted.',category='success')
    return redirect('/todo/page/'+str(page_num))

@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
def todo_view_json(id):
    if not session.get('logged_in'):
        return redirect('/login')

    todo=dbsession.query(todosTB).filter(and_(todosTB.user_id.like(session['user']['id']),todosTB.id == id)).one()
    value_list=[]

    dictret = dict(todo.__dict__)
    dictret.pop('_sa_instance_state', None)
    print(dictret)

    return jsonify(dictret)
