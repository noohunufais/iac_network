from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/add_device", methods=['GET','POST'])
def add_device():
    if request.method == 'GET':
        return render_template('add_device.html')
    else:
        return request.form


@app.route("/read_form", methods=['POST'])
def read_form():
    return request.form
        

if __name__ == "__main__":
    app.run(host='0.0.0.0')
