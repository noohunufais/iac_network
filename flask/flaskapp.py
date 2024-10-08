from flask import Flask, render_template, request, redirect, url_for
import getconfig
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


@app.route("/golden_config", methods=['GET'])
def golden_config():
    return getconfig.get_golden_config()


@app.route('/test_form', methods=['GET', 'POST'])
def test_form():
    if request.method == 'POST':
        vlan_data = request.form.getlist('vlan[]')
        vlan_names = request.form.getlist('vlan_name[]')
        # Process the vlan_data and vlan_names as needed
        for vlan_number, vlan_name in zip(vlan_data, vlan_names):
            print(f"VLAN Number: {vlan_number}, VLAN Name: {vlan_name}")
        return request.form
    return render_template('test_form.html')
        

if __name__ == "__main__":
    app.run(host='0.0.0.0')
