# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: rauli
"""

from datetime import datetime
import sqlite3
import hashlib
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth


DBNAME = './quiz.db'

def lambda_handler(event, context):
    '''
    Função responsável por fazer a correção do teste
    '''
    try:

        import numbers

        def not_equals(first, second):
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        # TODO implement
        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        exec(code, locals())


        test = []
        for index, arg in enumerate(args):
            if not 'desafio{0}'.format(ndes) in locals():
                return "Nome da função inválido. Usar 'def desafio{0}(...)'".format(ndes)

            if not_equals(eval('desafio{0}(*arg)'.format(ndes)), resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except:
        return "Função inválida."

def converte_data(orig):
    '''
        Função responsável por formatar string de data-tempo
    '''
    return orig[8:10]+'/'+orig[5:7]+'/'+orig[0:4]+' '+orig[11:13]+':'+orig[14:16]+':'+orig[17:]

def get_quizes(user):
    '''
    Faz o query do id e do número dos quizes disponíveis pro usuário
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user in ('admin', 'fabioja'):
        cursor.execute("SELECT id, numb from QUIZ")
    else:
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT id, numb from QUIZ where release < '{0}'".format(date_now))
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info

def get_user_quiz(userid, quizid):
    '''
    Faz o query das respostas e resultados dos quizzes do usuário
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sent,answer,result from USERQUIZ where userid = '{0}' and quizid = {1} order by sent desc".format(userid, quizid))
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info

def set_user_quiz(userid, quizid, sent, answer, result):
    '''
    Insere no bando de dados o quiz feito pelo usuário
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    #print("insert into USERQUIZ(userid,quizid,sent,answer,result) values ('{0}',{1},'{2}','{3}','{4}');".format(userid, quizid, sent, answer, result))
    #cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) values ('{0}',{1},'{2}','{3}','{4}');".format(userid, quizid, sent, answer, result))
    cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) values (?,?,?,?,?);", (userid, quizid, sent, answer, result))
    #
    conn.commit()
    conn.close()

def get_quiz(_id, user):
    '''
    Faz o query de com todas informações de todos os quizzes disponíveis para o usuário
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user in ('admin', 'fabioja'):
        cursor.execute("SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {0}".format(_id))
    else:
        date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT id, release, expire, problem, tests, results, diagnosis, numb from QUIZ where id = {0} and release < '{1}'".format(_id, date_now))
    info = [reg for reg in cursor.fetchall()]
    conn.close()
    return info

def set_info(pwd, user):
    '''
    Função responsável por alterar a senha do usuário no banco de dados
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()

def get_info(user):
    '''
    Faz o query de informações do usuário pelo username
    '''
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("SELECT pass, type from USER where user = '{0}'".format(user))
    print("SELECT pass, type from USER where user = '{0}'".format(user))
    info = [reg[0] for reg in cursor.fetchall()]
    conn.close()
    if info == 0:
        return None
    else:
        return info[0]

AUTH = HTTPBasicAuth()

APP = Flask(__name__, static_url_path='')
APP.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'

@APP.route('/', methods=['GET', 'POST'])
@AUTH.login_required
def main():
    '''
    Trata das rotas GET, POST da requisição /
    '''
    msg = ''
    _p = 1
    challenges = get_quizes(AUTH.username())
    sent = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if request.method == 'POST' and 'ID' in request.args:
        _id = request.args.get('ID')
        quiz = get_quiz(_id, AUTH.username())
        if quiz == 0:
            msg = "Boa tentativa, mas não vai dar certo!"
            _p = 2
            return render_template('index.html', username=AUTH.username(), challenges=challenges, _p=_p, msg=msg)


        quiz = quiz[0]
        if sent > quiz[2]:
            msg = "Sorry... Prazo expirado!"

        _f = request.files['code']
        filename = './upload/{0}-{1}.py'.format(AUTH.username(), sent)
        _f.save(filename)
        with open(filename, 'r') as _fp:
            answer = _fp.read()

        #lamb = boto3.client('lambda')
        args = {"ndes": _id, "code": answer, "args": eval(quiz[4]), "resp": eval(quiz[5]), "diag": eval(quiz[6])}

        #response = lamb.invoke(FunctionName="Teste", InvocationType='RequestResponse', Payload=json.dumps(args))
        #feedback = response['Payload'].read()
        #feedback = json.loads(feedback).replace('"','')
        feedback = lambda_handler(args, '')


        result = 'Erro'
        if feedback == 0:
            feedback = 'Sem erros.'
            result = 'OK!'

        set_user_quiz(AUTH.username(), _id, sent, feedback, result)


    if request.method == 'GET':
        if 'ID' in request.args:
            _id = request.args.get('ID')
        else:
            _id = 1

    if challenges == 0:
        msg = "Ainda não há desafios! Volte mais tarde."
        _p = 2
        return render_template('index.html', username=AUTH.username(), challenges=challenges, _p=_p, msg=msg)
    else:
        quiz = get_quiz(_id, AUTH.username())

        if quiz == 0:
            msg = "Oops... Desafio invalido!"
            _p = 2
            return render_template('index.html', username=AUTH.username(), challenges=challenges, _p=_p, msg=msg)

        answers = get_user_quiz(AUTH.username(), _id)

    return render_template('index.html', username=AUTH.username(), challenges=challenges, quiz=quiz[0], e=(sent > quiz[0][2]), answers=answers, _p=_p, msg=msg, expi=converte_data(quiz[0][2]))

@APP.route('/pass', methods=['GET', 'POST'])
@AUTH.login_required
def change():
    '''
     Função responsável por fazer as requisições de alteração de senha
    '''
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        _p = 1
        msg = ''
        if nova != repet:
            msg = 'As novas senhas nao batem'
            _p = 3
        elif get_info(AUTH.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = 'A senha antiga nao confere'
            _p = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), AUTH.username())
            msg = 'Senha alterada com sucesso'
            _p = 3
    else:
        msg = ''
        _p = 3

    return render_template('index.html', username=AUTH.username(), challenges=get_quizes(AUTH.username()), _p=_p, msg=msg)


@APP.route('/logout')
def logout():
    '''
    Função responsável pela rota de logout
    '''
    return render_template('index.html', _p=2, msg="Logout com sucesso"), 401

@AUTH.get_password
def get_password(username):
    '''
    Função responsável pela rota que consulta senha do usuário
    '''
    return get_info(username)

@AUTH.hash_password
def hash_pw(password):
    '''
    Função responsável pela rota que criptografa senha do usuário
    '''
    return hashlib.md5(password.encode()).hexdigest()

if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0', port=80)
