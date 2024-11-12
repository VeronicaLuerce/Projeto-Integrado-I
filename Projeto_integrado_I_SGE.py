# bibliotecas importadas
import sqlite3
import datetime
import random
import pandas as pd


# Variavel que definine onde esta e o nome do banco de dados
url = 'estoque.db'

# Variaveis de intera��o com banco de dados
conn = sqlite3.connect(url)
cursor = conn.cursor()


# Mapa para defini��o r�pida dos tipos de movimenta��es e de operadores para consultas no banco
mapa_movimentacao = {1 : "Entrada", 2 : "Sa�da"}
mapa_operacao_bd = {1 : " = ?", 2 : " >= ?", 3 : " <= ?", 4 : "<> ?"}

# Defini��o da quantidade de corredores, prateleiras em cada corredor e posi��es em cada prateleira
numero_corredores = 2
numero_prateleiras_corredor = 5
numero_posicoes_pratileira = 5


# Defini��o das estruturas de dados
class produto:
    def __init__ (self, nome, categoria_id, preco, posicao, quantidade, data, quantidade_minima, quantidade_excesso):
        self.nome = nome
        self.categoria_id = categoria_id
        self.preco = preco
        self.posicao = posicao
        self.quantidade = quantidade
        self.data = data
        self.quantidade_minimo = quantidade_minima
        self.quantidade_excesso = quantidade_excesso


class categoria:
    def __init__ (self, nome):
        self.nome = nome


class reg_movimento:
    def __init__ (self, produto_id, quantidade, tipo, data):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.tipo = tipo
        self.data = data


