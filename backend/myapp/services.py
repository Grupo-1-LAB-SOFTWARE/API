import re
import pypdf
#from docx import Document

def extrair_texto_do_pdf(caminho_do_pdf):
    pass
    '''with open(caminho_do_pdf, 'rb') as arquivo_pdf:
        leitor_pdf = pypdf.PdfReader(arquivo_pdf)
        texto = ""
        for pagina_num in range(leitor_pdf._get_num_pages()):
            pagina = leitor_pdf._get_page(pagina_num)
            texto += pagina.extract_text(extraction_mode='layout')
        print(texto)
    extrair_dados_de_atividades_letivas(texto)'''

def extrair_dados_de_atividades_letivas(texto):
    pass
    # Definindo expressões regulares e seus respectivos nomes de variáveis
    '''expressoes_regulares = {
        'nome_disciplina': re.compile(r'^\s+([a-zA-ZÀ-Ú0-9\s]+)\s+-\s*\d+\s+h\s+GRADUAÇÃO$', re.MULTILINE),
        # Adicionar mais expressões conforme necessário
    }
    resultados = {}
    # Itera sobre as expressões regulares
    for nome_variavel, expressao_regular in expressoes_regulares.items():
        resultados[nome_variavel] = re.findall(expressao_regular, texto)

    print(resultados)'''

#path_pdf = 'backend/myapp/pdfs/disciplinas-ministradas.pdf'

#extrair_texto_do_pdf(path_pdf)
    
#documento = Document("Modelo_RADOC.docx")

def escrever_dados_no_pdf(dados: dict):
    initial_dict = dados
    
    dados_docente = {
        'instituto_campos': 'icibe',
        'nome': 'reynan',
        'siape': '1234567',
        'classe': 'A',
        'vinculo': 'DE',
        'regime_de_trabalho': '40',
        'titulacao': 'Doutor',
    }

    dados_para_cada_tabela = {
    3: {}
    }

    for key, value in initial_dict.items():
        # Mapeando 'id' para (5, 0)
        if key == 'id':
            dados_para_cada_tabela[3][(5, 0)] = value
        # Mapeando 'ano' para (5, 1)
        elif key == 'ano':
            dados_para_cada_tabela[3][(5, 1)] = value
        # Mapeando 'nome' para (5, 2)
        elif key == 'nome':
            dados_para_cada_tabela[3][(5, 2)] = value
        pass

    preencher_radoc(documento, dados_para_cada_tabela)


def preencher_radoc(documento, dados_para_cada_tabela):
    for tabela_index, tabela in enumerate(documento.tables):
        dados = dados_para_cada_tabela.get(tabela_index + 1, {})  # Obtém os dados para a tabela atual, se existirem
        row_count = len(tabela.rows)
        for row_index in range(row_count):
            linha = tabela.rows[row_index]
            next_row_is_empty = row_index + 1 >= row_count or all(cell.text.strip() == '' for cell in tabela.rows[row_index + 1].cells)
            if next_row_is_empty:
                # Adiciona uma nova linha à tabela antes de preencher a célula
                tabela.add_row()
            for cell_index, celula in enumerate(linha.cells):
                # Verifica se a célula está vazia
                if not celula.text.strip():
                    # Se a posição existir nos dados, preenche a célula
                    posicao = (row_index, cell_index)
                    if posicao in dados:
                        celula.text = dados[posicao]
    documento.save("Radoc.docx")