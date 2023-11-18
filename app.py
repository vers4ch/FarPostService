from flask import Flask, render_template, request, session, redirect, flash, url_for, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os
from PIL import Image
from io import BytesIO

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
    
class ServiceType(db.Model):
    __tablename__ = 'service_type'

    sid = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name_service = db.Column(db.Text(collation='pg_catalog."default"'))
    image = db.Column(db.LargeBinary)
    subgroup = db.Column(db.Text(collation='pg_catalog."default"'))

    def __repr__(self):
        return f"<ServiceType(name_service='{self.name_service}', subgroup={self.subgroup}, image={self.image})>"



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
        
        if user.username == username and user.password == password:
            response = make_response()
            # Если чекбокс "Запомнить меня" отмечен, устанавливаем куку с токеном или другим идентификатором
            if remember:
                response.set_cookie('user_token', 'aergergberbbdb', max_age=30 * 24 * 60 * 60)  # Например, токен действителен 30 дней

            session['uid'] = user.uid
            session['username'] = user.username
            session['email'] = user.email
            session['first_name'] = user.first_name
            session['last_name'] = user.last_name
            session['patronymic'] = user.patronymic
            session['is_master'] = user.is_master
            session['is_admin'] = user.is_admin
            

            return redirect(url_for('home'))
        else:
            flash('Неверный логин или пароль. Пожалуйста, проверьте свои данные и повторите попытку.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    user = User.query.filter_by(username=session['username']).first()
    
    # Извлекаем данные из базы данных
    services_data = ServiceType.query.all()
    
    # Группируем данные по name_service
    grouped_services = {}
    for service in services_data:
        if service.name_service not in grouped_services:
            grouped_services[service.name_service] = []
        grouped_services[service.name_service].append(service)
        print(grouped_services)

    # return render_template('home.html', grouped_services=grouped_services)
    return render_template('home.html', user = user, grouped_services=grouped_services)


@app.route('/service_details/<name_service>')
def service_details_by_name(name_service):
    # Здесь вы можете извлечь дополнительные данные для конкретного name_service
    return render_template('masters_list.html', name_service=name_service)

@app.route('/service_details/<subgroup>')
def service_details_by_subgroup(subgroup):
    # Здесь вы можете извлечь дополнительные данные для конкретного subgroup
    return render_template('masters_list.html', subgroup=subgroup)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query')
        print(query)
        # Выполните поиск в базе данных
        results = ServiceType.query.filter(
            or_(
                ServiceType.name_service.ilike(f'%{query}%'),
                ServiceType.subgroup.ilike(f'%{query}%')
            )
        ).all()
        print(results)
        return render_template('search_results.html', results=results)
    return render_template('search.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('login.html')

        

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
