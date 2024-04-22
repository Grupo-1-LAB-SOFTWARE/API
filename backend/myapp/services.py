import os
import tempfile
import io
import shutil
from xhtml2pdf import pisa
import mammoth
from docxtpl import DocxTemplate
from typing import List, Dict

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


cabecalho_global: dict = {}
ch_semanal_aulas_1: dict = {}
ch_semanal_aulas_2: dict = {}
atividade_complementar_1_dict: dict = {}
atividade_complementar_2_dict: dict = {}
atividade_orientacao_preceptoria_tutoria_1_dict: dict = {}
atividade_orientacao_preceptoria_tutoria_2_dict: dict = {}
ch_atividade_ensino: dict = {}
ch_semanal_pesquisa: dict = {}
ch_semanal_atividades_extensao: dict = {}
distribuicao_ch_semanal_1: dict = {}
distribuicao_ch_semanal_2: dict = {}

lista_atividades_letivas_1: List[Dict] = []
lista_atividades_letivas_2: List[Dict] = []
descricao_orientacao: List[Dict] = []
supervisao_academica: List[Dict] = []
preceptoria_turoria_residencia: List[Dict] = []
bancas_examinadora: List[Dict] = []
avaliacao_discente: List[Dict] = []
pesquisa_producao: List[Dict] = []
trabalhos_completos: List[Dict] = []
livros_verbetes_publicados: List[Dict] = []
trabalhos_completos_congressos: List[Dict] = []
outras_atividades: List[Dict] = []
projetos_extensao: List[Dict] = []
estagios_extensao: List[Dict] = []
atividade_ensino_naoformal: List[Dict] = []
outras_atividade_extensao: List[Dict] = []
atividades_gestao_representacao: List[Dict] = []
qualificacao_docente: List[Dict] = []
outras_informacoes: List[Dict] = []
afastamentos: List[Dict] = []

global_context = {
    'cabecalho': cabecalho_global,
    'context': lista_atividades_letivas_1,
    'context_2': lista_atividades_letivas_2,
    'ch_semanal_aulas_1': ch_semanal_aulas_1,
    'ch_semanal_aulas_2': ch_semanal_aulas_2,
    'atividade_pedagogica_complementar_1': atividade_complementar_1_dict,
    'atividade_pedagogica_complementar_2': atividade_complementar_2_dict,
    'atividade_orientacao_preceptoria_tutoria_1': atividade_orientacao_preceptoria_tutoria_1_dict,
    'atividade_orientacao_preceptoria_tutoria_2': atividade_orientacao_preceptoria_tutoria_2_dict,
    'descricao_orientacao': descricao_orientacao,
    'supervisao_academica': supervisao_academica,
    'preceptoria_turoria_residencia': preceptoria_turoria_residencia,
    'bancas_examinadoras': bancas_examinadora,
    'ch_atividade_ensino': ch_atividade_ensino,
    'avaliacao_docente': avaliacao_discente,
    'pesquisa_producao': pesquisa_producao,
    'trabalhos_completos': trabalhos_completos,
    'livros_verbetes_publicados': livros_verbetes_publicados,
    'trabalhos_completos_congressos': trabalhos_completos_congressos,
    'outras_atividades': outras_atividades,
    'ch_semanal_pesquisa': ch_semanal_pesquisa,
    'projetos_extensao': projetos_extensao,
    'estagios_extensao': estagios_extensao,
    'atividade_ensino_naoformal': atividade_ensino_naoformal,
    'outras_atividade_extensao': outras_atividade_extensao,
    'ch_semanal_atividades_extensao': ch_semanal_atividades_extensao,
    'atividades_gestao_representacao': atividades_gestao_representacao,
    'qualificacao_docente': qualificacao_docente,
    'distribuicao_ch_semanal_1': distribuicao_ch_semanal_1,
    'distribuicao_ch_semanal_2': distribuicao_ch_semanal_2,
    'outras_informacoes': outras_informacoes,
    'afastamentos': afastamentos,
}

