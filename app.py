from flask import Flask, render_template
import os

app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/colleges')
def colleges():
    return render_template('colleges.html')

if __name__ == '__main__':
    app.run(debug=True)