# DEFINI��O DE FUN��ES
# Cria��o do banco de dados
def criar_banco():
    # TABELAS BANCO DE DADOS
    #Tabela 'Produtos' contem o estoque atual de produtos e a data da ultima movimenta��o
    #Tabela 'Categorias' contem as categorias de produtos
    #Tabela 'Movimentacao' com o registro de movimenta��es
    #Tabela 'Posicao' possui o registro das posi��es do estoque
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Produto(
        id INTEGER PRIMARY KEY UNIQUE,
        nome TEXT UNIQUE,
        categoria_id INTEGER,
        preco REAL,
        posicao_id INTEGER UNIQUE,
        quantidade INTEGER,
        data DATETIME,
        quantidade_minima INTEGER,
        quantidade_excesso INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES Categoria(id)
        FOREIGN KEY (posicao_id) REFERENCES Posicao(id)
        );

        CREATE TABLE IF NOT EXISTS Categoria(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS RegMovimentacao(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        tipo TEXT,
        data DATETIME,
        FOREIGN KEY (produto_id) REFERENCES Produto(id)
        );

        CREATE TABLE IF NOT EXISTS Posicao(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT
        );
    """)

    # Confifura��o da tabela Posicao, que contem as localiza��es do estoque
    # Para cada 1 corredor h� x prateleiras
    # Para cada 1 prateleira h� x posi��es
    # Assim, a fun��o a baixo gera c�digos padronizados que simbolizam as posi��es dentro do estoque
    # Exemplo1 um produto na posi��o C01P01A01, est� localizado no Corredor 01, Prateleira 01, Altura 01
    # Exemplo2 um produto na posi��o C10P02A01, est� localizado no Corredor 10, Prateleira 02, Altura 01
    count = 1
    while count <= numero_corredores:
        if count < 10:
            nome_corredor = f'C0{count}'
        else:
            nome_corredor = f'C{count}'
        count2 = 1
        while count2 <= numero_prateleiras_corredor:
            if count2 < 10:
                nome_prateleira = f'{nome_corredor}P0{count2}'
            else:
                nome_prateleira = f'{nome_corredor}P{count2}'
            count3 = 1
            while count3 <= numero_posicoes_pratileira:
                if count3 < 10:
                    nome_posicao = f'{nome_prateleira}A0{count3}'
                else:
                    nome_posicao = f'{nome_prateleira}A{count3}'
                cursor.execute("INSERT INTO Posicao(nome) VALUES = (?)" , (nome_posicao,))
                conn.commit()
    print("Banco de dados criado!")



# Realiza a valida��o dos caracteres digitado pelo usu�rio, para evitar SQL Injection
def validacao(input):
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./" #Lista de caracteres permitidos
    for i in input:
        if all(c in caracteres for c in i):
            continue
        else:
            print("\nERRO!:")
            print("\nCaractere inv�lido!")
            print("\nInsira apenas letras e n�meros, sem nenhum caractere especial!")
            return False
    return True


# Cadastro de categorias
def cadastrar_categoria(input):
    print("Adicionando Categoria...")
    for item in input:
        cursor.execute("INSERT INTO Categoria (nome) VALUES(?)" , (item.nome,))
        conn.commit()
    return print("Categoria adicionada!")


# Cadastro de produtos
def cadastrar_produto(dados_produto): # Deve conter uma lista de objetos da classe produto
        for produto in dados_produto:
            id = ''.join(random.choices('0123456789', k=4)) # Gera um codigo de id para o produto cadastrado.
            int(id)
            data = datetime.date.today()
            # Seleciona o nome da categoria pelo id informado
            cursor.execute("SELECT nome FROM Categoria WHERE id = ?", produto.categoria_id) 
            nome_categoria = cursor.fetchone()
            # Insere no banco os objetos
            cursor.execute("INSERT INTO Produto(id, nome, categoria_id, preco, posicao, quantidade, data, quantidade_minima, quantidade_excesso) VALUES(?,?,?,?,?,?,?,?,?)",
                          (id, produto.nome, nome_categoria, produto.preco, produto.posicao, produto.quantidade, data, produto.quantidade_minima, produto.quantidade_excesso))
            conn.commit()


# Registra as movimenta��es de entrada e saida e atualiza a quantidade do produto na tabela Produto
def movimentacao(movimentacoes):
        for movimentacao in movimentacoes:
            # Identifica o tipo de movimenta��o e realiza a opera��o para atualizar a quantidade de produto em estoque
            if movimentacao.tipo == mapa_movimentacao[1]:
                cursor.execute("UPDATE Produto SET quantidade = quantidade + ?, data = ? WHERE id = ? ", movimentacao.quantidade, movimentacao.data, movimentacao.produto_id)
            else:
                cursor.execute("UPDATE Produto SET quantidade = quantidade - ? AND data = ? WHERE id = ?",movimentacao.quantidade, movimentacao.data, movimentacao.produto_id)
            # Resgistra a movimenta��o no banco
            cursor.execute("INSERT INTO RegMovimentacao(produto_id, quantidade, tipo, data) VALUES(?,?,?,?)",movimentacao.produto_id, movimentacao.quantidade, mapa_movimentacao[movimentacao.tipo], movimentacao.data)
            conn.commit()


# Consulta no banco
def consultas_banco(tabela_consultar,  dado_consultar = '*',coluna_consultar = None, operacao = None, valor_consultar = None):
    select = f"SELECT {dado_consultar} FROM {tabela_consultar} WHERE TRUE" # Define oque sera selecionado e de qual tabela
    parametros = [] # parametros de compara��o
    if coluna_consultar is not None:
        for coluna, operacao, valor in zip(coluna_consultar, operacao,valor_consultar): #desempacota o dicionario com os parametros
            select += f" AND {coluna} {mapa_operacao_bd[operacao]} ?"   #Define a coluna a ser consultada e a opera��o relacional
            parametros.append(valor)   # define o valor dos parametros a serem relacionados
    cursor.execute(select, parametros)   # executa de fato a consulta
    resultado_consultado = cursor.fetchall()  # retorna a variavel resultado_consultado o resultado da consulta
    return resultado_consultado


# Emi��o dos relatorios
def emitir_relatorio(tipo, subtipo = None, id = None):
    if tipo == 'estado': # relatorio do estado atual do estoque
        if subtipo == 1 or subtipo == 12:           
            dados = consultas_banco('Produto','*', 'quantidade', 3, 'quantidade_minima') # cria um dataframe com os produtos que est�o com baixo estoque 
            df_produtos_baixo = pd.DataFrame({"Status" : "BAIXO" * len(dados) **dados})  # de acordo com o valor definido no cadastro
            return df_produtos_baixo
        if subtipo == 2 or subtipo == 12:
            dados2 = consultas_banco('Produto', '*', 'quantidade',2,'quantidade_excesso')       # cria um dataframe com os produtos que est�o com excesso de estoque
            df_produtos_excesso = pd.DataFrame({"Status" : "EXCESSO" * len(dados2) **dados2})   # de acordo com o valor definido no cadastro
            return df_produtos_excesso
        if subtipo == 12:
            df_produtos_estado = df_produtos_baixo
            for linha in df_produtos_excesso:
                df_produtos_estado.loc[len(df_produtos_estado)] = linha # une os dataframes acima mantendo o de baixo estoque a cima de de excesso
        
            ids = df_produtos_estado.index.tolist() # lista os ids contidos no dataframe que contem os produtos com baixo e excesso de estoque
            dados3 = consultas_banco('Produto', 'id', 'id', 4, ids)                          # cria um dataframe com os produtos que n�o est�o nos datafram
            df_produtos_normal = pd.DataFrame({"Status" : "NORMAL" *len(dados3) **dados3})     # de baixo e excesso de estoque

            for linha in df_produtos_normal:
                df_produtos_estado.loc[len(df_produtos_estado)] = linha # adiciona os demais produtos ao dataframe mostrando o estado geral do estoque destacando os
                                                                      # produtos com baixo e excesso de estoque, mantendo eles no inicio da tabela
            return df_produtos_estado

    elif tipo == 'movimentacao':
        dados = consultas_banco("RegMovimentacao") # Cria um dataframe das movimenta��es do estoque
        df_movimentacao = pd.DataFrame(dados)
        return df_movimentacao
    elif tipo == 'posicao':
        if subtipo == 1:
            ids = consultas_banco('Produto','posicao_id')           # Cria um dataframe das posi��es ocupadas no estoque
            dados = consultas_banco('Posicao','*', id, 1, ids)
        else:
            ids = consultas_banco('Produto','posicao_id')           # Cria um dataframe das posi��es vagas no estoque
            dados = consultas_banco('Posicao','*', 'id', 4, ids)
            df_posicao = pd.DataFrame(dados)
        return df_posicao

        
# Menu de intera��o 
while True:
    # Menu principal
    menu = input("Digite: 'a' - cadastros\n; 'b' - registrar movimenta��es\n; 'c' - consultas\n; 'd' - emitir relat�rio r�pido;\n'e' - configura��o\n'x' - encerrar")
    match menu:
        case 'a': # Menu de Cadastros
            while True:
                # Sub-menu de Cadastros - tipo de cadastro
                menua = input("CADASTRO:\nDigite:\n'a' - cadastrar uma categoria\n'b' - cadastrar um produto\n'x' - voltar para o menu anterior")
                if menua == 'a': # Cadastrar Categorias
                    while True:
                        print("\n CADASTRO DE CATEGORIAS\n")
                        novacategoria = input("Categoria a ser adicionada: ") # Usuario adiciona uma categoria
                        lista = []
                        if validacao(novacategoria): # Valida o que foi digitado pelo usu�rio
                            lista.append(categoria(novacategoria)) # Adiciona a lista
                        else:
                            continue
                        condicao = input("Deseja adicionar mais Categorias? [s/n]") # Usu�rio decide se deseja adicionar mais categorias
                        if condicao == "n": # Usu�rio n�o ir� cadastrar outras categorias
                            cadastrar_categoria(lista) # Cadastra as categoria da lista
                            break

                elif menua == 'b': # Cadastrar Produtos
                     while True:
                         lista = []
                         listaprodutos = []

                         print("\nCADASTRO DE PRODUTOS\n")
                         print("\nVERIFIQUE POSI��ES DISPONIVEIS NO ESTOQUE ANTES DE CADASTRAR NOVO PRODUTOS")
                         # Usur�rio inseri cada parametro da tabela 'Produtos', os quai s�o adicionados a uma lista
                         inputnome = input("\nInsira o nome do produto: ")
                         lista.append(inputnome)

                         inputcategoria = input("\nInsira a categoria deste produto: ")
                         lista.append(inputcategoria)

                         inputpreco = input("\nInsira o pre�o do produto. (Casasdecimais separa por '.')")
                         lista.append(inputpreco)

                         inputposicao = input("\nInsira a localiza��o do produto no estoque: ")
                         lista.append(inputposicao)

                         inputquantidade = input("\nInsira a quantidade deste produto no estoque: ")
                         lista.append(inputquantidade)

                         inputquantidade_minima = input("\nInsira a quantidade que ser� considerada 'baixa' deste produto no estoque: ")
                         lista.append(inputquantidade_minima)

                         inputquantidade_excesso = input("\nInsira a quantidade que ser� considerada 'excessiva' deste produto no estoque: ")                     
                         lista.append(inputquantidade_excesso)

                         if validacao(lista):   # Valida o que foi digitado pelo usu�rio
                             listaprodutos.append(novoproduto = produto(lista)) # normaliza a lista na categoria e adiciona a uma lista de objetos
                         else:
                             continue
                         condicao = input("\nDeseja adicionar mais Produtos?[s/n]: ") # Verifica se o usu�rio deseja cadastrar mais produtos
                         if condicao == "n":
                             cadastrar_categoria(listaprodutos) # Inseri a lista de objetos no banco
                             break
                elif menua == "x": # Volta para o menu anterior
                    break
                else:
                    print("\nERRO!:\nDigite uma op��o v�lida:")      
                
        case 'b': # Menu de Registro de Movimenta��es
            while True:
                produtomov = []
                listamov = []
                print("\nREGISTRO DE MOVIMENTA��O")
                # O usu�rio deve inserir o ID do produto, a quantidade e definir o tipo de movimenta��o todos s�o adicionados a uma lista
                inputproduto_id = input("\nInsira o ID do produto: ") 
                produtomov.append(inputproduto_id)

                inputquantidade = input("\nInsira a quantidade de produtos")
                produtomov.append(inputquantidade)

                inputtipo = input("\nInsira qual tipo de movimenta��o [1 - Entrada ou 2 - Sa�da]") 
                produtomov.append(inputtipo)

                if validacao(produtomov): # A lista � validada
                    listamov.append(reg_movimento(produtomov)) # a lista � normalizada na classe e adicionada a uma lista de objetos
                    reg_movimento(listamov) # a lista de objetos � adicionada ao banco
                else:
                    continue            
                condicao = input("\nRealizar mais registros? [s/n]") # usu�rio decide se decide realizar mais movimenta��es
                if condicao == 'n':
                    break

        case 'c': # Menu de consultas
            while True:
                # Sub-menu de consultas - tipo de consulta
                menuc = input("\nCONSULTAS\nDigite: 'a' para consultas referente a produtos;\n'b' - referente a movimenta��es;\n'c' - referente a categorias\n'x' - voltar para o menu anterior")
                # Sub-menu de consultas - tipo de consulta - consulta de produtos
                if menuc == 'a':
                    while True:
                        menuc = input("\nCONSULTAS DE PRODUTOS\nDigite:\n'a' - consultar o estoque;\n'b' - consultar os produtos com baixo estoque;\n'c' - consultar os produtos com excesso de estoque\n'd' - consultar o ID de um produto pelo nome;\n'e' - consultar o estado de um produto no estoque\n'f' - a posi��o de um produto\n'x' - voltar para o menu anterior")
                        match menuc:
                            case 'a': # Consulta o estoque completo
                                print('\nESTADO DO ESTOQUE\n')
                                print(consultas_banco('Produto'))
                                continue
                            case 'b': # Consulta os produtos com estoque baixo
                                print('\nPRODUTOS COM BAIXA DE ESTOQUE\n')
                                print(consultas_banco('Produto','*', 'quantidade', 3, 'quantidade_minima'))
                                continue
                            case 'c': # Consulta os produto com estoque em excesso
                                print('\nPRODUTOS COM EXCESSO DE ESTOQUE')
                                print(consultas_banco('Produto', '*', 'quantidade',2,'quantidade_excesso'))
                                continue
                            case 'd': # Consulta o id do produto pelo seu nome
                                while True:
                                    print('\nID DE UM PRODUTO PELO SEU NOME')
                                    nomeproduto = input("\nDigite o nome do produto: ") # Usu�rio digita o nome do produto
                                    if validacao(nomeproduto): # Valida��o do que o usu�rio digitou
                                        print(consultas_banco('Produto','id', 'nome',1, nomeproduto)) # retorno da consulta
                                        break
                                    else:
                                        continue
                            case 'e': # Consulta o estado de um produto especifico no estoque
                                print('\nESTADO DE UM PRODUTO NO ESTOQUE')
                                idproduto = input('\nDigite o id do produto') # Usu�rio digito o id do produto
                                if validacao(idproduto): # Valida��o do que o usu�rio digitou
                                    print(consultas_banco('Produto','*','id',1,idproduto)) # retorno da consulta
                                    break
                                else:
                                    continue
                            case 'f': # Consulta a localiza��o de um produto
                                while True:
                                    print('\nLOCALIZ��O DE UM PRODUTO NO ESTOQUE')
                                    idproduto = input("\nDigite o id do produto: ") # Usu�rio informa o id do produto
                                    if validacao(idproduto): # Valida��o do que o usu�rio digitou
                                        print(consultas_banco("produtos","posicao","id",1,idproduto)) # retorno da consulta
                                        break
                                    else:
                                        continue
                            case 'x':
                                break
                        condicao = input("\nDeseja fazer mais alguma consulta de produtos?[s/n]") # Usu�rio decide se deseja fazer outras consultas
                        if condicao == 'n':
                            break
                        else:
                            continue
                # Sub-menu de consultas - tipo de consulta - consulta de movimenta��es
                elif menuc == 'b':
                    while True:
                        menuc = input("\nCONSULTAS MOVIMENTA��ES\nDigite:\n'a' - moviment���es de um produto;\n'b' - todas entradas;\n'c' - todas sa�das;\n'd' - as movimenta��es de um periodo\n x - voltar para o menu anterior")
                        match menuc:
                            case 'a': # consulta a movimenta��o de um produto
                                consultas_banco('RegMovimentacao')
                                continue
                            case 'b': # consulta as entradas de produtos
                                consultas_banco('RegMovimentacao', '*', 'tipo', 1, 'Entrada')
                                continue
                            case 'c': # consulta as saidas de produtos
                                consultas_banco('RegMovimentacao', '*', 'tipo', 1, 'Sa�da')
                                continue
                            case 'd': # consulta as movimenta��es de um periodo
                                while True:
                                    print("CONSULTAS DE MOVIMENTA��ES POR PERIODO") 
                                    periodoinicio = input('Insira a data do inicio do periodo a consultar [dd/mm/yy]: ') # usu�rio inseri a data inicial
                                    periodofim = input('Insira a data do fim do periodo [dd/mm/yy]: ') # usu�rio inseri a data final
                                    lista = [periodofim, periodoinicio] # oque foi inserido pelo usu�rio � adicionado a uma lista
                                    if validacao(lista): # valida��o do que foi inserido pelo usu�rio
                                        periodoinicio = datetime.strptime(periodoinicio, "%d/%m/%y")  
                                        periodofim = datetime.strptime(periodofim, "%d/%m/%y")
                                        print(consultas_banco('RegMovimentacao','*',('data','data'),(2,3),(periodoinicio, periodofim))) # Realiza a consulta e retorna o resultado
                                    else:
                                        continue
                                    condicao = input('Deseja consultar outras movimenta��es por periodo? [s/n]') # verifica se o u�su�rio deseja realizar mais consultas de movimenta��es
                                    if condicao == 'n':
                                        break
                                    else:
                                        continue
                            case 'x': # volta para o menu anterior
                                break
                            case _:
                                print("\nERRO!:\nDigite uma op��o v�lida")

                # Sub-menu de consultas - tipo de consulta - consulta de movimenta��es
                elif menuc == 'c': 
                    print(consultas_banco('Categoria'))
                    continue

                elif menuc == 'x': # Volta para o menu anterior
                    break
                
                else:
                    print("\nERRO!:\nDigite uma op��o v�lida")
                    continue
                        
        
        case 'd': # Menu de emiss�o ded relat�rio
            while True:
                # Sub-menu de emiss�o de relat�rio - tipo de relat�rio
                menud = input("\nEMI��O DE RELAT�RIO R�PIDO\nDigite:\n'a' - estado atual do estoque\n'b' - movimenta��o\n'c' - localiza��o")
                if menud == 'a': 
                    # Sub-menu de emiss�o de relat�rio - tipo de relat�rio - estado atual do estoque
                    menud = input("\nEMI��O DE RELAT�RIO R�PIDO DO ESTADO ATUAL DO ESTOQUE\nDigite:\n'a' - relat�rio do estado geral do estoque;\n'b' - relat�rio dos produtos com baixo estoque;\,'c' - relat�rio dos produtos com excesso estoque;\n'x' - voltar para o menu anterior")
                    match menud:
                        case 'a': # Relat�rio do estado geral do estoque
                            print("\nESTADO GERAL DO ESTOQUE")
                            df_estado_geral = emitir_relatorio("estado",12) # gera um dataframe com a tabela
                            df_estado_geral.to_excel('estado_geral_estoque.xlsx', index=False)  # salva o dataframe em uma tabela excel
                            continue
                        case 'b':
                            print("\nPRODUTOS COM BAIXO ESTOQUE")
                            df_estoque_baixo = emitir_relatorio("estado",1) # gera um dataframe com a tabela
                            df_estoque_baixo.to_excel('produtos_baixo_estoque.xlsx', index=False) # salva o dataframe em uma tabela excel
                            continue
                        case 'c':
                            print("\nPRODUTOS COM EXCESSO ESTOQUE")
                            df_estoque_excesso = emitir_relatorio("estado",2) # gera um dataframe com a tabela
                            df_estoque_baixo.to_excel('produtos_excesso_estoque.xlsx', index=False) # salva o dataframe em uma tabela excel
                            continue
                        case 'x': # Retorna para o menu anterior
                            break
                        case _:
                            print('\nERRO!\nEscolha uma op��o v�lida!')
                            continue

                elif menud == 'b':
                    # Sub-menu de emiss�o de relat�rio - tipo de relat�rio - movimenta��o
                    print("\nEMISS�O DE RELAT�RIO DE MOVIMENTA��ES GERAIS")
                    df_movimentacao = emitir_relatorio("movimentacao") # gera um dataframe com a tabela
                    df_movimentacao.to_excel('movimentacao_geral.xlsx', index=False) # salva o dataframe em uma tabela excel
                     
                elif menud == 'c':
                    # Sub-menu de emiss�o de relat�rio - tipo de relat�rio - localiza��es
                    while True:
                        menud = input("\nEMISS�O DE RELAT�RIO R�PIDO DE POSI��ES\nDigite:\n'a' - posi��es ocupadas\n'b' - posi��es vagas;\n'x' - para retornar ao menu anterior")
                        if menud == 'a': # relat�rio das posi��es ocupadas
                            df_localizacao_ocupadas = emitir_relatorio("posicao",1) # gera um dataframe com a tabela
                            df_localizacao_ocupadas.to_excel('posicoes_ocupadas_estoque.slxs', indes =False) # salva o dataframe em uma tabela excel
                            break
                        elif menud == 'b': # relat�rio das posi��es vagas
                            df_localizacao = emitir_relatorio("posicao") # gera um dataframe com a tabela
                            df_localizacao.to_excel('posicoes_vagas_estoque.xlsx', index=False) # salva o dataframe em uma tabela excel
                            break
                        elif menud =='x': # volta para o menu anterior
                            break
                        else:
                            print("\nERRO!\nOp��o inv�lida!")
                            continue
        case 'e': # Menu de Configura��es        
            menue = input("\nCONFIGURA��ES\nDigite:\n'a' - criar banco de dados")
            if menue == 'a':
                criar_banco() # Cria o banco de dados
        case 'x': # Fecha o sistema
            print("Sistema fechando...")
            print("Sistema fechado.")
            break

        case _:
            print("\nERRO\nDigite um comando v�lido")
            continue