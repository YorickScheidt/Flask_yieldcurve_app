from tabnanny import check
from flask import Flask, session, render_template, request, redirect
import numpy as np
from hdbcli import dbapi
from nelson_siegel_svensson.calibrate import calibrate_ns_ols
from scipy.interpolate import InterpolatedUnivariateSpline

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/index', methods=['POST', 'GET'])
def index():
    checklog = 1 #session.get('checklog', None)

    print("value2 ", checklog )
    

    if checklog == 1:

        if request.method == 'POST':

            req = request.form

            fin_instrument = req["RFR_value"].lower()
            currency = req["currency"].lower()
            date = req["obs_date"]
            dateTab = date.split("-")
            date = dateTab[2]+"/"+dateTab[1]+"/"+dateTab[0]

            file = fin_instrument+"_"+currency+"2"

            print(fin_instrument, currency, date)

            username = "S0023847307" #session.get('username', None)
            password = "AnnickVan8GiovanitaVan50" #session.get('pwd', None)

            conn = dbapi.connect(
            address='localhost',
            port=30015,
            user= username,
            password= password
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
    else:
        print("Please connect first")
        return """
            <html>
                <head>
                    <title>Title of the document</title>
                    <style>
                    .button {
                        background-color: #1c87c9;
                        border: none;
                        color: white;
                        padding: 20px 34px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 20px;
                        margin: 4px 2px;
                        cursor: pointer;
                    }
                    </style>
                </head>
                <body>
                    <h2 style='color: red;'> You are not authentified ! </h2>
                    <h3>Please connect first</h3>
                    <a href="/" class="button">to login page !!</a>
                </body>
            </html>
            """

@app.route("/about")
def about():
    return """
    <h1 style='color: red;'>I'm a red H1 heading!</h1>
    <p>This is a lovely little paragraph</p>
    <code>Flask is <em>awesome</em></code>
    """

@app.route("/" , methods=['POST', 'GET'])
def login():

    session.clear()
    checklog = 0

    if request.method == 'POST':

        print('here')
        req = request.form

        username = req["userName"]
        password = req["userPassword"]


        try:
            conn = dbapi.connect(
            address='localhost',
            port=30015,
            user= username,
            password= password
            )
            print('Connected:', conn.isconnected())
        
            if( conn.isconnected()):
                checklog = 1
                session['checklog']= checklog 
                session['username']= username
                session['pwd']= password

                print (session.get('checklog', None))
                return redirect('/index')
            else:
                return render_template('login.html')

        except  (Exception, dbapi.Error) as error:
            print (error)

      
       # cur = conn.cursor()

       
       # if conn is not None:
            #conn.close()

    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)