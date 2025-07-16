from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import app
from models import Session_db, Users



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']       
        email = request.form["email"] 
        hashed = generate_password_hash(password)  
              
        user = Users.get_by_username(username)
        if user:
            flash("Користувач з таким ім'ям вже існує. Спробуйте інше ім'я.")
            return redirect(url_for('register'))
        else:
            new_user = Users(username=username, password=hashed, email=email)
            
            with Session_db() as session_db:
                session_db.add(new_user) 
                session_db.commit()
            
            flash("Реєстрація успішна, увійдіть у свій акаунт.")
            return redirect(url_for('login'))           
    
    return render_template("auth/register.html", title="Реєстрація")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Users.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Вхід успішний!")
            return redirect(url_for('index'))
        else:
            flash("Невірне ім'я користувача або пароль.")
            return redirect(url_for('login'))
    return render_template("auth/login.html", title="Вхід")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
