from flask import Flask, jsonify
from flask import render_template
from flask import request
from flask import session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
from flask_wtf.csrf import CSRFProtect
from flask import flash
import pyexcel
import os

from config import DevelopmentConfig

UPLOAD_FOLDER = os.path.abspath("../proyecto nuevo/")

from models import db, User
from flask import url_for
from flask import redirect

import forms

mail = Mail()

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
csrf = CSRFProtect()
mail.init_app(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/', methods=['GET','POST'])
def index():
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate(): 
        username = login_form.username.data
        success_message = 'Bienvenido {}'.format(username)
        password = generate_password_hash(login_form.password.data)
        flash(success_message)
        session['username'] = username
        return redirect(url_for('importar'))
    else:    
        return render_template('index.html', form = login_form)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('index'))

@app.route('/user/create', methods=['GET','POST'])
def create_user():
    create_form = forms.CreateUser(request.form)
    if request.method == 'POST' and create_form.validate():
        user = User(create_form.username.data,
                    create_form.email.data,
                    create_form.password.data)

        db.session.add(user)
        db.session.commit()            
        success_message = "Usuario registrado correctamente"
        flash(success_message)
    else:    
        return render_template('create_user.html', form = create_form)



@app.route('/import', methods=['GET', 'POST'])
def importar():
    import_excel = forms.ImportExcel(request.form)
    if request.method == 'POST':
        archivo = request.files["archivo"]
        nombre_archivo = archivo.filename
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo))
        success_message = 'Tu archivo a sido subido exitosamente'
        flash(success_message)
        leidos = pyexcel.get_sheet(file_name=nombre_archivo, name_columns_by_row=0)
        cantidad_lineas = []
        contador = 0
        for leido in leidos:
            cantidad_lineas.append(contador)
            contador = contador+1
        return render_template("table.html", datos = leidos, cantidad = cantidad_lineas)
    else:    
        return render_template('importar.html', form = import_excel)

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    if request.method == 'POST':
        cantidad = request.form['cantidad']
        cantidades = []
        archivo_lista = open("bdd.txt", "w")
        for canti in cantidad:
            if canti != "[" and canti != "]" and canti != "," and canti != " ":
                canti = int(canti)
                cantidades.append(canti)
        for cantidad in cantidades:
            nombre = request.form["nombre"+str(cantidad)]
            apellido = request.form["apellido"+str(cantidad)]
            telefono = request.form["phone"+str(cantidad)]
            archivo_lista.write(nombre+",")
            archivo_lista.write(apellido+",")
            archivo_lista.write(telefono+"\n")      
        return "hasta acá"

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        nombre = request.form["name"]
        print(nombre)
        return render_template('contact.html')
    else:    
        if 'username' in session:
            return render_template('contact.html')

if __name__=='__main__':
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        db.create_all()
    app.run()