def docx_to_html(docx_path):
    # Realiza a conversão do conteúdo do arquivo docx para HTML
    result = mammoth.convert_to_html(io.BytesIO(docx_path))
    html = result.value
    html_with_styles = """
         <style>
            table {
                 border-collapse: collapse;
                 display: content;
             }
            table th, table td {
                border: 1px solid black;
                padding-top: 10px;
                table-layout: auto;
            } 
            img {
                 display: flex;
                 margin-left: auto;
                 margin-right: auto;
             }
            body {
                text-align: center;
                font-family: Arial, sans-serif;
            }
         </style>
     """ + html

    return html_with_styles

def convert_html_to_pdf(html_content):
    try:
        # Criar um buffer de memória para o PDF
        with io.BytesIO() as pdf_buffer:
            # Converter HTML para PDF usando pisa
            pdf_buffer.truncate(0)
            pisa.CreatePDF(io.BytesIO(html_content.encode('utf-8')), dest=pdf_buffer)

            pdf_binary = pdf_buffer.getvalue()

            return pdf_binary
    except Exception as e:
        print(f"PDF generation failed: {e}")

def escrever_dados_no_radoc(dados: dict):

    data = dados
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
    pesquisa_producao_dict = data['pesquisa_producao']
    trabalhos_completos_dict = data['trabalhos_completos']
    livros_verbetes_publicados_dict = data['livros_verbetes_publicados']
    trabalhos_completos_congressos_dict = data['trabalhos_completos_congressos']
    outras_atividades_dict = data['outras_atividades']
    ch_semanal_pesquisa_dict = data['ch_semanal_pesquisa']
    projetos_extensao_dict = data['projetos_extensao']
    estagios_extensao_dict = data['estagios_extensao']
    atividade_ensino_naoformal_dict = data['atividade_ensino_naoformal']
    outras_atividade_extensao_dict = data['outras_atividade_extensao']
    ch_semanal_atividades_extensao_dict = data['ch_semanal_atividades_extensao']
    atividades_gestao_representacao_dict = data['atividades_gestao_representacao']
    qualificacao_docente_dict = data['qualificacao_docente']
    distribuicao_ch_semanal_dict = data['distribuicao_ch_semanal']
    outras_informacoes_dict = data['outras_informacoes']
    afastamentos_dict = data['afastamentos']

    preencher_cabecalho(usuario_dict, relatorio_docente_dict)
    preencher_atividade_letiva(atividade_letiva_dict)
    preencher_ch_semanal_aulas(calculo_ch_semanal_aulas_dict)
    preencher_atividade_pedagogica_complementar(atividade_pedagogica_complementar_dict)
    preencher_atividade_orientacao_supervisao_preceptoria_tutoria(atividade_orientacao_supervisao_preceptoria_tutoria_dict)
    preencher_descricao_orientacao_coorientacao_academica(descricao_orientacao_coorientacao_academica_dict)
    preencher_supervisao_academica(supervisao_academica_dict)
    preencher_preceptoria_tutoria_residencia(preceptoria_tutoria_residencia_dict)
    preencher_banca_examinadora(banca_examinadora_dict)
    preencher_ch_semanal_atividade_ensino(ch_semanal_atividade_ensino_dict)
    preencher_avaliacao_discente(avaliacao_discente_dict)
    preencher_pesquisa_producao(pesquisa_producao_dict)
    preencher_trabalhos_completos(trabalhos_completos_dict)
    preencher_livros_verbetes_publicados(livros_verbetes_publicados_dict)
    preencher_trabalhos_completos_congressos(trabalhos_completos_congressos_dict)
    preencher_outras_atividades(outras_atividades_dict)
    preencher_ch_semanal_pesquisa(ch_semanal_pesquisa_dict)
    preencher_projetos_extensao(projetos_extensao_dict)
    preencher_estagios_extensao(estagios_extensao_dict)
    preencher_atividade_ensino_naoformal(atividade_ensino_naoformal_dict)
    preencher_outras_atividade_extensao(outras_atividade_extensao_dict)
    preencher_ch_semanal_atividades_extensao(ch_semanal_atividades_extensao_dict)
    preencher_atividades_gestao_representacao(atividades_gestao_representacao_dict)
    preencher_qualificacao_docente(qualificacao_docente_dict)
    preencher_distribuicao_ch_semanal(distribuicao_ch_semanal_dict)
    preencher_outras_informacoes(outras_informacoes_dict)
    preencher_afastamentos(afastamentos_dict)
    with io.BytesIO() as temp_docx_buffer:
        with open("myapp/doc/Modelo_RADOC.docx", 'rb') as file:
            conteudo_arquivo = file.read()

            with io.BytesIO() as arquivo_em_memoria:
                arquivo_em_memoria = io.BytesIO(conteudo_arquivo)
                doc = DocxTemplate(arquivo_em_memoria)

        doc.render(global_context)
        doc.save(temp_docx_buffer)
        doc.__setattr__("is_rendered", False)
        html_content = docx_to_html(temp_docx_buffer.getvalue())
        pdf_binary = convert_html_to_pdf(html_content)
        temp_docx_buffer.truncate(0)
        arquivo_em_memoria.truncate(0)
        temp_docx_buffer.close()
        arquivo_em_memoria.close()
        file.close()

    return pdf_binary

