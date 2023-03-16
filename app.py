import os
from flask import Flask,flash, request, render_template, redirect,url_for
import urllib.request
import mysql.connector
from werkzeug.utils import secure_filename
import datetime
# from app import preencode

app = Flask(__name__,template_folder='template')
# results = []
# cols = ("S_id","S_Name","Arrival_Time","Date") 
UPLOAD_FOLDER = 'images/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Connect to the database
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#CREATE A DATABASE IN YOUR MYSQL WORKBENCH AND MAKE A CONNECTION
conn = mysql.connector.connect(host='localhost',
                                            database='$DATABASE',
                                            user='$USER',
                                            password='$PASSWORD')
cursor = conn.cursor(buffered=True)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image():
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Image successfully uploaded')
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        # Get the user input from the form
        user_input1 = request.form['name']
        user_input2 = request.form['roll']

        # Save the user input in the database
        mySql_insert_query = """INSERT INTO details (Roll_No,S_Name) VALUES (%s,%s) """ #CREATE DETAILS table in your database
        records = (user_input2,user_input1)
        cursor.execute(mySql_insert_query,records)
        conn.commit()
        upload_image()

    # Render the HTML template and pass it the user inputs from the database
    cursor.execute("SELECT Roll_No FROM details")
    user_inputs = cursor.fetchall()
    return render_template('index.html', user_inputs=user_inputs)

@app.route('/home.html', methods=['GET','POST'])
def home():
    date = request.form.get("date")
    mySql_insert_query = """SELECT * FROM date WHERE Date= %s """ #CREATE DATE table in your database
    # record = date
    cursor.execute(mySql_insert_query,(date,))
    conn.commit()
    # global results
    res = ()
    list1 = []
    list2= []
    list3 = []
    list4 = []
    results = cursor.fetchall()
    for i in results:
        res = res+i
    for i in res:
        if type(i) is int:
            list1.append(i)
        elif type(i) is str:
            list2.append(i)
        elif type(i) is datetime.timedelta:
            list3.append(str(i))
        elif type(i) is datetime.date:
            list4.append(str(i))        
    return render_template('home.html', count=len(list1),result1=list1,result2=list2,result3=list3,result4=list4)
        

@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)
if __name__ == '__main__':
    app.run()
