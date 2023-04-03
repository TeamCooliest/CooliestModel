import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import Response,Flask, request, render_template,jsonify


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

app = Flask(__name__)
def solve(mdot, Cp, Tin, Tout, Twall, Tmid, area):
    # NOTE there might be more inputs than these... if there are,
    # please make changes where necessary... good luck (●'◡'●)
    h = (mdot * Cp * (Tout - Tin)) / (area * (Twall - Tmid))
    return h

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/solve', methods=['GET','POST'])
def my_form_post():
    mdot = float(request.form['mdot'])
    Cp = float(request.form['Cp'])
    Tin = float(request.form['Tin'])
    Tout = float(request.form['Tout'])
    Twall = float(request.form['Twall'])
    Tmid = float(request.form['Tmid'])
    area = float(request.form['area'])
    liquid = request.form['liquid']
    h = solve(mdot, Cp, Tin, Tout, Twall, Tmid, area)
    result = {
        "h": h
    }
    result = {str(key): value for key, value in result.items()}
    xs = []
    xs = [1,2,3,4]
    y1 = []
    y2 = []
    y1 = [mdot,Cp,Tin,Tout]
    y2 = [Twall,Tmid,area,h]
    plt.figure()
    plt.plot(xs, y1)
    plt.plot(xs, y2)
    plt.title("Test Plot")
    plt.xlabel("Numbers")
    plt.ylabel("Random Variables")
    plt.legend(["data about flow", "more data about flow"])
    plt.savefig('static/my_plot.png')
    return render_template('home.html', get_plot = True, plot_url = 'static/my_plot.png',result=result)



    #return jsonify(result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)