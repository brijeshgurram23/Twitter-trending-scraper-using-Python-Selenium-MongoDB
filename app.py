from flask import Flask, render_template, jsonify
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('C:/Users/asbmr/Desktop/scraper/index.html')

@app.route('/run-script')
def run_script():
    result = main(TWITTER_USERNAME, TWITTER_PASSWORD)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
