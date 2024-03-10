import re
import pypdf

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

