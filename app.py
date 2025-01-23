from flask import Flask, json, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
import bcrypt
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import WebsiteSearchTool, SerperDevTool
import MySQLdb.cursors 
import markdown2
from flask import send_file
from functools import wraps
from pathlib import Path
import markdown2
import pdfkit
from langchain_openai import ChatOpenAI
from openai import OpenAI
import requests


os.environ["OPENAI_API_KEY"] = ""
os.environ["SERPER_API_KEY"] = "966f510dc332f3fc6db2bb39af3e4c90685ccb50" # serper.dev API key


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

web_search_tool = WebsiteSearchTool()
serper_tool = SerperDevTool()

gpt_4_mini = ChatOpenAI(
    model = "gpt-4o-mini",
    openai_api_key=os.environ["OPENAI_API_KEY"]
)

llama = ChatOpenAI(
    model = "ollama/llama3.1:8b",
    openai_api_key="sk-proj-1111",
    base_url ="http://localhost:11434"
)

gemma = ChatOpenAI(
    model = "ollama/gemma",
    openai_api_key="sk-proj-1111",
    base_url ="http://localhost:11434"
)

mistral = ChatOpenAI(
    model = "ollama/mistral",
    openai_api_key="sk-proj-1111",
    base_url ="http://localhost:11434"
)


# Configurações do MySQL
app.config['MYSQL_HOST'] = 'mysql10-farm1.kinghost.net'
app.config['MYSQL_USER'] = 'trettel_add1'
app.config['MYSQL_PASSWORD'] = 'WtBL1mvM8Yd'
app.config['MYSQL_DB'] = 'trettel'

