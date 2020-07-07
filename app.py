from flask import Flask, render_template, request, redirect, send_file, session
import flask_login
from werkzeug.security import check_password_hash
from receipts import clientReceipt, seminarReceipt
from datetime import date, datetime
from os import remove, path
import sqlite3


# Configure app
app = Flask(__name__)
app.secret_key = "b'mo&I:/xfc2xfb.x0bc,xe3?xdbJ/xac!$5'"
ROOT = path.dirname(path.realpath(__file__))


# LOGIN STUFF
# To set it all up
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
class User(flask_login.UserMixin):
    pass
@login_manager.user_loader
def user_loader(user_id):
    user = User()
    user.id = user_id
    return user
# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    # Display login page
    if request.method == "GET":
        return render_template("login.html", firstTime = True)

    # Log user in
    else:
        # Using hash of the password Mom decided on
        if check_password_hash('pbkdf2:sha256:150000$NdXimIou$e43134704cb1264e6532218161e1d8f9f07f4eaea96c0c0807aa7175c3b5c540', request.form['password']):
            user = User()
            user.id = 'CASAOCEANE'
            flask_login.login_user(user)
            # Clear docName for the session when logging in
            session['docName'] = None
            return redirect('/')
        else:
            return render_template("login.html", wrongPassword = True)
# Log out button
@app.route("/logout")
@flask_login.login_required
def logout():
    # Delete any receipt in web app, if any
    if session['docName']:
        remove(path.join(ROOT, session['docName']))
        session['docName'] = None

    flask_login.logout_user()
    return redirect('/login')


# RECEIPT PAGE
@app.route("/")
@flask_login.login_required
def receipt():
    # Delete any receipt in web app, if any
    if session['docName']:
        remove(path.join(ROOT, session['docName']))
        session['docName'] = None

    # Get the receipt number to pre-fill the receipt number text box
    connection = sqlite3.connect(path.join(ROOT, "receipts.db"))
    cursor = connection.cursor()
    cursor.execute("SELECT MAX (receiptID) FROM receipts")
    receiptIDData = cursor.fetchall()
    receiptID = int(receiptIDData[0][0])
    newReceiptID = receiptID + 1
    cursor.close()
    connection.commit()
    connection.close()

    return render_template('receipt.html', newReceiptID = newReceiptID)
# Client receipt page
@app.route("/getClientReceipt", methods=["POST"])
def getClientReceipt():
    if request.method == "POST":
        # Process given information to produce the receipt, download it to computer, and store info in db

        # GET ALL USER DATA
        # Get client source
        source = request.form["source"]
        # Get full name
        firstName = request.form["firstName"].capitalize()
        lastName = request.form["lastName"].upper()
        # Get sex
        gender = request.form["gender"]
        if gender == "m":
            sex = "M."
        else: 
            sex = "Mme."
        # Get receipt ID
        receiptID = int(request.form["ID"])
        # Set up start date
        startDateEntry = request.form["startDate"]
        sYear, sMonth, sDay = map(int, startDateEntry.split("-"))
        startDate = date(sYear, sMonth, sDay)
        # Set up end date
        endDateEntry = request.form["endDate"]
        eYear, eMonth, eDay = map(int, endDateEntry.split("-"))
        endDate = date(eYear, eMonth, eDay)
        # Calculate length of stay from given dates
        lengthOfStay = (endDate - startDate).days
        # Get total price
        totalPrice = float(request.form["totalPrice"])

        # GENERATE FILE AND PROCEED TO DOWNLOAD PAGE
        # Call the clientReceipt() function to generate it as well as save info in db
        session['docName'] = clientReceipt(source, firstName, lastName, sex, startDate, endDate, lengthOfStay, receiptID, totalPrice)
        # Redirect to download page
        return render_template("download.html")
# Seminar receipt page
@app.route("/getSeminarReceipt", methods=["POST"])
def getSeminarReceipt():
    if request.method == "POST":
        # Process given information to produce the receipt, download it to computer, and store info in db
        
        # GET ALL USER DATA
        # Get company name
        company = request.form["company"].upper()
        # Get receipt ID
        receiptID = int(request.form["ID"])
        # Set up start date
        startDateEntry = request.form["startDate"]
        sYear, sMonth, sDay = map(int, startDateEntry.split("-"))
        startDate = date(sYear, sMonth, sDay)
        # Set up end date
        endDateEntry = request.form["endDate"]
        eYear, eMonth, eDay = map(int, endDateEntry.split("-"))
        endDate = date(eYear, eMonth, eDay)
        # Calculate length of stay from given dates
        lengthOfStay = (endDate - startDate).days + 1
        # Get total price
        pricePerDayWithoutTax = float(request.form["pricePerDay"])

        # GENERATE FILE AND PROCEED TO DOWNLOAD PAGE
        # Call the seminarReceipt() function to generate it as well as save info in db
        session['docName'] = seminarReceipt(company, receiptID, startDate, endDate, lengthOfStay, pricePerDayWithoutTax)
        # Redirect to download page
        return render_template("download.html")
