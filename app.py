

from flask import Flask, render_template, request
import numpy as np
from hdbcli import dbapi
from nelson_siegel_svensson.calibrate import calibrate_ns_ols
from scipy.interpolate import InterpolatedUnivariateSpline
import csv
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':

        req = request.form

        fin_instrument = req["RFR_value"].lower()
        currency = req["currency"].lower()
        date = req["obs_date"]
        dateTab = date.split("-")
        date = dateTab[2]+"/"+dateTab[1]+"/"+dateTab[0]

        file = fin_instrument+"_"+currency+"2"

        print(fin_instrument, currency, date)

        conn = dbapi.connect(
            address='localhost',
            port=30015,
            user="S0023847278",
            password="@Teddyvito42873"
        )
        print('Connected:', conn.isconnected())
        cur = conn.cursor()

        try:
            change_schema = 'SET SCHEMA GROUPE_3_MACHINELEARNING'
            cur.execute(change_schema)
            sql_query = 'SELECT * FROM "' + file + '" WHERE "Dates"=?'
            cur.execute(sql_query, date)
            records = cur.fetchall()
            t = np.array([])
            y = np.array([])
            for row in records:
                if row[2] and row[1]:
                    t = np.append(t, float(row[1]))
                    y = np.append(y, float(row[2]))

        except (Exception, dbapi.DatabaseError) as error:
            print(error)
        if conn is not None:
            conn.close()

        curve, status = calibrate_ns_ols(t, y, tau0=1.0)  # starting value of 1.0 for the optimization of tau
        xi = t
        yi = curve(t)
        assert status.success

        x = np.linspace(0, 60, 61)
        order = 1
        s = InterpolatedUnivariateSpline(xi, yi, k=order)
        r = s(x)
        labels = [i for i in x]
        values = [i for i in r]
        print(labels)
        print(curve(t))
        return render_template("index.html", labels=labels, values=values,date=date, fin_instrument=fin_instrument,currency= currency)

    else:
        return render_template('index.html')


@app.route("/csv", methods=['POST', 'GET'])
def genarateByCsv():
    if request.method == 'POST':
        req = request.form
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)

        date = req["obs_date"]
        dateTab = date.split("-")
        date = dateTab[2] + "-" + dateTab[1] + "-" + dateTab[0]


        t = np.array([])
        y = np.array([])

        with open(file_path) as csv_file:
            csv_reader = csv.reader(csv_file)

            row_count = 0
            toDeleteIndex = 0

            for row in csv_reader:
                if (row_count == 0):
                    for data in row:
                        if (row.index(data) != 0):
                            t = np.append(t, int(re.search(r'\d+', data).group()))
                if (row[0] == date):
                    for data in row:
                        if (row.index(data) != 0) and data != "":
                            y = np.append(y, float(data))
                        if data == "" and t.size >= row.index(data):
                            t = np.delete(t, row.index(data) - 1)
                row_count += 1

        curve, status = calibrate_ns_ols(t, y, tau0=1.0)
        xi = t
        yi = curve(t)
        assert status.success

        x = np.linspace(0, 60, 61)
        order = 1
        s = InterpolatedUnivariateSpline(xi, yi, k=order)
        r = s(x)
        labels = [i for i in x]
        values = [i for i in r]
        print(labels)
        print(curve(t))

        return render_template("index.html", labels=labels, values=values)

    else:
        return render_template('index.html')

@app.route("/about")
def about():
    return """
    <h1 style='color: red;'>I'm a red H1 heading!</h1>
    <p>This is a lovely little paragraph</p>
    <code>Flask is <em>awesome</em></code>
    """

if __name__ == "__main__":
    app.run(debug=True)