mysql = MySQL(app)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email já cadastrado!')
        else:
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed))
            mysql.connection.commit()
            flash('Registro bem-sucedido! Agora você pode fazer login.')
            return redirect(url_for('login'))
        cur.close()
    return render_template('opening/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass'].encode('utf-8')

        cur = mysql.connection.cursor()
        cur.execute("SELECT name, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password, user[1].encode('utf-8')):  
            session['user_name'] = user[0]  
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.')
            

    return render_template('opening/login.html')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_name' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.pop('user_name', None) 
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/index.html', user_name=session.get('user_name'))

CORS(app)  # Habilita CORS para todas as rotas


# Rota para verificar os emails 
@app.route('/CheckEmailSurvey', methods=['POST'])
@login_required
def verificar_email_survey():
    try:
        email_survey_pairs = request.get_json()

        if not email_survey_pairs or not isinstance(email_survey_pairs, list):
            return jsonify({"error": "Nenhum email e id_survey fornecidos ou formato incorreto"}), 400

        cur = mysql.connection.cursor()

        email_survey_tuples = [(pair['email'], pair['id_survey']) for pair in email_survey_pairs]

        if not email_survey_tuples:
            return jsonify({"existingEmailSurveyPairs": []}), 200

        query = """
            SELECT email, id_survey FROM form
            WHERE (email, id_survey) IN (%s)
        """ % ','.join(['(%s, %s)'] * len(email_survey_tuples))

        cur.execute(query, sum(email_survey_tuples, ()))
        existing_pairs = [f"{row[0]}-{row[1]}" for row in cur.fetchall()]
        cur.close()

        return jsonify({"existingEmailSurveyPairs": existing_pairs}), 200

    except Exception as e:
        print(f"Erro ao verificar emails e id_survey: {e}")
        return jsonify({"error": "Erro ao verificar emails e id_survey"}), 500



@app.route('/add_survey', methods=['POST'])
@login_required
def add_survey():
    try:
        data = request.get_json()
        id_survey = data.get('id_survey')

        if id_survey:
            cursor = mysql.connection.cursor()
            
            # Insere o ID do survey no banco de dados
            query = "INSERT INTO surveys (id_survey) VALUES (%s)"
            cursor.execute(query, (id_survey,))
            
            # Confirma a transação
            mysql.connection.commit()
            
            cursor.close()
            
            return jsonify({"success": f"Survey ID {id_survey} adicionado com sucesso!"}), 200
        else:
            return jsonify({"error": "ID do Survey não fornecido"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
        
@app.route('/get_surveys', methods=['GET'])
def get_surveys():
    try:

        query = "SELECT id_survey FROM surveys"
        cursor = mysql.connection.cursor()
        cursor.execute(query)
        surveys = cursor.fetchall() 

        survey_list = [{"id_survey": row[0]} for row in surveys]
        return jsonify(survey_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Rota para salvar no banco de dados
@app.route('/SaveDataForm', methods=['POST'])
@login_required
def salvar_dados():
    try:
        dados = request.get_json()

        cur = mysql.connection.cursor()

        for row in dados:
            id_survey = row['surveyId']  
            empresa = row['empresa']
            email = row['email']
            respostas = row['respostas']
            pergunta1 = respostas.get('pergunta1', '')
            pergunta2 = respostas.get('pergunta2', '')
            pergunta3 = respostas.get('pergunta3', '')
            pergunta4 = respostas.get('pergunta4', '')
            pergunta5 = respostas.get('pergunta5', '')
            pergunta6 = respostas.get('pergunta6', '')
            pergunta7 = respostas.get('pergunta7', '')
            pergunta8 = respostas.get('pergunta8', '')
            pergunta9 = respostas.get('pergunta9', '')
            pergunta10 = respostas.get('pergunta10', '')

            query = """
                INSERT INTO form (id_survey, empresa, email, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (id_survey, empresa, email, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Dados salvos com sucesso!"}), 200
    except Exception as e:
        print(f"Erro ao salvar os dados: {e}")
        return jsonify({"error": "Erro ao salvar dados"}), 500


@app.route('/getDataForm', methods=['GET'])
@login_required
def get_formulario_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_survey, empresa, email, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10 FROM form")
        dados = cur.fetchall()
        cur.close()

        
        resultado = []
        for id_survey, empresa, email, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10 in dados:
            resultado.append({
                'id_survey': id_survey,
                'empresa': empresa,
                'email': email,
                'respostas': {
                    'pergunta1': pergunta1,
                    'pergunta2': pergunta2,
                    'pergunta3': pergunta3,
                    'pergunta4': pergunta4,
                    'pergunta5': pergunta5,
                    'pergunta6': pergunta6,
                    'pergunta7': pergunta7,
                    'pergunta8': pergunta8,
                    'pergunta9': pergunta9,
                    'pergunta10': pergunta10
                }
            })

        return jsonify(resultado), 200
    except Exception as e:
        print(f"Erro ao buscar dados do formulario: {e}")
        return jsonify({"error": "Erro ao buscar dados"}), 500

    

@app.route('/questionarios')
@login_required
def listar_empresas():
    try:
        cur = mysql.connection.cursor()


        cur.execute("SELECT DISTINCT empresa, crew, pdf FROM form")
        resultados = cur.fetchall()
        cur.close()

        enviados = [empresa for empresa, crew, pdf in resultados if crew == 1 and pdf == 1]
        pendentes = [empresa for empresa, crew, pdf in resultados if crew == 0 and pdf == 0]
        pdf_baixado = [empresa for empresa, crew, pdf in resultados if pdf == 1 and crew == 1]
        pdf_pendente = [empresa for empresa, crew, pdf in resultados if pdf == 0 and crew == 1]

        return render_template('dashboard/questionarios.html', pdf_baixado=pdf_baixado, pdf_pendente=pdf_pendente, enviados=enviados, pendentes=pendentes, user_name=session.get('user_name'))

    except Exception as e:
        print(f"Erro ao listar empresas: {e}")
        return jsonify({"error": "Erro ao listar empresas"}), 500




@app.route('/empresa')
@login_required
def empresa():
    nome_empresa = request.args.get('nome', 'Empresa não informada')
    
    try:
        cur = mysql.connection.cursor()

        # Buscando todos os formulários associados à empresa, incluindo a coluna 'crew'
        cur.execute("""
            SELECT id_survey, email, pergunta1, pergunta2, pergunta3, pergunta4, pergunta5, pergunta6, pergunta7, pergunta8, pergunta9, pergunta10, crew, pdf
            FROM form
            WHERE empresa = %s
        """, (nome_empresa,))
        formularios = cur.fetchall()
        cur.close()

        if formularios:
            return render_template('dashboard/empresa.html', empresa=nome_empresa, formularios=formularios, user_name=session.get('user_name'))
        else:
            return redirect('/dashboard')

    except Exception as e:
        print(f"Erro ao buscar dados para a empresa: {e}")
        return jsonify({"error": "Erro ao buscar dados para a empresa"}), 500


@app.route('/editar_formulario/<string:formulario_id>/<string:email>', methods=['POST'])
@login_required
def editar_formulario(formulario_id, email):
    try:
        dados = request.form
        respostas_atualizadas = {
            'pergunta1': dados.get('pergunta1', ''),
            'pergunta2': dados.get('pergunta2', ''),
            'pergunta3': dados.get('pergunta3', ''),
            'pergunta4': dados.get('pergunta4', ''),
            'pergunta5': dados.get('pergunta5', ''),
            'pergunta6': dados.get('pergunta6', ''),
            'pergunta7': dados.get('pergunta7', ''),
            'pergunta8': dados.get('pergunta8', ''),
            'pergunta9': dados.get('pergunta9', ''),
            'pergunta10': dados.get('pergunta10', '')
        }

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE form
            SET pergunta1 = %s, pergunta2 = %s, pergunta3 = %s, pergunta4 = %s,
                pergunta5 = %s, pergunta6 = %s, pergunta7 = %s, pergunta8 = %s,
                pergunta9 = %s, pergunta10 = %s
            WHERE id_survey = %s AND email = %s
        """, (*respostas_atualizadas.values(), formulario_id, email))

        mysql.connection.commit()
        cur.close()


        return redirect(url_for('empresa', nome=dados['empresa']))  

    except Exception as e:
        print(f"Erro ao atualizar o formulário: {e}")
        return redirect(url_for('empresa', nome=dados['empresa']))
    
@app.route('/nova_resposta', methods=['GET', 'POST'])
@login_required
def nova_resposta():
    return render_template('dashboard/formulario.html', user_name=session.get('user_name'))

@app.route('/novo_formulario', methods=['GET', 'POST'])
@login_required
def novo_formulario():
    if request.method == 'POST':
        empresa = request.form.get('empresa')
        email = request.form.get('email')
        resposta = request.form.get('resposta')
        crew = 0
        pdf = 0
        id_survey = 0

        # Conecta ao banco e salva os dados
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO form (id_survey, empresa, email, crew, pdf, pergunta1)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_survey, empresa, email, crew, pdf, resposta))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('listar_empresas'))
        except Exception as e:
            print(f"Erro ao salvar o formulário: {e}")
            return redirect(url_for('novo_formulario'))
    
    return render_template('questionarios.html')