# To download the receipt when button is clicked
@app.route("/getReceipt")
def getReceipt():
    return send_file(path.join(ROOT, session['docName']), as_attachment = True)


# STATISTICS PAGE
@app.route("/stats", methods=["GET", "POST"])
@flask_login.login_required
def stats():
    # Display all statistics indicators, organized by year
    if request.method == "GET":
        # Delete any receipt in web app, if any
        if session['docName']:
            remove(path.join(ROOT, session['docName']))
            session['docName'] = None

        # Current year to limit all db data for Overview Stats to the current year
        year = str(datetime.now().year)
        
        # Open db
        connection = sqlite3.connect(path.join(ROOT, "receipts.db"))
        
        # If there is nothing in the database (for both clients and seminars), display error message
        # Get client count
        clientCountCursor = connection.cursor()
        clientCountCursor.execute("SELECT COUNT (*) FROM receipts WHERE type = 'client'")
        clientCountData = clientCountCursor.fetchall()
        clientCount = clientCountData[0][0]
        # Get seminar count
        seminarCountCursor = connection.cursor()
        seminarCountCursor.execute("SELECT COUNT (*) FROM receipts WHERE type = 'seminar'")
        seminarCountData = seminarCountCursor.fetchall()
        seminarCount = seminarCountData[0][0]
        # Do check to display error message
        if clientCount == 0 or seminarCount == 0:
            return render_template("stats.html", noData = True)

        # REVENUE TABLE
        # Set up dict with revenue data
        revenues = {}
        # Get total revenue from clients
        clientRevCursor = connection.cursor()
        clientRevCursor.execute(f"SELECT SUM (totalPrice) FROM receipts WHERE type = 'client' AND endDate >= '{year}-01-01'")
        clientRevData = clientRevCursor.fetchall()
        clientRev = float(clientRevData[0][0])
        revenues['clientRev'] = str(round(clientRev)) + " MAD"
        # Get total revenue from seminars
        seminarRevCursor = connection.cursor()
        seminarRevCursor.execute(f"SELECT SUM (lengthOfStay), AVG (pricePerDayWithoutTax) FROM receipts WHERE type = 'seminar' AND endDate >= '{year}-01-01'")
        seminarRevData = seminarRevCursor.fetchall()
        seminarRev = (float(seminarRevData[0][0]) * float(seminarRevData[0][1])) * 1.2
        revenues['seminarRev'] = str(round(seminarRev)) + " MAD"
        # Get total revenue (client + seminar)
        total = clientRev + seminarRev
        revenues['total'] = str(round(total)) + " MAD"
        # Get percentages of different revenues
        revenues['clientPercent'] = round(((clientRev / total) * 100), 1)
        revenues['seminarPercent'] = round(((seminarRev / total) * 100), 1)

        # CLIENT SOURCES TABLE
        # Set up dict with source percentages
        sources = {}
        # Get total number of clients from AirBnB
        airbnbCursor = connection.cursor()
        airbnbCursor.execute(f"SELECT COUNT (*) FROM receipts WHERE type = 'client' AND source = 'AirBnB' AND endDate >= '{year}-01-01'")
        airbnbData = airbnbCursor.fetchall()
        airbnbCount = float(airbnbData[0][0])
        # Get total number of clients from Other
        otherCursor = connection.cursor()
        otherCursor.execute(f"SELECT COUNT (*) FROM receipts WHERE type = 'client' AND source = 'Other' AND endDate >= '{year}-01-01'")
        otherData = otherCursor.fetchall()
        otherCount = float(otherData[0][0])
        # Calculate percentages and store in sources dict
        total = airbnbCount + otherCount
        sources['percentAirbnb'] = round(((airbnbCount / total) * 100), 1)
        sources['percentOther'] = round(((otherCount / total) * 100), 1) 

        # ALL CLIENT DATA
        clientDataCursor = connection.cursor()
        clientDataCursor.execute("SELECT receiptID, source, firstName, lastName, sex, startDate, endDate, lengthOfStay, totalPrice FROM receipts WHERE type = 'client' ORDER BY endDate DESC, receiptID DESC")
        clientData = clientDataCursor.fetchall()
        clientTableLength = len(clientData)
        # Create Client CSV file to export data
        clientCSVCursor = connection.cursor()
        with open(path.join(ROOT, 'clientCSV.csv'), 'w') as file:
            file.write("Receipt Number,First Name,Last Name,Sex,Start Date,End Date,Length of Stay,Total Price\n")
            for row in clientCSVCursor.execute("SELECT receiptID, firstName, lastName, sex, startDate, endDate, lengthOfStay, totalPrice FROM receipts WHERE type = 'client' ORDER By endDate DESC, receiptID DESC"):
                for i in range(len(row)):
                    file.write(str(row[i]) + ",")
                file.write('\n')

        # ALL SEMINAR DATA
        seminarDataCursor = connection.cursor()
        seminarData = seminarDataCursor.execute("SELECT receiptID, company, startDate, endDate, lengthOfStay, pricePerDayWithoutTax FROM receipts WHERE type = 'seminar' ORDER BY endDate DESC, receiptID DESC")
        seminarData = seminarDataCursor.fetchall()
        seminarTableLength = len(seminarData)
        # Create Seminar CSV file to export data
        seminarCSVCursor = connection.cursor()
        with open(path.join(ROOT, 'seminarCSV.csv'), 'w') as file:
            file.write("Receipt Number, Company, Start Date, End Date, Duration, Price per Day (HT)\n")
            for row in seminarCSVCursor.execute("SELECT receiptID, company, startDate, endDate, lengthOfStay, pricePerDayWithoutTax FROM receipts WHERE type = 'seminar' ORDER BY endDate DESC, receiptID DESC"):
                for i in range(len(row)):
                    file.write(str(row[i]) + ",")
                file.write('\n')

        # Save and close cursors and db
        clientCountCursor.close()
        seminarCountCursor.close()
        clientDataCursor.close()
        clientCSVCursor.close()
        seminarDataCursor.close()
        seminarCSVCursor.close()
        clientRevCursor.close()
        seminarRevCursor.close()
        airbnbCursor.close()
        otherCursor.close()
        connection.commit()
        connection.close()

        # Send data to the stats page to render it
        return render_template("stats.html", revenues = revenues, sources = sources, clientData=clientData, clientTableLength=clientTableLength, seminarData=seminarData, seminarTableLength=seminarTableLength)
