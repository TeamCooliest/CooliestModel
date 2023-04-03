import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Response,Flask, request, render_template,jsonify
from model.analyze import solve

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/solve', methods=['GET','POST'])
def my_form_post():
    w = float(request.form['w'])
    h = float(request.form['h'])
    l = float(request.form['l'])
    T_in = float(request.form['T_in'])
    V_dot = float(request.form['V_dot'])
    q_chip = float(request.form['q_chip'])
    fluid_name = request.form['fluid_name']
    T_wall = solve(w, h, l, T_in, V_dot, q_chip, fluid_name)

    result = {
        "T_wall": T_wall
    }

    result = {str(key): value for key, value in result.items()}
    
    #plt.figure()
    #plt.plot(xs, y1)
    #plt.plot(xs, y2)
    #plt.title("Test Plot")
    #plt.xlabel("Numbers")
    #plt.ylabel("Random Variables")
    #plt.legend(["data about flow", "more data about flow"])
    #plt.savefig('static/my_plot.png')

    return render_template(result=result)



    #return jsonify(result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)