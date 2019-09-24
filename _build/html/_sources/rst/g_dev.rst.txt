Guia Desenvolvedor
==================

Setup
_____

Cria um ambiente virtual para maior comodidade e instale as dependências através de:
$ pip install -r requirements.txt

Com as dependências instaladas é necessário instalar a biblioteca customizada de testes,
para isso vá até a pasta `ChallengeTestRunner` e rode o setup.py:
$ cd ChallengeTestRunner
$ python setup.py install

Servidor de produção
____________________
Para utilizar as configurações de produção é necessário que o arquivo InsperProgChallenges/production_settings.py exista (ele pode estar vazio).

Para atualizar o servidor de produção basta executar um git pull e reiniciar o Apache.

Configuração do lambda
______________________
Execute o script prepare_lambda_code.sh. Faça o upload do arquivo lambda_code.zip na função testRunner na Amazon.