# To download the client CSV
@app.route('/getClientCSV')
def getClientCSV():
    return send_file(path.join(ROOT, 'clientCSV.csv'), as_attachment=True)
# To download the seminar CSV
@app.route('/getSeminarCSV')
def getSeminarCSV():
    return send_file(path.join(ROOT, 'seminarCSV.csv'), as_attachment=True)
# Delete client receipt entry on button click
@app.route("/deleteClient", methods=['POST'])
def deleteClient():
    if request.method == 'POST':
        # Get info on which user to delete
        entryData = request.form['deleteClient']
        entryDataSplit = entryData.split(" ")
        receiptID = entryDataSplit[0]
        totalPrice = entryDataSplit[1]

        # Delete from the db
        connection = sqlite3.connect(path.join(ROOT, "receipts.db"))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM receipts WHERE receiptID = ? AND totalPrice = ?", (receiptID, totalPrice))
        cursor.close()
        connection.commit()
        connection.close()

        # Reload page
        return redirect("/stats")
# Delete seminar receipt entry on button click
@app.route("/deleteSeminar", methods=['POST'])
def deleteSeminar():
    if request.method == 'POST':
        # Get info on which user to delete
        entryData = request.form['deleteSeminar']
        entryDataSplit = entryData.split(" ")
        receiptID = entryDataSplit[0]
        lengthOfStay = entryDataSplit[1]

        # Delete from the db
        connection = sqlite3.connect(path.join(ROOT, "receipts.db"))
        cursor = connection.cursor()
        cursor.execute("DELETE FROM receipts WHERE receiptID = ? AND lengthOfStay = ?", (receiptID, lengthOfStay))
        cursor.close()
        connection.commit()
        connection.close()

        # Reload page
        return redirect("/stats")

