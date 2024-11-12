# bibliotecas importadas
import sqlite3
import datetime
import random
import pandas as pd


# Variavel que definine onde esta e o nome do banco de dados
url = 'estoque.db'

# Variaveis de interação com banco de dados
conn = sqlite3.connect(url)
cursor = conn.cursor()


# Mapa para definição rápida dos tipos de movimentações e de operadores para consultas no banco
mapa_movimentacao = {1 : "Entrada", 2 : "Saída"}
mapa_operacao_bd = {1 : " = ?", 2 : " >= ?", 3 : " <= ?", 4 : "<> ?"}

# Definição da quantidade de corredores, prateleiras em cada corredor e posições em cada prateleira
numero_corredores = 2
numero_prateleiras_corredor = 5
numero_posicoes_pratileira = 5


# Definição das estruturas de dados
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


# DEFINIÇÂO DE FUNÇÔES
# Criação do banco de dados
def criar_banco():
    # TABELAS BANCO DE DADOS
    #Tabela 'Produtos' contem o estoque atual de produtos e a data da ultima movimentação
    #Tabela 'Categorias' contem as categorias de produtos
    #Tabela 'Movimentacao' com o registro de movimentações
    #Tabela 'Posicao' possui o registro das posições do estoque
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

    # Confifuração da tabela Posicao, que contem as localizações do estoque
    # Para cada 1 corredor há x prateleiras
    # Para cada 1 prateleira há x posições
    # Assim, a função a baixo gera códigos padronizados que simbolizam as posições dentro do estoque
    # Exemplo1 um produto na posição C01P01A01, está localizado no Corredor 01, Prateleira 01, Altura 01
    # Exemplo2 um produto na posição C10P02A01, está localizado no Corredor 10, Prateleira 02, Altura 01
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



# Realiza a validação dos caracteres digitado pelo usuário, para evitar SQL Injection
def validacao(input):
    caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./" #Lista de caracteres permitidos
    for i in input:
        if all(c in caracteres for c in i):
            continue
        else:
            print("\nERRO!:")
            print("\nCaractere inválido!")
            print("\nInsira apenas letras e números, sem nenhum caractere especial!")
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


# Registra as movimentações de entrada e saida e atualiza a quantidade do produto na tabela Produto
def movimentacao(movimentacoes):
        for movimentacao in movimentacoes:
            # Identifica o tipo de movimentação e realiza a operação para atualizar a quantidade de produto em estoque
            if movimentacao.tipo == mapa_movimentacao[1]:
                cursor.execute("UPDATE Produto SET quantidade = quantidade + ?, data = ? WHERE id = ? ", movimentacao.quantidade, movimentacao.data, movimentacao.produto_id)
            else:
                cursor.execute("UPDATE Produto SET quantidade = quantidade - ? AND data = ? WHERE id = ?",movimentacao.quantidade, movimentacao.data, movimentacao.produto_id)
            # Resgistra a movimentação no banco
            cursor.execute("INSERT INTO RegMovimentacao(produto_id, quantidade, tipo, data) VALUES(?,?,?,?)",movimentacao.produto_id, movimentacao.quantidade, mapa_movimentacao[movimentacao.tipo], movimentacao.data)
            conn.commit()


# Consulta no banco
def consultas_banco(tabela_consultar,  dado_consultar = '*',coluna_consultar = None, operacao = None, valor_consultar = None):
    select = f"SELECT {dado_consultar} FROM {tabela_consultar} WHERE TRUE" # Define oque sera selecionado e de qual tabela
    parametros = [] # parametros de comparação
    if coluna_consultar is not None:
        for coluna, operacao, valor in zip(coluna_consultar, operacao,valor_consultar): #desempacota o dicionario com os parametros
            select += f" AND {coluna} {mapa_operacao_bd[operacao]} ?"   #Define a coluna a ser consultada e a operação relacional
            parametros.append(valor)   # define o valor dos parametros a serem relacionados
    cursor.execute(select, parametros)   # executa de fato a consulta
    resultado_consultado = cursor.fetchall()  # retorna a variavel resultado_consultado o resultado da consulta
    return resultado_consultado


