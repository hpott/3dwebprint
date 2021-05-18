from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
import sqlite3 as sql
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)

      
@app.route('/')
def homepage():
   return render_template('index.html')

@app.route('/print')
def upload():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']

      if '.stl' in f.filename:
         
         f.save('uploads/'+f.filename)
         name = request.form.get("username")
         quality = request.form.get("quality")

         #Insert values into database
         with sql.connect("printer.db") as db:
            head = db.cursor()
            head.execute("INSERT INTO files (name,quality,filename) VALUES (?,?,?)", (name,quality,f.filename))
            db.commit()
         return 'file uploaded successfully. <a href=/upload>go back</a> or <a href=/files>list files</a>'
      else:
         return 'not an STL file. try again. <a href=/upload>go back</a>'

@app.route('/files', methods = ['GET', 'POST'])
def list_files():
   if request.method == 'POST':
      if request.form['password'] == 'password' and request.form['username'] == 'admin':
         session['loggedin'] = True
         return redirect(url_for('list_files'))

   #   elif session['loggedin']:
         
        # db  = sql.connect("printer.db")
        # head = db.cursor()
        # head.execute("select * from files") 
        # rows=head.fetchall()
        # print(rows)
        # return render_template('list.html', data=rows)
      else:
         return "password incorrect"
   else:
      if not 'loggedin' in session:
         return render_template('login.html')
      else:
         db  = sql.connect("printer.db")
         head = db.cursor()
         head.execute("select * from files") 
         rows=head.fetchall()
         print(rows)
         return render_template('list.html', data=rows)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   return redirect(url_for('list_files'))
      

@app.route('/download/<filename>', methods = ['GET'])
def download_file(filename):
 #  uploads = os.path.join(current_app.root_path, 'uploads')
   return send_from_directory(directory='./uploads/', filename=filename)

@app.route('/delete/<filename>')
def delete_file(filename):
   with sql.connect("printer.db") as db:
      head = db.cursor()
      head.execute("DELETE FROM files WHERE filename = '"+filename+"'")
      db.commit()
   os.remove("./uploads/"+filename)
   return redirect(url_for('list_files'))
   
   
      
		
if __name__ == '__main__':
   app.run(debug = True)
