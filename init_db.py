from models import Friends, Messages, Users
from settings import Base, Session_db
from werkzeug.security import generate_password_hash

if __name__ == "__main__":

    base = Base()
    base.drop_db()
    base.create_db()
    
    with Session_db() as s:
        
        u1 = Users(username = 'admin', email="a@ex.com")    
        u1.password = generate_password_hash("admin")
        
        u2 = Users(username = 'user', email="a2@ex.com")    
        u2.password = generate_password_hash("user")
        s.add_all([u1, u2])
        s.commit()
        