# Emição dos relatorios
def emitir_relatorio(tipo, subtipo = None, id = None):
    if tipo == 'estado': # relatorio do estado atual do estoque
        if subtipo == 1 or subtipo == 12:           
            dados = consultas_banco('Produto','*', 'quantidade', 3, 'quantidade_minima') # cria um dataframe com os produtos que estão com baixo estoque 
            df_produtos_baixo = pd.DataFrame({"Status" : "BAIXO" * len(dados) **dados})  # de acordo com o valor definido no cadastro
            return df_produtos_baixo
        if subtipo == 2 or subtipo == 12:
            dados2 = consultas_banco('Produto', '*', 'quantidade',2,'quantidade_excesso')       # cria um dataframe com os produtos que estão com excesso de estoque
            df_produtos_excesso = pd.DataFrame({"Status" : "EXCESSO" * len(dados2) **dados2})   # de acordo com o valor definido no cadastro
            return df_produtos_excesso
        if subtipo == 12:
            df_produtos_estado = df_produtos_baixo
            for linha in df_produtos_excesso:
                df_produtos_estado.loc[len(df_produtos_estado)] = linha # une os dataframes acima mantendo o de baixo estoque a cima de de excesso
        
            ids = df_produtos_estado.index.tolist() # lista os ids contidos no dataframe que contem os produtos com baixo e excesso de estoque
            dados3 = consultas_banco('Produto', 'id', 'id', 4, ids)                          # cria um dataframe com os produtos que não estão nos datafram
            df_produtos_normal = pd.DataFrame({"Status" : "NORMAL" *len(dados3) **dados3})     # de baixo e excesso de estoque

            for linha in df_produtos_normal:
                df_produtos_estado.loc[len(df_produtos_estado)] = linha # adiciona os demais produtos ao dataframe mostrando o estado geral do estoque destacando os
                                                                      # produtos com baixo e excesso de estoque, mantendo eles no inicio da tabela
            return df_produtos_estado

    elif tipo == 'movimentacao':
        dados = consultas_banco("RegMovimentacao") # Cria um dataframe das movimentações do estoque
        df_movimentacao = pd.DataFrame(dados)
        return df_movimentacao
    elif tipo == 'posicao':
        if subtipo == 1:
            ids = consultas_banco('Produto','posicao_id')           # Cria um dataframe das posições ocupadas no estoque
            dados = consultas_banco('Posicao','*', id, 1, ids)
        else:
            ids = consultas_banco('Produto','posicao_id')           # Cria um dataframe das posições vagas no estoque
            dados = consultas_banco('Posicao','*', 'id', 4, ids)
            df_posicao = pd.DataFrame(dados)
        return df_posicao

        