@app.route('/create_crew', methods=['GET', 'POST'])
@login_required
def create_crew():
    return render_template('dashboard/create_crew.html', user_name=session.get('user_name'))


@app.route('/crew_manager', methods=['GET', 'POST'])
@login_required
def crew_manager():
    cursor = mysql.connection.cursor()
    
    # Buscar agentes
    cursor.execute("SELECT name_agent FROM agents")
    agentes = cursor.fetchall()
    
    # Buscar tarefas
    cursor.execute("SELECT name_task FROM tasks")
    tarefas = cursor.fetchall()
    
    # Buscar crews
    cursor.execute("SELECT name_crew FROM crews")
    crews = cursor.fetchall()
    print(crews)
    print(agentes)
    print(tarefas)
    
    cursor.close()

    # Renderizar o template com as listas dinâmicas
    return render_template('dashboard/crew_manager.html', agentes=agentes, tarefas=tarefas, crews=crews, user_name=session.get('user_name'))


@app.route('/LoadCrews', methods=['GET'])
@login_required
def load_crews():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT name_crew FROM crews")  
        crews = cur.fetchall()
        cur.close()

        # Retornar os nomes dos crews em formato JSON
        return jsonify([crew[0] for crew in crews]), 200
    except Exception as e:
        print(f"Erro ao buscar crews: {e}")
        return jsonify({"error": "Erro ao buscar crews"}), 500


@app.route('/LoadAgents', methods=['GET'])
@login_required
def load_agents():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_agent, name_agent, role_agent, backstory_agent, goal_agent FROM agents")  
        agents = cur.fetchall()
        cur.close()

        # Cria um dicionário para cada agente
        agents_list = [{
            'id': agent[0],
            'name': agent[1],
            'role': agent[2],
            'backstory': agent[3],
            'goal': agent[4]
        } for agent in agents]

        return jsonify(agents_list), 200
    except Exception as e:
        print(f"Erro ao buscar agentes: {e}")
        return jsonify({"error": "Erro ao buscar agentes"}), 500

@app.route('/LoadTasks', methods=['GET'])
@login_required
def load_tasks():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_task, name_task, description_task, expected_output_task, agent_task FROM tasks")  
        tasks = cur.fetchall()
        cur.close()

        # Cria um dicionário para cada tarefa
        tasks_list = [{
            'id': task[0],
            'name': task[1],
            'description': task[2],
            'expected_output': task[3],
            'agent_task': task[4] 
        } for task in tasks]

        return jsonify(tasks_list), 200
    except Exception as e:
        print(f"Erro ao buscar tarefas: {e}")
        return jsonify({"error": "Erro ao buscar tarefas"}), 500


