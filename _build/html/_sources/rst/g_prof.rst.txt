Guia Professor
==============

Adicionar alunos no servidor
____________________________

Baixe o arquivo CSV da lista de alunos do Blackboard e faça o upload pela linha
de terminal conectado no servidor via SSH:

- cd softdes
- source venv/bin/activate
- python3 manage.py batch_add_users ARQUIVO_BLACKBOARD.csv

Admin
__________________
Para ter permissão de adicionar desafios é necessário acessar o servidor como usuário 
admin
* acesse o servido com o endereço /admin

Adicionar desafios
__________________

* Acesse /admin/challenges/challenge
* Clique `ADICIONAR CHALLENGE`
* Dê o nome da função que o aluno deve criar em `Function name`.

* Adicione Tags para que os alunos possam acompanhar o desempenho em diferentes categorias, identificando facilidades e desafios.

* Adicone o arquivo com a bateria de testes necessárias para se passar no desafio. O arquivo deve seguir essa estrutura padrão:

.. code-block:: python

    from challenge_test_lib import challenge_test as ch
    # O nome da classe deve necessariamente ser TestCase
    class TestCase(ch.TestCaseWrapper):
    TIMEOUT = 2  # Limite de tempo em segundos por teste (default: 3s)

    # A mensagem de erro é definida por meio de um decorator.
    # Ela não é obrigatória. Caso não seja definida, uma mensagem
    # padrão será apresentada em caso de erro.
    # Todos os testes devem começar com 'test_'
    @ch.error_message('Verificar quando os argumentos forem zero')
    def test_argumentos_zero(self):
        # A challenge_test_lib foi construída com base no unittest.
        # Assim, quaisquer asserts do unittest podem ser utilizados.
        # Para mais opções:
        # https://docs.python.org/3/library/unittest.html#assert-methods
        # A função submetida pelo aluno estará disponível como
        # self.challenge_fun. Neste exemplo ela recebe 3 argumentos,
        # mas a quantidade e tipo dos argumentos pode ser diferente
        self.assertAlmostEquals(self.challenge_fun(0, 0, 0), 0.0)

    # Outro exemplo de teste
    @ch.error_message('Verificar quando o número de meses é zero')
    def test_zero_meses(self):
        self.assertAlmostEquals(self.challenge_fun(100, 0, 0.1), 100.0)



Adicionar tutoriais
___________________

* Acesse /admin/tutorials/tutorial ou /'superuser'/tutorials/tutorial
* Clique `ADICIONAR TUTORIAL`
* A descrição aceita código HTML.
* O campo Replit url pode ser usado para adicionar um iframe com o repl.it ao final do tutorial. O valor deste campo deve ser uma url, fornecida em Share Link ao clicar em share no repl.it.


