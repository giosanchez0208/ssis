from flask import Flask, url_for

app = Flask(__name__)

# Main page with hyperlinks to other pages
@app.route('/')
def home():
    return f'''
        <h1>Welcome to the Flask App!</h1>
        <ul>
            <li><a href="{url_for('about')}">About Page</a></li>
            <li><a href="{url_for('contact')}">Contact Page</a></li>
            <li><a href="{url_for('services')}">Services Page</a></li>
        </ul>
    '''

# About page
@app.route('/about')
def about():
    return '<h1>About Us</h1><p>This is the about page.</p>'

# Contact page
@app.route('/contact')
def contact():
    return '<h1>Contact Us</h1><p>This is the contact page.</p>'

# Services page
@app.route('/services')
def services():
    return '<h1>Our Services</h1><p>This is the services page.</p>'

if __name__ == '__main__':
    app.run(debug=True)
