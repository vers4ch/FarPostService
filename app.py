from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '314'

@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('index.html')

# Запуск приложения
if __name__ == '__main__':
    os.system("clear")
    # Запуск приложения в режиме отладки
    app.run(debug=True)