@app.route('/SaveTask', methods=['POST'])
@login_required
def save_task():
    try:
        data = request.get_json()

        print(data)
        name_task = data['name_task']
        description_task = data['description_task']
        expected_output_task = data['expected_output_task']
        agent_task = data['agent_task']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO tasks (name_task, description_task, expected_output_task, agent_task)
            VALUES (%s, %s, %s, %s)
        """, (name_task, description_task, expected_output_task, agent_task))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Tarefa salva com sucesso!"}), 201

    except Exception as e:
        print(f"Erro ao salvar a tarefa: {e}")
        return jsonify({"error": "Erro ao salvar a tarefa."}), 500
    
@app.route('/SaveAgent', methods=['POST'])
@login_required
def save_agent():
    try:
        data = request.get_json()

        if not all(key in data for key in ['name_agent', 'role_agent', 'backstory_agent', 'goal_agent']):
            return jsonify({"error": "Dados insuficientes para salvar o agente."}), 400

        name_agent = data['name_agent']
        role_agent = data['role_agent']
        backstory_agent = data['backstory_agent']
        goal_agent = data['goal_agent']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO agents (name_agent, role_agent, backstory_agent, goal_agent)
            VALUES (%s, %s, %s, %s)
        """, (name_agent, role_agent, backstory_agent, goal_agent))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Agente salvo com sucesso!"}), 201

    except Exception as e:
        print(f"Erro ao salvar o agente: {e}")
        return jsonify({"error": "Erro ao salvar o agente."}), 500
    

@app.route('/SaveCrew', methods=['POST'])
@login_required
def save_crew():
    try:
        data = request.get_json()

        if not all(key in data for key in ['name_crew', 'agents_crew', 'tasks_crew', 'agent_count', 'task_count', 'llm_crew']):
            return jsonify({"error": "Dados insuficientes para salvar o crew."}), 400

        name_crew = data['name_crew']
        agents_crew = data['agents_crew']  
        tasks_crew = data['tasks_crew']    
        quantity_agents = data['agent_count']  
        quantity_tasks = data['task_count']    
        llm = data['llm_crew']  

        agent_ids = []
        cur = mysql.connection.cursor()
        for agent_name in agents_crew: 
            cur.execute("SELECT id_agent FROM agents WHERE name_agent = %s", (agent_name,))
            result = cur.fetchone()
            if result:
                agent_ids.append(result[0]) 
            else:
                return jsonify({"error": f"Agente '{agent_name}' não encontrado."}), 400


        task_ids = []
        for task_name in tasks_crew: 
            cur.execute("SELECT id_task FROM tasks WHERE name_task = %s", (task_name,))
            result = cur.fetchone()
            if result:
                task_ids.append(result[0]) 
            else:
                return jsonify({"error": f"Tarefa '{task_name}' não encontrada."}), 400

        cur.execute("""
            INSERT INTO crews (name_crew, quantity_agents, quantity_tasks, llm)
            VALUES (%s, %s, %s, %s)
        """, (name_crew, quantity_agents, quantity_tasks, llm))

        crew_id = cur.lastrowid  
        

        for agent_id in agent_ids:
            cur.execute("INSERT INTO crew_agent (crew_id, agent_id) VALUES (%s, %s)", (crew_id, agent_id))


        for task_id in task_ids:
            cur.execute("INSERT INTO crew_task (crew_id, task_id) VALUES (%s, %s)", (crew_id, task_id))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Crew salvo com sucesso!"}), 201

    except Exception as e:
        print(f"Erro ao salvar crew: {e}")
        return jsonify({"error": "Erro ao salvar crew."}), 500


@app.route('/enviar_crew/<string:form_id>/<string:email>', methods=['POST'])
@login_required
def enviar_crew(form_id, email):
    try:
        data = request.get_json()
        respostas= data.get('respostas', {})  
        crew_name = data.get('crew_name') 

        cur = mysql.connection.cursor()
        cur.execute("UPDATE form SET crew = 1 WHERE id_survey = %s AND email = %s", (form_id, email))
        mysql.connection.commit()
        cur.close()

        # Envia tudo pra executar no crew
        if crew_name:
            return jsonify({
                "success": True, 
                "redirect_to": url_for(
                    'start_crew', 
                    crew_name=crew_name, 
                    respostas=json.dumps(respostas),
                    id_survey=form_id, 
                    email=email 
                )
            }), 200

        return jsonify({"success": True}), 200

    except Exception as e:
        print(f"Erro ao enviar para crew: {e}")
        return jsonify({"error": "Erro ao enviar para crew"}), 500
    
        

