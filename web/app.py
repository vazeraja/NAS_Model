from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '')  # Safely get the input value
        return f"<div>{user_input}</div>"  # Return the text wrapped in a div
    return "No input received", 400  # Handle unexpected cases


if __name__ == '__main__':
    app.run(debug=True)