def preencher_cabecalho(usuario, relatorio):
    classe = usuario[0]['classe']
    vinculo = usuario[0]['vinculo']
    titulacao = usuario[0]['titulacao']
    regime_de_trabalho = usuario[0]['regime_de_trabalho']
    
    x_vin = ''
    x_gra = ''
    x_mes = ''
    x_esp = ''
    x_dot = ''
    x_de = ''
    x_40 = ''
    x_20 = ''
    x_a = ''
    x_b = ''
    x_c = ''
    x_d = ''
    x_e = ''

    if classe == 'a':
        x_a = 'X'
    elif classe == 'b':
        x_b = 'X'
    elif classe == 'c':
        x_c = 'X'
    elif classe == 'd':
        x_d = 'X'
    elif classe == 'e':
        x_e = 'X'
    
    if vinculo == 'Estatuário':
        x_vin = 'X'
    else:
        x_vin = x_vin

    if regime_de_trabalho == 'Exclusivo' or regime_de_trabalho == 'Dedicação Exclusiva':
        x_de = 'X'
    elif regime_de_trabalho == 'Integral':
        x_40 = 'X'
    elif regime_de_trabalho == 'Parcial':
        x_20 = 'X'

    if titulacao == 'Graduacão':
        x_gra = 'X'
    elif titulacao == 'Mestre':
        x_mes == 'X'
    elif titulacao == 'Especialização':
        x_esp == 'X'
    elif titulacao == 'Doutor':
        x_dot = 'X'

    cabecalho = {
        'ano_relatorio': relatorio[0]['ano_relatorio'],
        'instituto_campus': f"{usuario[0]['instituto']}/{usuario[0]['campus']}",
        'nome_completo': usuario[0]['nome_completo'],
        'siape': usuario[0]['siape'],
        'X_a': x_a,
        'X_b': x_b,
        'X_c': x_c,
        'X_d': x_d,
        'X_e': x_e,
        'X_vin': x_vin,
        'X_de': x_de,
        'X_40': x_40,
        'X_20': x_20,
        'X_gra': x_gra,
        'X_mes': x_mes,
        'X_esp': x_esp,
        'X_dot': x_dot
    }
    cabecalho_global.update(cabecalho)
    return