@app.route('/crew')
@login_required
def crew():
    crew_name = request.args.get('name', 'Crew não informado')
    
    try:
        cur = mysql.connection.cursor()

        # Buscando todos os dados relacionados ao crew
        cur.execute("""
            SELECT id_crew, name_crew, quantity_agents, quantity_tasks, llm FROM crews
            WHERE name_crew = %s
        """, (crew_name,))
        crew_info = cur.fetchone()

        if not crew_info:
            return redirect('/dashboard')

        crew_id, name_crew, quantity_agents, quantity_tasks, llm = crew_info

       # Buscando os IDs dos agentes
        cur.execute("""
            SELECT a.id_agent 
            FROM agents a
            INNER JOIN crew_agent ca ON a.id_agent = ca.agent_id
            WHERE ca.crew_id = %s
        """, (crew_id,))
        agents = [row[0] for row in cur.fetchall()]  # Coleta os IDs dos agentes

        # Buscando os IDs das tarefas
        cur.execute("""
            SELECT t.id_task 
            FROM tasks t
            INNER JOIN crew_task ct ON t.id_task = ct.task_id
            WHERE ct.crew_id = %s
        """, (crew_id,))
        tasks = [row[0] for row in cur.fetchall()]  # Coleta os IDs das tarefas


        cur.close()
        return render_template('dashboard/crew.html', user_name=session.get('user_name'), crew_info={
            "name": name_crew,
            "quantity_agents": quantity_agents,
            "quantity_tasks": quantity_tasks,
            "agents": agents,
            "tasks": tasks,
            "llm": llm,
        })

    except Exception as e:
        print(f"Erro ao buscar dados do crew: {e}")
        return jsonify({"error": "Erro ao buscar dados do crew"}), 500



@app.route('/editar_crew', methods=['POST'])
@login_required
def editar_crew():
    try:
        data = request.get_json()

        name_crew = data['name_crew']
        agents_crew = data['agents_crew']
        tasks_crew = data['tasks_crew']
        quantity_agents = data['agent_count']
        quantity_tasks = data['task_count']
        llm = data['llm']

        cur = mysql.connection.cursor()
        
        cur.execute("SELECT id_crew FROM crews WHERE name_crew = %s", (name_crew,))
        result = cur.fetchone()

        if not result:
            return jsonify({"error": "Crew não encontrado."}), 404

        crew_id = result[0]

        # Atualizando a quantidade de agentes e tarefas
        cur.execute("""
            UPDATE crews 
            SET quantity_agents = %s, quantity_tasks = %s, llm = %s 
            WHERE id_crew = %s
        """, (quantity_agents, quantity_tasks, llm, crew_id))

        # Buscando IDs dos agentes selecionados
        agent_ids = []
        for id_agent in agents_crew:
            cur.execute("SELECT id_agent FROM agents WHERE id_agent = %s", (id_agent,))
            result = cur.fetchone()
            if result:
                agent_ids.append(result[0])
            else:
                return jsonify({"error": f"Agente '{id_agent}' não encontrado."}), 400

        # Buscando IDs das tarefas selecionadas
        task_ids = []
        for id_task in tasks_crew:
            cur.execute("SELECT id_task FROM tasks WHERE id_task = %s", (id_task,))
            result = cur.fetchone()
            if result:
                task_ids.append(result[0])
            else:
                return jsonify({"error": f"Tarefa '{id_task}' não encontrada."}), 400

        # Apagando relações antigas de agentes e tarefas
        cur.execute("DELETE FROM crew_agent WHERE crew_id = %s", (crew_id,))
        cur.execute("DELETE FROM crew_task WHERE crew_id = %s", (crew_id,))

        # Inserindo novas relações de agentes
        for agent_id in agent_ids:
            cur.execute("INSERT INTO crew_agent (crew_id, agent_id) VALUES (%s, %s)", (crew_id, agent_id))

        # Inserindo novas relações de tarefas
        for task_id in task_ids:
            cur.execute("INSERT INTO crew_task (crew_id, task_id) VALUES (%s, %s)", (crew_id, task_id))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Crew atualizado com sucesso!"}), 200

    except Exception as e:
        print(f"Erro ao editar crew: {e}")
        return jsonify({"error": "Erro ao editar crew."}), 500


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


conversations = []
user_email = None
answers = {} 
current_question = 1  


