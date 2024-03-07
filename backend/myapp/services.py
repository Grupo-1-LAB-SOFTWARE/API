import re
#import PyPDF2

def extrair_texto_do_pdf(caminho_do_pdf):
    with open(caminho_do_pdf, 'rb') as arquivo_pdf:
        leitor_pdf = PyPDF2.PdfFileReader(arquivo_pdf)
        texto = ""
        for pagina_num in range(leitor_pdf.numPages):
            pagina = leitor_pdf.getPage(pagina_num)
            texto += pagina.extractText()
    return texto

def extrair_dados_de_atividades_letivas(texto):
    # Definindo expressões regulares e seus respectivos nomes de variáveis
    expressoes_regulares = {
        'dado1': re.compile(r'SuaExpressaoRegular1'),
        'dado2': re.compile(r'SuaExpressaoRegular2'),
        'dado3': re.compile(r'SuaExpressaoRegular3'),
        # Adicionar mais expressões conforme necessário
    }
    resultados = {}
    # Itera sobre as expressões regulares
    for nome_variavel, expressao_regular in expressoes_regulares.items():
        resultados[nome_variavel] = re.findall(expressao_regular, texto)

    return resultados
