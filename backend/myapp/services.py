import re
import pypdf
from docx import Document

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
    
doc = Document("myapp/doc/Modelo_RADOC.docx")

def escrever_dados_no_pdf(dados: dict):
    data = dados
    print(data)
    usuario_dict = data['usuario']
    relatorio_docente_dict = data['relatorio_docente']
    atividade_letiva_dict = data['atividade_letiva']
    calculo_ch_semanal_aulas_dict = data['calculo_ch_semanal_aulas']
    atividade_pedagogica_complementar_dict = data['atividade_pedagogica_complementar']
    atividade_orientacao_supervisao_preceptoria_tutoria_dict = data['atividade_orientacao_supervisao_preceptoria_tutoria']
    descricao_orientacao_coorientacao_academica_dict = data['descricao_orientacao_coorientacao_academica']
    supervisao_academica_dict = data['supervisao_academica']
    preceptoria_tutoria_residencia_dict = data['preceptoria_tutoria_residencia']
    banca_examinadora_dict = data['banca_examinadora']
    ch_semanal_atividade_ensino_dict = data['ch_semanal_atividade_ensino']
    avaliacao_discente_dict = data['avaliacao_discente']
    
    placeholder_inicial = {
    'ANO_RELATORIO': relatorio_docente_dict[0]['ano_relatorio'],
    'INSTITUTO_CAMPUS': f"{usuario_dict[0]['instituto']}/{usuario_dict[0]['campus']}",
    'NOME_COMPLETO': usuario_dict[0]['nome_completo'],
    'SIAPE_P': usuario_dict[0]['siape'],
    'CLASSE': usuario_dict[0]['classe'],
    'VINCULO': usuario_dict[0]['vinculo'],
    'REGIME_DE_TRABALHO': usuario_dict[0]['regime_de_trabalho'],
    'TITULACAO': usuario_dict[0]['titulacao'],
    }

    def preencher_cabecalho(placeholder_inicial):
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for placeholder, value in placeholder_inicial.items():
                        if placeholder in cell.text:
                            cell.text = cell.text.replace(placeholder, str(value))
                        elif placeholder == 'CLASSE':
                            if value == 'a' or value == 'A':
                                if '(   ) A' in cell.text:
                                    cell.text = cell.text.replace('(   ) A', '( X ) A')
                            elif value == 'b' or value == 'B':
                                if '(  ) B' in cell.text:
                                    cell.text = cell.text.replace('(  ) B', '( X ) B')
                            elif value == 'c' or value == 'C':
                                if '(   ) C' in cell.text:
                                    cell.text = cell.text.replace('(   ) C', '( X ) C')        
                            elif value == 'd' or value == 'D':
                                if '(   ) D' in cell.text:
                                    cell.text = cell.text.replace('(   ) D', '( X ) D')
                            elif value == 'e' or value == 'E':
                                if '(   ) E' in cell.text:
                                    cell.text = cell.text.replace('(   ) E', '( X ) E')
                        elif placeholder == 'VINCULO':
                            if value == 'Estatuário':
                                if '(    ) Estatutário' in cell.text:
                                    cell.text = cell.text.replace('(    ) Estatutário', '(  X  ) Estatutário')
                        elif placeholder == 'REGIME_DE_TRABALHO':
                            if value == 'Exclusivo':
                                if '(    ) DE' in cell.text:
                                    cell.text = cell.text.replace('(    ) DE', '(  X  ) DE')
                            elif value == 'Integral':
                                if '(    ) 40h' in cell.text:
                                    cell.text = cell.text.replace('(    ) 40h', '(  X  ) 40h')
                            elif value == 'Parcial':
                                if '(    ) 20h' in cell.text:
                                    cell.text = cell.text.replace('(    ) 20h', '(  X  ) 20h')
                        elif placeholder == 'TITULACAO':
                            if value == 'Graduacão':
                                if '(    ) Graduação' in cell.text:
                                    cell.text = cell.text.replace('(    ) Graduação', '(  X  ) Graduação')
                            elif value == 'Especialização':
                                if '(     ) Especialização' in cell.text:
                                    cell.text = cell.text.replace('(     ) Especialização', '(  X  ) Especialização')
                            elif value == 'Mestre':
                                if '(    ) Mestre' in cell.text:
                                    cell.text = cell.text.replace('(    ) Mestre', '(  X  ) Mestre')
                            elif value == 'Doutor':
                                if '(    ) Doutor' in cell.text:
                                    cell.text = cell.text.replace('(    ) Doutor', '(  X  ) Doutor')

    doc.save('myapp/doc/Modelo_RADOC_preenchido.docx')
    return(data)