@app.route("/chat", methods=["GET", "POST"])
def chat():
    global user_email, answers, current_question

    if request.method == "GET":
        return render_template("dashboard/chat.html", user_name=session.get('user_name'))

    if request.is_json:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "Mensagem não pode estar vazia."}), 400

        # Solicitar e armazenar o e-mail na primeira interação
        if user_email is None:
            if "@" in user_message and "." in user_message:  # Validação básica de e-mail
                user_email = user_message.strip()
                conversations.append({"role": "user", "content": user_message})
                conversations.append({"role": "assistant", "content": "Obrigado! Quais as características do seu negócio atual?"})
                return jsonify({"response": "Obrigado! Quais as características do seu negócio atual?"}), 200
            else:
                return jsonify({"response": "Olá! Primeiramente, qual seu e-mail?"}), 200

        # Lógica de interação dinâmica com reformulação
        if current_question <= 3:
            if user_message.lower() == "sim":
                # Confirmar a resposta reformulada e avançar para a próxima pergunta
                answers[f"pergunta{current_question}"] = conversations[-1]["content"]
                current_question += 1
                next_question = get_next_question(current_question)
                return jsonify({"response": next_question}), 200

            elif f"pergunta{current_question}" not in answers:
                improved_response = improve_answer(user_message)

                # Armazenar reformulação no histórico da conversa
                conversations.append({"role": "user", "content": user_message})
                conversations.append({"role": "assistant", "content": improved_response})

                return jsonify({
                    "response": f"Podemos dizer então que a sua resposta é: '{improved_response}'. Essa resposta está clara e condizente com a sua empresa? Responda com 'sim' para confirmar ou ajuste conforme necessário."
                }), 200

            else:
                # Continuar iterando na reformulação da resposta
                improved_response = improve_answer(user_message)
                conversations.append({"role": "user", "content": user_message})
                conversations.append({"role": "assistant", "content": improved_response})

                return jsonify({
                    "response": f"Então agora é possível dizer que: '{improved_response}'. Ajuste novamente ou confirme com 'sim'."
                }), 200

        # Identificar o comando /enviar
        if user_message.strip().lower() == "/enviar":
            conversations.append({"role": "user", "content": user_message})
            print(answers)

            crew_name = "Crew1"
            if crew_name:
                return jsonify({
                    "success": True,
                    "redirect_to": url_for(
                        'start_crew',
                        crew_name=crew_name,
                        respostas=json.dumps(answers),
                        id_survey=0,
                        email=user_email
                    )
                }), 200

        return jsonify({"response": "Por favor, continue respondendo às perguntas."}), 200

    return jsonify({"error": "Requisição inválida."}), 400



def improve_answer(answer):
    """
    Reformular e melhorar a resposta fornecida pelo usuário, utilizando `chat.completions.create`.
    """
    try:
        chat_completion = openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Você é um assistente que melhora e entende respostas para torná-las mais claras, objetivas e profissionais."},
                {"role": "user", "content": f"Recebi a seguinte resposta: '{answer}'. Melhore-a para que fique mais clara, objetiva e profissional, mantendo o contexto."}
            ],
            model="gpt-4o-mini",
            max_tokens=100
        )

        # Extraindo a mensagem do objeto retornado
        reformulated_answer = chat_completion.choices[0].message.content.strip()

        return reformulated_answer
    except Exception as e:
        print(f"Erro ao melhorar a resposta: {e}")
        return "Desculpe, ocorreu um erro ao tentar reformular sua resposta. Por favor, tente novamente."

def get_next_question(question_number):
    """
    Retornar a próxima pergunta com base no número atual.
    """
    questions = {
        1: "Quais as características do seu negócio atual?",
        2: "Quais são as principais competências nas quais sua empresa se destaca?",
        3: "Informe as palavras-chave da área que gostaria de buscar oportunidades de novos negócios.",
    }
    return questions.get(question_number, "Obrigado! Agora digite /enviar para enviar ao Crew.")



############################################################################################



def get_crew_id_by_name(crew_name):
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT id_crew, llm FROM crews WHERE name_crew = %s", (crew_name,))
    crew = cursor.fetchone()
    cursor.close()
    
    if crew:
        return {"id_crew": crew[0], "llm": crew[1]}
    else:
        print(f"Nenhum crew encontrado com o nome: {crew_name}")
        return None