def preencher_atividade_letiva(atividade_letiva_dict):  
    disciplinas_semestre_1 = [atividade for atividade in atividade_letiva_dict[::-1] if atividade['semestre'] == 1]
    disciplinas_semestre_2 = [atividade for atividade in atividade_letiva_dict[::-1] if atividade not in disciplinas_semestre_1]

    for atividade in disciplinas_semestre_1:
        docentes = atividade['docentes_envolvidos_e_cargas_horarias']['lista']
        nomes_docentes = [docente['nome_docente'] for docente in docentes]
        docente_ch = [docente['carga_horaria'] for docente in docentes]

        linha = {
            'nome_disciplina': f"{atividade['codigo_disciplina']} - {atividade['nome_disciplina']}",
            'curso': atividade['curso'],
            'nivel': atividade['nivel'],
            'ch_total': str(atividade['ch_total']),
            'numero_turmas_teorico': str(atividade['numero_turmas_teorico']),
            'numero_turmas_pratico': str(atividade['numero_turmas_pratico']),
            'ch_turmas_teorico': str(atividade['ch_turmas_teorico']),
            'ch_turmas_pratico': str(atividade['ch_turmas_pratico']),
            'docente': "\n".join(nomes_docentes),
            'docente_ch': "\n".join(map(str, docente_ch)),
        }
        lista_atividades_letivas_1.append(linha)

    for atividade in disciplinas_semestre_2:
        docentes = atividade['docentes_envolvidos_e_cargas_horarias']['lista']
        nomes_docentes = [docente['nome_docente'] for docente in docentes]
        docente_ch = [docente['carga_horaria'] for docente in docentes]

        linha = {
            'nome_disciplina': f"{atividade['codigo_disciplina']} - {atividade['nome_disciplina']}",
            'curso': atividade['curso'],
            'nivel': atividade['nivel'],
            'ch_total': str(atividade['ch_total']),
            'numero_turmas_teorico': str(atividade['numero_turmas_teorico']),
            'numero_turmas_pratico': str(atividade['numero_turmas_pratico']),
            'ch_turmas_teorico': str(atividade['ch_turmas_teorico']),
            'ch_turmas_pratico': str(atividade['ch_turmas_pratico']),
            'docente': "\n".join(nomes_docentes),
            'docente_ch': "\n".join(map(str, docente_ch)),
        }
        lista_atividades_letivas_2.append(linha)
    return

def preencher_ch_semanal_aulas(calculo_ch_semanal_aulas_dict):
    calculo_ch_semanal_aulas_1 = [ch for ch in calculo_ch_semanal_aulas_dict if ch['semestre'] == 1]
    calculo_ch_semanal_aulas_2 = [ch for ch in calculo_ch_semanal_aulas_dict if ch not in calculo_ch_semanal_aulas_1]
    if calculo_ch_semanal_aulas_1:
        ch_semanal_1 = {
            'ch_semanal_graduacao': calculo_ch_semanal_aulas_1[0]['ch_semanal_graduacao'],
            'ch_semanal_pos_graduacao': calculo_ch_semanal_aulas_1[0]['ch_semanal_pos_graduacao'],
            'ch_semanal_total': calculo_ch_semanal_aulas_1[0]['ch_semanal_total']
        }
        ch_semanal_aulas_1.update(ch_semanal_1)
    if calculo_ch_semanal_aulas_2:
        ch_semanal_2 = {
            'ch_semanal_graduacao': calculo_ch_semanal_aulas_2[0]['ch_semanal_graduacao'],
            'ch_semanal_pos_graduacao': calculo_ch_semanal_aulas_2[0]['ch_semanal_pos_graduacao'],
            'ch_semanal_total': calculo_ch_semanal_aulas_2[0]['ch_semanal_total']
        }
        ch_semanal_aulas_2.update(ch_semanal_2)
    return

