from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy_declarative import usersTB, Base, todosTB

engine = create_engine('sqlite:///sqlalchemy_todo.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def clear_data():
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        print ('Clear table %s' % table)
        session.execute(table.delete())
    session.commit()

clear_data()

### User 1

new_user = usersTB(username='user1',password='user1')
session.add(new_user)
session.commit()

new_todo = todosTB(description='Vivamus tempus', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='lorem ac odio', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='Ut congue odio', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='Sodales finibus', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='Accumsan nunc vitae', users=new_user)
session.add(new_todo)
session.commit()



### User 2

new_user = usersTB(username='user2',password='user2')
session.add(new_user)
session.commit()

new_todo = todosTB(description='Lorem ipsum', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='In lacinia est', users=new_user)
session.add(new_todo)
session.commit()

new_todo = todosTB(description='Odio varius gravida', users=new_user)
session.add(new_todo)
session.commit()

### User 3
new_user = usersTB(username='user3',password='user3')
session.add(new_user)
session.commit()
