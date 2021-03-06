from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import os
import json

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'koreanfood'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'ck'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# routes
@app.route('/')
def home():
    return render_template('home.html')


# guiides
@ app.route('/guides')
def guides():
    return render_template('guides.html')

@ app.route('/gettingStarted')
def gettingStarted():
    return render_template('gettingStarted.html')

@ app.route('/layouts')
def layouts():
    return render_template('layouts.html')

@ app.route('/guides/parts')
def parts():
    return render_template('parts.html')

@ app.route('/guides/switches')
def switches():
    return render_template('switches.html')

@ app.route('/guides/modifications')
def modifications():
    return render_template('mods.html')


# builds
@app.route('/builds', methods=['GET', 'POST'])
def builds():
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':

        print("POST method")

        # Add a new build
        if request.form.get('add'):

            build_name = request.form['build_name']
            case = request.form['case']
            pcb = request.form['pcb']
            plate = request.form['plate']
            switches = request.form['switches']
            keycaps = request.form['keycaps']

            add_query = 'INSERT INTO Builds (buildName, caseID, pcbID, plateID, switchID, keycapID) VALUES (%s, %s, %s, %s, %s, %s);'
            cur.execute(add_query, (build_name, case, pcb, plate, switches, keycaps))
            mysql.connection.commit()

        # Update an existing build
        if request.form.get('update'):

            print("UPDATE request received")

            id = request.form['id']
            name = request.form['build_name']
            case = request.form['case']
            pcb = request.form['pcb']
            plate = request.form['plate']
            switch = request.form['switches']
            keycap = request.form['keycaps']

            update_query = 'UPDATE Builds SET buildName = %s, caseID = %s, pcbID = %s, plateID = %s, switchID = %s, keycapID = %s WHERE Builds.buildID = %s;'
            cur.execute(update_query, (name, case, pcb, plate, switch, keycap, id))
            mysql.connection.commit()

        # Delete a build
        if request.form.get('delete'):

            print("DELETE request received")

            id = request.form['id']
            cur.execute('DELETE FROM Builds WHERE Builds.buildID = %s;', (id, ))
            mysql.connection.commit()
    
    # Get all existing builds
    query = (""" 
            SELECT Builds.buildID, Builds.buildName, Cases.caseName, Pcbs.pcbType, Plates.material, Switches.switchName, Keycaps.keycapName FROM Builds 
            INNER JOIN Cases ON Builds.caseID = Cases.caseID
            INNER JOIN Pcbs ON Builds.pcbID = Pcbs.pcbID
            INNER JOIN Plates ON Builds.plateID = Plates.plateID
            INNER JOIN Switches ON Builds.switchID = Switches.switchID
            INNER JOIN Keycaps ON Builds.keycapID = Keycaps.keycapID; """)

    cur.execute(query)
    builds = cur.fetchall()
    return render_template('builds.html', builds = builds)

@app.route('/updatebuild/<int:id>', methods=['GET', 'POST'])
def updateBuild(id):
    cur = mysql.connection.cursor()

    # Get existing selections for current build
    build_query = (""" 
            SELECT Builds.buildID, Builds.buildName, Cases.caseID, Pcbs.pcbID, Plates.plateID, Switches.switchID, Keycaps.keycapID FROM Builds 
            INNER JOIN Cases ON Builds.caseID = Cases.caseID
            INNER JOIN Pcbs ON Builds.pcbID = Pcbs.pcbID
            INNER JOIN Plates ON Builds.plateID = Plates.plateID
            INNER JOIN Switches ON Builds.switchID = Switches.switchID
            INNER JOIN Keycaps ON Builds.keycapID = Keycaps.keycapID
            WHERE Builds.buildID = %s;
            """)
    cur.execute(build_query, (id, ))
    build = cur.fetchall()

    # Get all options for build components 
    # get cases
    cur.execute('SELECT * FROM Cases;')
    cases = cur.fetchall()

    # get pcbs
    cur.execute('SELECT * FROM Pcbs;')
    pcbs = cur.fetchall()

    # get plates
    cur.execute('SELECT * FROM Plates;')
    plates = cur.fetchall()

    # get switches
    cur.execute('SELECT * FROM Switches;')
    switches = cur.fetchall()

    # get keycaps
    cur.execute('SELECT * FROM Keycaps;')
    keycaps = cur.fetchall()

    return render_template('updatebuild.html', build = build, cases = cases, pcbs = pcbs, plates = plates, switches = switches, keycaps = keycaps)


@app.route('/builds/sample')
def sample():
    return render_template('samplebuild.html')

@app.route('/builds/create', methods=['GET', 'POST'])
def create():
    cur = mysql.connection.cursor()

    if request.method == 'GET':

        # get cases
        cur.execute('SELECT * FROM Cases;')
        cases = cur.fetchall()

        # get pcbs
        cur.execute('SELECT * FROM Pcbs;')
        pcbs = cur.fetchall()

        # get plates
        cur.execute('SELECT * FROM Plates;')
        plates = cur.fetchall()

        # get switches
        cur.execute('SELECT * FROM Switches;')
        switches = cur.fetchall()

        # get keycaps
        cur.execute('SELECT * FROM Keycaps;')
        keycaps = cur.fetchall()

    return render_template('createbuild.html', cases = cases, pcbs = pcbs, plates = plates, switches = switches, keycaps = keycaps)


@app.route('/productSearch', methods=['GET', 'POST'])
def productSearch():

    if request.args.get('search'):
        os.system('python shopping_service.py ' + '"' + request.args['product'] + '"')

        # Get search data from json file
        try:
            with open(request.args['product'] + " result.json") as infile:
                json_array = json.load(infile)
                results = []
                for i in range(10):
                    item_details = {'thumbnail': None, 'title': None, 'price': None, 'vendor': None, 'link': None}
                    item_details['thumbnail'] = json_array[i]['thumbnail']
                    item_details['title'] = json_array[i]['title']
                    item_details['price'] = json_array[i]['price']

                    if json_array[i]['source'][:7] == '.aULzUe':
                        item_details['vendor'] = json_array[i]['source'][169:]
                    else: 
                        item_details['vendor'] = json_array[i]['source']
                    item_details['link'] = json_array[i]['link']

                    results.append(item_details)

            return render_template('productSearch.html', results = results, show_results = 1, no_results = 0)
    
        # SerpAPI did not find any results
        except:
            no_results = 1
            return render_template('productSearch.html', show_results = 0, no_results = 1)
       
    
    return render_template('productSearch.html', show_results = 0, no_results = 0)


# listener
if __name__ == '__main__':
    app.run(host='localhost', port=2297, debug=True)