def get_agents_for_crew(crew_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 

    crew_data = get_crew_id_by_name(crew_name)
    if crew_data is None:
        return []

    crew_id = crew_data['id_crew']
    
    if crew_id is None:
        print(f"Nenhum crew encontrado com o nome: {crew_name}")
        return []
    
    cursor.execute("""
        SELECT a.id_agent, a.name_agent, a.role_agent, a.backstory_agent, a.goal_agent 
        FROM agents a
        INNER JOIN crew_agent ca ON a.id_agent = ca.agent_id
        WHERE ca.crew_id = %s
    """, (crew_id,))
    
    agents = cursor.fetchall()
    cursor.close()
    
    if not agents:
        print(f"Nenhum agente encontrado para o crew: {crew_name}")
    
    return agents

def get_tasks_for_crew(crew_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    
    crew_data = get_crew_id_by_name(crew_name)
    if crew_data is None:
        return []

    crew_id = crew_data['id_crew']
    
    if crew_id is None:
        print(f"Nenhum crew encontrado com o nome: {crew_name}")
        return []
    
    cursor.execute("""
        SELECT t.id_task, t.name_task, t.description_task, t.expected_output_task, t.agent_task
        FROM tasks t
        INNER JOIN crew_task ct ON t.id_task = ct.task_id
        WHERE ct.crew_id = %s
    """, (crew_id,))
    
    tasks = cursor.fetchall()
    cursor.close()
    
    if not tasks:
        print(f"Nenhuma tarefa encontrada para o crew: {crew_name}")
    
    return tasks

def create_agents_and_tasks_for_crew(crew_name):
    agents_data = get_agents_for_crew(crew_name)
    tasks_data = get_tasks_for_crew(crew_name)

    agents = []
    agents_map = {} 
    tasks = []
    
    llm_mapping = {
        'llama': llama,
        'gpt_4_mini': gpt_4_mini,  
        'gemma': gemma,             
        'mistral': mistral          
    }
    
    crew_data = get_crew_id_by_name(crew_name)
    llm_name = crew_data['llm']  
    llm_instance = llm_mapping[llm_name]
    
    # Cria agentes dinamicamente
    for agent_data in agents_data:
        # print(f"Criando agente com dados: {agent_data}")
        agent = Agent(
            role=agent_data['role_agent'],
            goal=agent_data['goal_agent'],
            backstory=agent_data['backstory_agent'],
            tools=[web_search_tool, serper_tool],
            verbose=True,
            memory=True,
            llm= llm_instance,
            max_tokens=20000,
            allow_delegation=False
        )
        agents.append(agent)
        agents_map[agent] = agent_data['name_agent'].strip().lower()

    # Cria tarefas dinamicamente
    task_output_files = []  # Lista para armazenar os caminhos dos arquivos de saída
    for task_data in tasks_data:
        agent_for_task = next(
            (a for a, name in agents_map.items() if name == task_data['agent_task'].strip().lower()), 
            None
        )
    
        if agent_for_task:
            # Define o caminho do arquivo .md para a tarefa
            task_output_file = f"outputs/{crew_name}_{task_data['name_task']}.md"
            task_output_files.append(task_output_file)  # Adiciona à lista de arquivos de saída
    
            # Cria a tarefa com o arquivo de saída configurado
            task = Task(
                description=task_data['description_task'],
                expected_output=task_data['expected_output_task'],
                agent=agent_for_task,
                async_execution=False,
                output_file=task_output_file  # Especifica o arquivo de saída
            )
            tasks.append(task)
        else:
            print(f"Nenhum agente encontrado para a tarefa: {task_data['name_task']}")

    return agents, tasks
    

def process_and_save_output(crew_name, id_survey, email):
    try:
        # Buscar todos os arquivos que começam com o nome do crew
        md_files = sorted(
            Path("outputs").glob(f"{crew_name}_*.md"),
            key=lambda x: getattr(x.stat(), 'st_birthtime', x.stat().st_ctime)  
        )

        if not md_files:
            raise FileNotFoundError(f"Nenhum arquivo correspondente ao padrão '{crew_name}_*.md' encontrado.")

        # Concatenar o conteúdo dos arquivos
        merged_content = ""
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as file:
                merged_content += file.read() + "\n\n"

        save_output_to_db(name_crew=crew_name, output=merged_content, id_survey=id_survey, email=email)

    except Exception as e:
        print(f"Erro ao processar e salvar os arquivos: {e}")
        raise

# Função para salvar o output na tabela output_crew
def save_output_to_db(name_crew, output, id_survey, email):
    cursor = None
    try:
        cursor = mysql.connection.cursor()
        query = "INSERT INTO output_crew (id_survey, email, name_crew, output) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (id_survey, email, name_crew, output))
        mysql.connection.commit()  
        print("Output foi salvo com sucesso no banco de dados.")
    except Exception as e:
        mysql.connection.rollback()  
        print(f"Erro ao salvar o output no banco de dados: {e}")
        raise
    finally:
        if cursor:
            cursor.close()

@app.route('/start_crew/<crew_name>', methods=['GET', 'POST'])
def start_crew(crew_name):
    try:
        respostas_json = request.args.get('respostas')
        id_survey = request.args.get('id_survey')  # Obtém o id_survey dos parâmetros
        email = request.args.get('email')  # Obtém o email da empresa dos parâmetros
        print(f"Email da empresa: {email}")
        print(f"Id_Survey do formulário: {id_survey}")
        if respostas_json:
            try:
                respostas = json.loads(respostas_json)
                print(f"Respostas recebidas para o crew {crew_name}:\n{respostas}\n\n")
            except json.JSONDecodeError as e:
                print(f"Erro ao fazer parse do JSON: {e}")
                return jsonify({"error": "Formato de JSON inválido"}), 400
        else:
            print("Nenhuma resposta recebida.")
            respostas = None
            
        agents, tasks = create_agents_and_tasks_for_crew(crew_name)
        crew_data = get_crew_id_by_name(crew_name)
        if crew_data is None:
            return []

        crew_llm = crew_data['llm']
        print(f"\nLLM utilizado: {crew_llm}\n")
        
        print(f"\nTasks recebidas: {tasks}\n\nAgentes recebidos: {agents}")
        if not agents or not tasks:
            print(f"Não foi possível criar agentes ou tarefas para o crew: {crew_name}")
            return jsonify({"error": "Erro ao criar agentes ou tarefas"}), 500

        # Cria o crew dinamicamente
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True,
            full_output=True,
			memory=True,
        	cache=True,
            process=Process.sequential  
        )

        try:
            result = crew.kickoff(respostas)
            print(f"Resultado do kickoff: {result}")
        except Exception as e:
            print(f"Erro ao executar kickoff: {e}")
            return jsonify({"error": "Erro ao executar crew kickoff"}), 500

        # Salva o resultado no banco de dados
        process_and_save_output(crew_name, id_survey, email)

        return redirect(url_for('listar_empresas'))

    except Exception as e:
        print(f"Erro ao iniciar o crew: {e}")
        return redirect(url_for('listar_empresas'))
        

def generate_pdf(id_survey, email, company_name, markdown_content, filename):
    # Converta Markdown para HTML
    html_content = markdown2.markdown(markdown_content)

    # Adicione a tag meta com codificação UTF-8 e o CSS para estilizar o conteúdo
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                margin: 30px;
                color: #333;
                line-height: 1.6;
            }}
            h1, h2, h3 {{
                font-weight: bold;
                color: #333;
            }}
            p {{
                font-size: 14px;
                margin-bottom: 15px;
            }}
            pre {{
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }}
            code {{
                padding: 2px 4px;
                border-radius: 4px;
                font-size: 14px;
                color: #d6336c;
            }}
            blockquote {{
                border-left: 4px solid #ccc;
                margin-left: 20px;
                padding-left: 15px;
                font-style: italic;
                color: #666;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Gera o PDF a partir do HTML estilizado
    pdf = pdfkit.from_string(html_content, False)

    # Salve o PDF no caminho desejado
    filepath = os.path.join(os.getcwd(), f"{filename}.pdf")
    with open(filepath, 'wb') as f:
        f.write(pdf)

    return filepath


# Rota para baixar o PDF
@app.route('/download_pdf/<id_survey>/<email>', methods=['GET'])
def download_pdf(id_survey, email):
    cursor = None
    try:
        cursor = mysql.connection.cursor()

        # Busca o nome da empresa com base no email na tabela "form"
        company_query = "SELECT empresa FROM form WHERE email = %s"
        cursor.execute(company_query, (email,))
        company_result = cursor.fetchone()

        if not company_result:
            return jsonify({"error": "Empresa não encontrada para esse email."}), 404

        company_name = company_result[0]  # Pega o nome da empresa

        # Busca o conteúdo do formulário na tabela "output_crew"
        query = "SELECT output FROM output_crew WHERE id_survey = %s AND email = %s"
        cursor.execute(query, (id_survey, email))
        result = cursor.fetchone()

        if result:
            output_content = result[0]
            filename = f"Resultado_{id_survey}_{email}"
            filepath = generate_pdf(id_survey, email, company_name, output_content, filename)
            
            # Atualiza o booleano
            update_query = "UPDATE form SET pdf = 1 WHERE id_survey = %s AND email = %s"
            cursor.execute(update_query, (id_survey, email))
            mysql.connection.commit()

            
            return send_file(filepath, as_attachment=True)
        else:
            return "Crew não executado para este formulário", 404
    except Exception as e:
        # Registrar erro completo
        app.logger.error(f"Erro ao gerar PDF: {str(e)}")
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()



@app.route('/')
def home():
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)