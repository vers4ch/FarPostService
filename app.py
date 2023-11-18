from flask import Flask, render_template, request, session, redirect, flash, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '314'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/versach'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    patronymic = db.Column(db.String)
    password = db.Column(db.String, nullable=False, default='20042004')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_master = db.Column(db.Boolean, default=False)
    is_customer = db.Column(db.Boolean, default=False)
    uid = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'<User {self.username}>'


# Создание таблицы в базе данных
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        remember = request.form.get('remember')  # Получаем значение чекбокса

        # print(user.email)
        
        if user.username == username and user.password == password:
            response = make_response()
            # Если чекбокс "Запомнить меня" отмечен, устанавливаем куку с токеном или другим идентификатором
            if remember:
                response.set_cookie('user_token', 'aergergberbbdb', max_age=30 * 24 * 60 * 60)  # Например, токен действителен 30 дней

            session['user_id'] = user.uid
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['patronymic'] = user.patronymic

            return redirect(url_for('home'))
        else:
            flash('Неверный логин или пароль. Пожалуйста, проверьте свои данные и повторите попытку.', 'danger')
    return render_template('login.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html')
        

# new_item = User(username="Versach", email="dan2004degvl@mail.ru", last_name="Дегтярев", first_name="Данил", patronymic="Викторович", password="admin")
# try:
# 				db.session.add(new_item)
# 				db.session.commit()
# 				return render_template('login.html')
# except Exception as e:
# 				db.session.rollback()
# 				return f'Error adding item. Error: {str(e)}'


# Запуск приложения
if __name__ == '__main__':
    os.system("clear")
    # Запуск приложения в режиме отладки
    app.run(debug=True)