def preencher_atividade_pedagogica_complementar(lista_dicionario):
    atividade_complementar_1 = [atividade for atividade in lista_dicionario if atividade['semestre'] == 1]
    atividade_complementar_2 = [atividade for atividade in lista_dicionario if atividade not in atividade_complementar_1]
    if atividade_complementar_1:
        atividade_1 = {
            'ch_semanal_graduacao': atividade_complementar_1[0]['ch_semanal_graduacao'],
            'ch_semanal_pos_graduacao': atividade_complementar_1[0]['ch_semanal_pos_graduacao'],
            'ch_semanal_total': atividade_complementar_1[0]['ch_semanal_total']
        }
        atividade_complementar_1_dict.update(atividade_1)
    if atividade_complementar_2:
        atividade_2 = {
            'ch_semanal_graduacao': atividade_complementar_2[0]['ch_semanal_graduacao'],
            'ch_semanal_pos_graduacao': atividade_complementar_2[0]['ch_semanal_pos_graduacao'],
            'ch_semanal_total': atividade_complementar_2[0]['ch_semanal_total']
        }
        atividade_complementar_2_dict.update(atividade_2)
    return

def preencher_atividade_orientacao_supervisao_preceptoria_tutoria(lista_dicionario):
    atividade_orientacao_supervisao_preceptoria_tutoria_1 = [atividade for atividade in lista_dicionario if atividade['semestre'] == 1]
    atividade_orientacao_supervisao_preceptoria_tutoria_2 = [atividade for atividade in lista_dicionario if atividade not in atividade_orientacao_supervisao_preceptoria_tutoria_1]
    if atividade_orientacao_supervisao_preceptoria_tutoria_1:
        atividade_1 = {
            'ch_semanal_orientacao': atividade_orientacao_supervisao_preceptoria_tutoria_1[0]['ch_semanal_orientacao'],
            'ch_semanal_coorientacao': atividade_orientacao_supervisao_preceptoria_tutoria_1[0]['ch_semanal_coorientacao'],
            'ch_semanal_supervisao': atividade_orientacao_supervisao_preceptoria_tutoria_1[0]['ch_semanal_supervisao'],
            'ch_semanal_preceptoria_e_ou_tutoria': atividade_orientacao_supervisao_preceptoria_tutoria_1[0]['ch_semanal_preceptoria_e_ou_tutoria'],
            'ch_semanal_total': atividade_orientacao_supervisao_preceptoria_tutoria_1[0]['ch_semanal_total']
        }
        atividade_orientacao_preceptoria_tutoria_1_dict.update(atividade_1)
    if atividade_orientacao_supervisao_preceptoria_tutoria_2:
        atividade_2 = {
            'ch_semanal_orientacao': atividade_orientacao_supervisao_preceptoria_tutoria_2[0]['ch_semanal_orientacao'],
            'ch_semanal_coorientacao': atividade_orientacao_supervisao_preceptoria_tutoria_2[0]['ch_semanal_coorientacao'],
            'ch_semanal_supervisao': atividade_orientacao_supervisao_preceptoria_tutoria_2[0]['ch_semanal_supervisao'],
            'ch_semanal_preceptoria_e_ou_tutoria': atividade_orientacao_supervisao_preceptoria_tutoria_2[0]['ch_semanal_preceptoria_e_ou_tutoria'],
            'ch_semanal_total': atividade_orientacao_supervisao_preceptoria_tutoria_2[0]['ch_semanal_total']
        }
        atividade_orientacao_preceptoria_tutoria_2_dict.update(atividade_2)
    return