# Menu de interação 
while True:
    # Menu principal
    menu = input("Digite: 'a' - cadastros\n; 'b' - registrar movimentações\n; 'c' - consultas\n; 'd' - emitir relatório rápido;\n'e' - configuração\n'x' - encerrar")
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
                        if validacao(novacategoria): # Valida o que foi digitado pelo usuário
                            lista.append(categoria(novacategoria)) # Adiciona a lista
                        else:
                            continue
                        condicao = input("Deseja adicionar mais Categorias? [s/n]") # Usuário decide se deseja adicionar mais categorias
                        if condicao == "n": # Usuário não irá cadastrar outras categorias
                            cadastrar_categoria(lista) # Cadastra as categoria da lista
                            break

                elif menua == 'b': # Cadastrar Produtos
                     while True:
                         lista = []
                         listaprodutos = []

                         print("\nCADASTRO DE PRODUTOS\n")
                         print("\nVERIFIQUE POSIÇÕES DISPONIVEIS NO ESTOQUE ANTES DE CADASTRAR NOVO PRODUTOS")
                         # Usurário inseri cada parametro da tabela 'Produtos', os quai são adicionados a uma lista
                         inputnome = input("\nInsira o nome do produto: ")
                         lista.append(inputnome)

                         inputcategoria = input("\nInsira a categoria deste produto: ")
                         lista.append(inputcategoria)

                         inputpreco = input("\nInsira o preço do produto. (Casasdecimais separa por '.')")
                         lista.append(inputpreco)

                         inputposicao = input("\nInsira a localização do produto no estoque: ")
                         lista.append(inputposicao)

                         inputquantidade = input("\nInsira a quantidade deste produto no estoque: ")
                         lista.append(inputquantidade)

                         inputquantidade_minima = input("\nInsira a quantidade que será considerada 'baixa' deste produto no estoque: ")
                         lista.append(inputquantidade_minima)

                         inputquantidade_excesso = input("\nInsira a quantidade que será considerada 'excessiva' deste produto no estoque: ")                     
                         lista.append(inputquantidade_excesso)

                         if validacao(lista):   # Valida o que foi digitado pelo usuário
                             listaprodutos.append(novoproduto = produto(lista)) # normaliza a lista na categoria e adiciona a uma lista de objetos
                         else:
                             continue
                         condicao = input("\nDeseja adicionar mais Produtos?[s/n]: ") # Verifica se o usuário deseja cadastrar mais produtos
                         if condicao == "n":
                             cadastrar_categoria(listaprodutos) # Inseri a lista de objetos no banco
                             break
                elif menua == "x": # Volta para o menu anterior
                    break
                else:
                    print("\nERRO!:\nDigite uma opção válida:")      
                
        case 'b': # Menu de Registro de Movimentações
            while True:
                produtomov = []
                listamov = []
                print("\nREGISTRO DE MOVIMENTAÇÃO")
                # O usuário deve inserir o ID do produto, a quantidade e definir o tipo de movimentação todos são adicionados a uma lista
                inputproduto_id = input("\nInsira o ID do produto: ") 
                produtomov.append(inputproduto_id)

                inputquantidade = input("\nInsira a quantidade de produtos")
                produtomov.append(inputquantidade)

                inputtipo = input("\nInsira qual tipo de movimentação [1 - Entrada ou 2 - Saída]") 
                produtomov.append(inputtipo)

                if validacao(produtomov): # A lista é validada
                    listamov.append(reg_movimento(produtomov)) # a lista é normalizada na classe e adicionada a uma lista de objetos
                    reg_movimento(listamov) # a lista de objetos é adicionada ao banco
                else:
                    continue            
                condicao = input("\nRealizar mais registros? [s/n]") # usuário decide se decide realizar mais movimentações
                if condicao == 'n':
                    break

        case 'c': # Menu de consultas
            while True:
                # Sub-menu de consultas - tipo de consulta
                menuc = input("\nCONSULTAS\nDigite: 'a' para consultas referente a produtos;\n'b' - referente a movimentações;\n'c' - referente a categorias\n'x' - voltar para o menu anterior")
                # Sub-menu de consultas - tipo de consulta - consulta de produtos
                if menuc == 'a':
                    while True:
                        menuc = input("\nCONSULTAS DE PRODUTOS\nDigite:\n'a' - consultar o estoque;\n'b' - consultar os produtos com baixo estoque;\n'c' - consultar os produtos com excesso de estoque\n'd' - consultar o ID de um produto pelo nome;\n'e' - consultar o estado de um produto no estoque\n'f' - a posição de um produto\n'x' - voltar para o menu anterior")
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
                                    nomeproduto = input("\nDigite o nome do produto: ") # Usuário digita o nome do produto
                                    if validacao(nomeproduto): # Validação do que o usuário digitou
                                        print(consultas_banco('Produto','id', 'nome',1, nomeproduto)) # retorno da consulta
                                        break
                                    else:
                                        continue
                            case 'e': # Consulta o estado de um produto especifico no estoque
                                print('\nESTADO DE UM PRODUTO NO ESTOQUE')
                                idproduto = input('\nDigite o id do produto') # Usuário digito o id do produto
                                if validacao(idproduto): # Validação do que o usuário digitou
                                    print(consultas_banco('Produto','*','id',1,idproduto)) # retorno da consulta
                                    break
                                else:
                                    continue
                            case 'f': # Consulta a localização de um produto
                                while True:
                                    print('\nLOCALIZÇÃO DE UM PRODUTO NO ESTOQUE')
                                    idproduto = input("\nDigite o id do produto: ") # Usuário informa o id do produto
                                    if validacao(idproduto): # Validação do que o usuário digitou
                                        print(consultas_banco("produtos","posicao","id",1,idproduto)) # retorno da consulta
                                        break
                                    else:
                                        continue
                            case 'x':
                                break
                        condicao = input("\nDeseja fazer mais alguma consulta de produtos?[s/n]") # Usuário decide se deseja fazer outras consultas
                        if condicao == 'n':
                            break
                        else:
                            continue
                # Sub-menu de consultas - tipo de consulta - consulta de movimentações
                elif menuc == 'b':
                    while True:
                        menuc = input("\nCONSULTAS MOVIMENTAÇÕES\nDigite:\n'a' - movimentãções de um produto;\n'b' - todas entradas;\n'c' - todas saídas;\n'd' - as movimentações de um periodo\n x - voltar para o menu anterior")
                        match menuc:
                            case 'a': # consulta a movimentação de um produto
                                consultas_banco('RegMovimentacao')
                                continue
                            case 'b': # consulta as entradas de produtos
                                consultas_banco('RegMovimentacao', '*', 'tipo', 1, 'Entrada')
                                continue
                            case 'c': # consulta as saidas de produtos
                                consultas_banco('RegMovimentacao', '*', 'tipo', 1, 'Saída')
                                continue
                            case 'd': # consulta as movimentações de um periodo
                                while True:
                                    print("CONSULTAS DE MOVIMENTAÇÔES POR PERIODO") 
                                    periodoinicio = input('Insira a data do inicio do periodo a consultar [dd/mm/yy]: ') # usuário inseri a data inicial
                                    periodofim = input('Insira a data do fim do periodo [dd/mm/yy]: ') # usuário inseri a data final
                                    lista = [periodofim, periodoinicio] # oque foi inserido pelo usuário é adicionado a uma lista
                                    if validacao(lista): # validação do que foi inserido pelo usuário
                                        periodoinicio = datetime.strptime(periodoinicio, "%d/%m/%y")  
                                        periodofim = datetime.strptime(periodofim, "%d/%m/%y")
                                        print(consultas_banco('RegMovimentacao','*',('data','data'),(2,3),(periodoinicio, periodofim))) # Realiza a consulta e retorna o resultado
                                    else:
                                        continue
                                    condicao = input('Deseja consultar outras movimentações por periodo? [s/n]') # verifica se o u´suário deseja realizar mais consultas de movimentações
                                    if condicao == 'n':
                                        break
                                    else:
                                        continue
                            case 'x': # volta para o menu anterior
                                break
                            case _:
                                print("\nERRO!:\nDigite uma opção válida")

                # Sub-menu de consultas - tipo de consulta - consulta de movimentações
                elif menuc == 'c': 
                    print(consultas_banco('Categoria'))
                    continue

                elif menuc == 'x': # Volta para o menu anterior
                    break
                
                else:
                    print("\nERRO!:\nDigite uma opção válida")
                    continue
                        
        
        case 'd': # Menu de emissão ded relatório
            while True:
                # Sub-menu de emissão de relatório - tipo de relatório
                menud = input("\nEMIÇÃO DE RELATÓRIO RÁPIDO\nDigite:\n'a' - estado atual do estoque\n'b' - movimentação\n'c' - localização")
                if menud == 'a': 
                    # Sub-menu de emissão de relatório - tipo de relatório - estado atual do estoque
                    menud = input("\nEMIÇÃO DE RELATÓRIO RÁPIDO DO ESTADO ATUAL DO ESTOQUE\nDigite:\n'a' - relatório do estado geral do estoque;\n'b' - relatório dos produtos com baixo estoque;\,'c' - relatório dos produtos com excesso estoque;\n'x' - voltar para o menu anterior")
                    match menud:
                        case 'a': # Relatório do estado geral do estoque
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
                            print('\nERRO!\nEscolha uma opção válida!')
                            continue

                elif menud == 'b':
                    # Sub-menu de emissão de relatório - tipo de relatório - movimentação
                    print("\nEMISSÃO DE RELATÓRIO DE MOVIMENTAÇÕES GERAIS")
                    df_movimentacao = emitir_relatorio("movimentacao") # gera um dataframe com a tabela
                    df_movimentacao.to_excel('movimentacao_geral.xlsx', index=False) # salva o dataframe em uma tabela excel
                     
                elif menud == 'c':
                    # Sub-menu de emissão de relatório - tipo de relatório - localizações
                    while True:
                        menud = input("\nEMISSÃO DE RELATÓRIO RÁPIDO DE POSIÇÕES\nDigite:\n'a' - posições ocupadas\n'b' - posições vagas;\n'x' - para retornar ao menu anterior")
                        if menud == 'a': # relatório das posições ocupadas
                            df_localizacao_ocupadas = emitir_relatorio("posicao",1) # gera um dataframe com a tabela
                            df_localizacao_ocupadas.to_excel('posicoes_ocupadas_estoque.slxs', indes =False) # salva o dataframe em uma tabela excel
                            break
                        elif menud == 'b': # relatório das posições vagas
                            df_localizacao = emitir_relatorio("posicao") # gera um dataframe com a tabela
                            df_localizacao.to_excel('posicoes_vagas_estoque.xlsx', index=False) # salva o dataframe em uma tabela excel
                            break
                        elif menud =='x': # volta para o menu anterior
                            break
                        else:
                            print("\nERRO!\nOpção inválida!")
                            continue
        case 'e': # Menu de Configurações        
            menue = input("\nCONFIGURAÇÕES\nDigite:\n'a' - criar banco de dados")
            if menue == 'a':
                criar_banco() # Cria o banco de dados
        case 'x': # Fecha o sistema
            print("Sistema fechando...")
            print("Sistema fechado.")
            break

        case _:
            print("\nERRO\nDigite um comando válido")
            continue