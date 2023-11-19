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

class MasterCard(db.Model):
    __tablename__ = 'master_cards'

    mc_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer)
    service_id = db.Column(db.Text)
    price = db.Column(db.Text)
    about_master = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Integer)
    address = db.Column(db.Text)
    count_rate = db.Column(db.Integer)
    sum_rate = db.Column(db.Integer)

    # def __init__(self, user_id, service_id, price, about_master, education, experience, address, count_rate, sum_rate):
    #     self.user_id = user_id
    #     self.service_id = service_id
    #     self.price = price
    #     self.about_master = about_master
    #     self.education = education
    #     self.experience = experience
    #     self.address = address
    #     self.count_rate = count_rate
    #     self.sum_rate = sum_rate
        
    def __repr__(self):
        return f"<MasterCard(user_id='{self.user_id}', service_id={self.service_id}, price={self.price}, about_master={self.about_master}, education={self.education}, experience={self.experience}, address={self.address}, count_rate={self.count_rate}, sum_rate={self.sum_rate})>"

# Создание таблицы в базе данных
with app.app_context():
    db.create_all()

def cutEmail(email):
    if "@" in email:
        index = email.index("@")
        login = email[:index]
        return login
    else:
        return email


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user == None:
            flash('Логин не найден', 'danger')
            return redirect(url_for('login'))
        print(user)
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
            flash('Неверный пароль', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        patronymic = request.form['patronymic']
        email = request.form['email']
        password = request.form['password']
        registration_type = request.form.get('registration_type')
        print(registration_type)
        if registration_type == "is_master":
            is_master = True
            is_customer = False
        else:
            is_customer = True
            is_master = False
        new_item = User(username=cutEmail(email), email=email, last_name=last_name, first_name=first_name, patronymic=patronymic, password=password, is_master = is_master, is_customer = is_customer)
        db.session.add(new_item)
        db.session.commit()
        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('login'))
        
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

@app.route('/service_types')
def get_service_types():
    service_types = ServiceType.query.all()
    types_list = [service_type.name_service for service_type in service_types]
    return {'service_types': types_list}

@app.route('/unique_service_names')
def get_unique_service_names():
    unique_names = ServiceType.query.distinct(ServiceType.name_service).all()
    names_list = [name.name_service for name in unique_names]
    return {'unique_names': names_list}


@app.route('/service_subgroups/<name_service>')
def get_service_subgroups(name_service):
    service_subgroups = ServiceType.query.filter_by(name_service=name_service).distinct(ServiceType.subgroup).all()
    subgroups_list = [subgroup.subgroup for subgroup in service_subgroups]
    return {'subgroups': subgroups_list}


@app.route('/create_master_card', methods=['GET', 'POST'])
def create_master_card():
    user = User.query.filter_by(username=session['username']).first()
    cards = MasterCard.query.filter_by(user_id=user.uid).all()
    # service = ServiceType.query.filter_by(sid=16).first()
    for card in cards:
        print(card.service_id)
        service = ServiceType.query.filter_by(sid=card.service_id).first()
        card.service_id = service.subgroup
        print(card.service_id) 
    
    return render_template('create_master_card.html', user = user, cards=cards, service = service)

@app.route('/new_card', methods=['GET', 'POST'])
def new_card():
    if request.method == 'POST':
        service_subgroup = request.form['service-subgroup']
        about = request.form['about']
        education = request.form['education']
        exp = request.form['exp']
        price = request.form.get('price')
        address = request.form.get('address')
        new_item = MasterCard(user_id = session['uid'], service_id = 2, price = price, about_master = about, education = education, experience = exp, address = address, count_rate = 0, sum_rate = 0)
        db.session.add(new_item)
        db.session.commit()
        flash('Карточка успешно создана!', 'success')
        return create_master_card
    return render_template('new_card.html', user = session)


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
        return render_template('search_results.html', results=results, user = session)
    return render_template('search.html')

@app.route('/reset_pass', methods=['GET', 'POST'])
def reset_pass():
    return render_template('reset_pas.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html', user = session)



# Запуск приложения
if __name__ == '__main__':
    os.system("clear")
    # Запуск приложения в режиме отладки
    app.run(debug=True)