def preencher_descricao_orientacao_coorientacao_academica(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'nome_e_ou_matricula_discente': atividade['nome_e_ou_matricula_discente'],
            'curso': atividade['curso'],
            'tipo': atividade['tipo'],
            'nivel': atividade['nivel'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre'],
        }
        descricao_orientacao.append(linha)
    return

def preencher_supervisao_academica(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'nome_e_ou_matricula_discente': atividade['nome_e_ou_matricula_discente'],
            'curso': atividade['curso'],
            'tipo': atividade['tipo'],
            'nivel': atividade['nivel'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre'],
        }
        supervisao_academica.append(linha)
    return

def preencher_preceptoria_tutoria_residencia(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'nome_e_ou_matricula_discente': atividade['nome_e_ou_matricula_discente'],
            'tipo': atividade['tipo'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre'],
        }
        preceptoria_turoria_residencia.append(linha)
    return

def preencher_banca_examinadora(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'nome_candidato_titulo_trabalho_ies': f"{atividade['nome_candidato']} {atividade['titulo_trabalho']} {atividade['ies']}",
            'tipo': atividade['tipo'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre'],
        }
        bancas_examinadora.append(linha)
    return

def preencher_ch_semanal_atividade_ensino(lista_dicionario):
    if lista_dicionario:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': lista_dicionario[0]['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': lista_dicionario[0]['ch_semanal_segundo_semestre'],
        }
        ch_atividade_ensino.update(ch_semanal)
    else:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': '',
            'ch_semanal_segundo_semestre': '',
        }
        ch_atividade_ensino.update(ch_semanal)
    return

def preencher_avaliacao_discente(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc_primeiro_semestre': atividade['numero_doc_primeiro_semestre'],
            'nota_primeiro_semestre_codigo': f"{atividade['nota_primeiro_semestre']} {atividade['codigo_turma_primeiro_semestre']}",
            'numero_doc_segundo_semestre': atividade['numero_doc_segundo_semestre'],
            'nota_segundo_semestre_codigo': f"{atividade['nota_segundo_semestre']} {atividade['codigo_turma_segundo_semestre']}",
        }
        avaliacao_discente.append(linha)
    return

def preencher_pesquisa_producao(lista_dicionario):
    index = 1
    x_cor = ''
    x_cola = ''
    for atividade in lista_dicionario[::-1]:
        if atividade['funcao'] == 'Coordenador':
            x_cor = 'X'
        else:
            x_cola = 'X'
        linha = {
            'numero_doc': atividade['numero_doc'],
            'index_titulo': index,
            'titulo': atividade['titulo'],
            'X_cord': x_cor,
            'X_cola': x_cola,
            'cadastro_proped': atividade['cadastro_proped'],
            'situacao_atual': atividade['situacao_atual']
        }
        pesquisa_producao.append(linha)
        index += 1
    return

def preencher_trabalhos_completos(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'descricao': atividade['descricao'],
        }
        trabalhos_completos.append(linha)
    return

def preencher_livros_verbetes_publicados(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'descricao': atividade['descricao'],
        }
        livros_verbetes_publicados.append(linha)
    return

def preencher_trabalhos_completos_congressos(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'descricao': atividade['descricao'],
        }
        trabalhos_completos.append(linha)
    return

def preencher_outras_atividades(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'descricao': atividade['descricao'],
        }
        outras_atividades.append(linha)
    return

def preencher_ch_semanal_pesquisa(lista_dicionario):
    if lista_dicionario:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': lista_dicionario[0]['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': lista_dicionario[0]['ch_semanal_segundo_semestre'],
        }
        ch_semanal_pesquisa.update(ch_semanal)
    else:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': '',
            'ch_semanal_segundo_semestre': '',
        }
        ch_semanal_pesquisa.update(ch_semanal)
    return

def preencher_projetos_extensao(lista_dicionario):
    index = 1
    x_cor = ''
    x_cola = ''
    for atividade in lista_dicionario[::-1]:
        if atividade['funcao'] == 'Coordenador':
            x_cor = 'X'
        else:
            x_cola = 'X'
        linha = {
            'numero_doc': atividade['numero_doc'],
            'index_titulo': index,
            'titulo': atividade['titulo'],
            'X_cord': x_cor,
            'X_cola': x_cola,
            'cadastro_proex': atividade['cadastro_proex'],
            'situacao_atual': atividade['situacao_atual']
        }
        projetos_extensao.append(linha)
        index += 1
    return

def preencher_estagios_extensao(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'area_conhecimento': atividade['area_conhecimento'],
            'instituicao_ou_local': atividade['instituicao_ou_local'],
            'periodo': atividade['periodo'],
            'ch_semanal': atividade['ch_semanal'],
        }
        estagios_extensao.append(linha)
    return

