from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required
from sqlalchemy import select
from app import app
from models import Users, Friends, Messages
from flask_login import current_user
from settings import Session_db, cache


@app.route("/search_friends", methods = ["GET","POST"])
@login_required
def search_friends():
    if request.method == 'POST':
        user_search_name = request.form['name']
        
        search_user = Users.get_by_username(user_search_name)
        print(search_user)
        if search_user:
            check_request= Friends.check_friends(search_user.id, current_user.id)     
            if check_request:
                Friends.create_request(current_user, search_user)                
                flash("Запит на дружбу успішно надіслано!", 'success')
            else:
                flash("Ви вже являєтеся друзями або між вами вже є активниз запит на дружбу", 'danger')
        else:
            flash("Користувача з таким нікнеймом не знайдено", 'danger')
    return render_template("search_friends.html")


@app.route('/friend_requests')
@login_required
def friend_requests():
    with Session_db() as session:
        stmt = select(Friends).filter_by(recipient = current_user.id, status = False)
        all_friend_requests = session.scalars(stmt).all()
        id_names_dict = {}
        for i in all_friend_requests:
            id_names_dict[i.sender_user.id] = i.sender_user.username

        return render_template('friend_requests.html', data = id_names_dict)



@app.route('/friend_requests_confirm', methods = ["POST"])
@login_required
def friend_requests_confirm():
    request_sende_id = request.form['id']
    with Session_db() as session:
        select_request = session.query(Friends).filter_by(sender=request_sende_id, recipient=current_user.id, status=False).first()
        if not select_request:
            return 'Сталася помилка при підтвердженні'

        if request.form['result'] == 'yes':
                select_request.status = True
                session.commit()

        elif request.form['result'] == 'no':
            session.delete(select_request)
            session.commit()
        else:
            return redirect(url_for('home'))
    
    cache.clear()
    return redirect(url_for("friend_requests"))


def make_key_cache():
    return f"user:{current_user.id}|{request.full_path}"

@app.route("/my_friends")
@cache.cached(timeout=60*5, key_prefix=make_key_cache)
@login_required
def my_friends():
    with Session_db() as session:
        all_friends1 = session.query(Friends).filter_by(sender = current_user.id, status=True).all()
        all_friends2 = session.query(Friends).filter_by(recipient=current_user.id, status=True).all()
        friend_names = []
        for i in all_friends1:
            friend_names.append(i.recipient_user.username)
        for i in all_friends2:
            friend_names.append(i.sender_user.username)
        return render_template("my_friends.html", data=friend_names)


@app.route('/create_message/<string:user_name>', methods = ["GET","POST"])
@login_required
def create_message(user_name):
    if request.method == 'POST':
        message_text = request.form["text"]
        with Session_db() as session:
            user_recipient = session.query(Users).filter_by(username = user_name).first()
            if not user_recipient:
                flash('Отримувача не знайдено','danger')
                return render_template('create_message.html')

            check_request1 = session.query(Friends).filter_by(sender=user_recipient.id, recipient=current_user.id, status = True).first()
            check_request2 = session.query(Friends).filter_by(sender=current_user.id, recipient=user_recipient.id, status = True).first()
            
            if check_request1 or check_request2:
                new_message = Messages(sender = current_user.id, recipient=user_recipient.id, message_text = message_text)
                session.add(new_message)
                session.commit()
                flash("Повідомлення надіслано!","success")

            else:
                flash("Отримувача не являється другом", "danger")
                return render_template('create_message.html')

    return render_template('create_message.html', for_user=user_name)


@app.route("/new_messages")
@login_required
def new_messages():
    with Session_db() as session:
        # unread_messages
        stmt = select(Messages).filter_by(recipient = current_user.id, status_check=False)
        new_messages = session.scalars(stmt).fetchall()
        
        name_text_list = []
        for i in new_messages:
            name_text_list. append({i.sender_user.username: i.message_text})
            i.status_check = True
            session.commit()
        
    return render_template('new_messages.html', data = name_text_list)
    