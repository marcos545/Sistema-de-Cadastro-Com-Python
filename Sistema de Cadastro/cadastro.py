from flask import Flask, render_template, redirect, request, session
import mysql.connector, bcrypt,secrets
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="cursoflask",
    database="curso"
)       
cursor = db.cursor()

@app.route("/")
def inicio():
    if 'id' in session:
        usuario = session['usuario']
        cursor.execute("SELECT * FROM tarefas WHERE idusuario = %s", (session['id'],))
        resultado = cursor.fetchall()
        return render_template("inicio.html", usuario=usuario, tarefas=resultado)
    return redirect("/loguin")

@app.route("/loguin", methods=['GET', 'POST'])
def loguin():
    if 'id' in session:
      return redirect("/")

    if request.method == "POST":
        usuario = request.form['usuario']
        senha = request.form['senha']
         
        if not usuario or not senha:
            return render_template("loguin.html", erro="prencha todos os campos.")
        
        cursor.execute("SELECT id, usuario, senha FROM usuarios WHERE usuario = %s", (usuario,))       
        resultado = cursor.fetchone()

        if resultado and bcrypt.checkpw(senha.encode("utf-8"), resultado[2].encode("utf-8")):
            session['id'] = resultado[0]
            session['usuario'] = resultado[1]

            return redirect("/")
      
        return render_template("loguin.html", erro="usuario ou senha invalida")

    return render_template("loguin.html")    

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    if 'id' in session:
     return redirect("/")
   
    if request.method =="POST":
        usuario = request.form['usuario']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar']

        if not usuario or not senha or not confirmar_senha:
           return render_template("cadastro.html", erro="prencha todos os campos")  

        if senha != confirmar_senha:
            return   render_template("cadastro.html", erro="as senhas não conferem favor tentar novamente!")


        cursor.execute("SELECT id FROM usuarios WHERE usuario = %s",(usuario,))
        resultado = cursor.fetchone()
        if resultado:
            return render_template("cadastro.html", erro="usuario Já Existe")

        salt = bcrypt.gensalt()
        nova_senha = bcrypt.hashpw(senha.encode("utf-8"), salt)
        sql ="INSERT INTO usuarios(usuario, senha) VALUES (%s, %s)"
        valores = (usuario, nova_senha)
        cursor.execute(sql, valores)
        db.commit()

        return redirect("/loguin")
    
    return render_template("cadastro.html")


@app.route("/add_tarefa", methods=['GET', 'POST'])
def add_tarefa():
    if 'id' not  in session:
        return redirect("/loguin")
    
    if request.method == "POST":
        nome = request.form['nome']
        descricao = request.form['descricao']

        if not nome or not descricao:
            return render_template("inicio.html", erro="prencha todos os campos")  

        
        sql ="INSERT INTO tarefas (nome, descricao, idusuario) VALUES (%s, %s, %s)"
        valores = (nome, descricao, session['id'])
        cursor.execute(sql, valores)
        db.commit()

        return redirect("/")

    return render_template("inicio.html")

@app.route("/editar_tarefa/<int:id>", methods =['GET', 'POST'])
def editar_tarefa(id):
    if request.method =="GET":
        cursor.execute("SELECT nome, descricao FROM tarefas WHERE id=%s", (id,))
        resultado = cursor.fetchone()
        nome = resultado[0]
        descricao = resultado[1]

        return render_template("editar_tarefa.html", nome=nome, descricao=descricao)
    return redirect("/")

@app.route("/excluir_tarefa/<int:id>")
def excluir_tarefa(id):
    if 'id' not in session:
        redirect("/loguin")

    sql ="DELETE FROM tarefas WHERE id = %s"
    valores = (id,)
    cursor.execute(sql, valores)
    db.commit()

    return redirect("/")    


@app.errorhandler(404)
def não_encontrada(e):
   return redirect("/loguin")

@app.route("/logout")
def logout():
    session.pop('id', None)
    session.pop('usuario', None)
    return redirect("/")

app.run()