def preencher_atividade_ensino_naoformal(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'atividade': atividade['atividade'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre']
        }
        atividade_ensino_naoformal.append(linha)
    return

def preencher_outras_atividade_extensao(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'atividade': atividade['atividade'],
            'ch_semanal_primeiro_semestre': atividade['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': atividade['ch_semanal_segundo_semestre']
        }
        outras_atividade_extensao.append(linha)
    return

def preencher_ch_semanal_atividades_extensao(lista_dicionario):
    if lista_dicionario:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': lista_dicionario[0]['ch_semanal_primeiro_semestre'],
            'ch_semanal_segundo_semestre': lista_dicionario[0]['ch_semanal_segundo_semestre'],
        }
        ch_semanal_atividades_extensao.update(ch_semanal)
    else:
        ch_semanal = {
            'ch_semanal_primeiro_semestre': '',
            'ch_semanal_segundo_semestre': '',
        }
        ch_semanal_atividades_extensao.update(ch_semanal)
    return

def preencher_atividades_gestao_representacao(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'cargo_e_ou_funcao': atividade['cargo_e_ou_funcao'],
            'semestre': atividade['semestre'],
            'ch_semanal': atividade['ch_semanal'],
            'ato_de_designacao': atividade['ato_de_designacao'],
            'periodo': atividade['periodo'],
        }
        atividades_gestao_representacao.append(linha)
    return

def preencher_qualificacao_docente(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'atividades': atividade['atividades'],
            'portaria_e_ou_data_de_realizacao': atividade['portaria_e_ou_data_de_realizacao'],
        }
        qualificacao_docente.append(linha)
    return

def preencher_distribuicao_ch_semanal(lista_dicionario):
    distribuicao_ch_semanal_1_dict = [ch for ch in lista_dicionario if ch['semestre'] == 1]
    distribuicao_ch_semanal_2_dict = [ch for ch in lista_dicionario if ch not in distribuicao_ch_semanal_1_dict]
    if distribuicao_ch_semanal_1_dict:
        ch_semanal_1 = {
            'ch_semanal_atividade_didatica': distribuicao_ch_semanal_1_dict[0]['ch_semanal_atividade_didatica'],
            'ch_semanal_administracao': distribuicao_ch_semanal_1_dict[0]['ch_semanal_administracao'],
            'ch_semanal_pesquisa': distribuicao_ch_semanal_1_dict[0]['ch_semanal_pesquisa'],
            'ch_semanal_extensao': distribuicao_ch_semanal_1_dict[0]['ch_semanal_extensao'],
            'ch_semanal_total': distribuicao_ch_semanal_1_dict[0]['ch_semanal_total']
        }
        distribuicao_ch_semanal_1.update(ch_semanal_1)
    if distribuicao_ch_semanal_2_dict:
        ch_semanal_2 = {
            'ch_semanal_atividade_didatica': distribuicao_ch_semanal_1_dict[0]['ch_semanal_atividade_didatica'],
            'ch_semanal_administracao': distribuicao_ch_semanal_1_dict[0]['ch_semanal_administracao'],
            'ch_semanal_pesquisa': distribuicao_ch_semanal_1_dict[0]['ch_semanal_pesquisa'],
            'ch_semanal_extensao': distribuicao_ch_semanal_1_dict[0]['ch_semanal_extensao'],
            'ch_semanal_total': distribuicao_ch_semanal_1_dict[0]['ch_semanal_total']
        }
        distribuicao_ch_semanal_2.update(ch_semanal_2)
    return

def preencher_outras_informacoes(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'atividades': atividade['atividades'],
        }
        outras_informacoes.append(linha)
    return

def preencher_afastamentos(lista_dicionario):
    for atividade in lista_dicionario[::-1]:
        linha = {
            'numero_doc': atividade['numero_doc'],
            'atividades': atividade['atividades'],
            'portaria_e_ou_data_de_realizacao': atividade['portaria_e_ou_data_de_realizacao'],
        }
        afastamentos.append(linha)
    return