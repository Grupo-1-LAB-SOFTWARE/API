# Generated by Django 4.1.13 on 2024-03-11 22:52

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome_completo', models.CharField(max_length=500)),
                ('perfil', models.CharField(choices=[('Docente', 'Docente'), ('Administrador', 'Administrador')], default='Docente', max_length=25)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('siape', models.CharField(max_length=500)),
                ('classe', models.CharField(choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E')], default='a', max_length=30)),
                ('vinculo', models.CharField(choices=[('Estatuário', 'Estatuário'), ('Não selecionado', 'Não selecionado')], max_length=100)),
                ('regime_de_trabalho', models.CharField(choices=[('Exclusivo', 'Dedicação Exclusiva'), ('Integral', 'Integral'), ('Parcial', 'Parcial')], max_length=50)),
                ('titulacao', models.CharField(choices=[('Graduacão', 'Graduação'), ('Especialização', 'Especialização'), ('Mestre', 'Mestre'), ('Doutor', 'Doutor')], max_length=100)),
                ('campus', models.CharField(max_length=150)),
                ('instituto', models.CharField(max_length=150)),
                ('confirmar_email', models.EmailField(max_length=254, null=True)),
                ('confirmar_senha', models.CharField(max_length=128, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioDocente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data_criacao', models.DateField()),
                ('ano_relatorio', models.CharField(max_length=4)),
                ('atividades_letivas', models.JSONField(null=True)),
                ('calculos_ch_semanal_aulas', models.JSONField(null=True)),
                ('atividades_pedagogicas_complementares', models.JSONField(null=True)),
                ('atividades_orientacao_supervisao_preceptoria_tutoria', models.JSONField(null=True)),
                ('descricoes_orientacao_coorientacao_academica', models.JSONField(null=True)),
                ('supervisoes_academicas', models.JSONField(null=True)),
                ('preceptorias_tutorias_residencia', models.JSONField(null=True)),
                ('bancas_examinadoras', models.JSONField(null=True)),
                ('ch_semanal_atividade_ensino', models.JSONField(null=True)),
                ('avaliacoes_discentes', models.JSONField(null=True)),
                ('projetos_pesquisa_producao_intelectual', models.JSONField(null=True)),
                ('trabalhos_completos_publicados_periodicos_boletins_tecnicos', models.JSONField(null=True)),
                ('livros_capitulos_verbetes_publicados', models.JSONField(null=True)),
                ('trabalhos_completos_resumos_publicados_apresentados_congressos', models.JSONField(null=True)),
                ('outras_atividades_pesquisa_producao_intelectual', models.JSONField(null=True)),
                ('ch_semanal_atividades_pesquisa', models.JSONField(null=True)),
                ('projetos_extensao', models.JSONField(null=True)),
                ('estagios_extensao', models.JSONField(null=True)),
                ('atividades_ensino_nao_formal', models.JSONField(null=True)),
                ('outras_atividades_extensao', models.JSONField(null=True)),
                ('ch_semanal_atividades_extensao', models.JSONField(null=True)),
                ('distribuicao_ch_semanal', models.JSONField(null=True)),
                ('atividades_gestao_representacao', models.JSONField(null=True)),
                ('qualificacoes_docente_academica_profissional', models.JSONField(null=True)),
                ('outras_informacoes', models.JSONField(null=True)),
                ('afastamentos', models.JSONField(null=True)),
                ('usuario_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TrabalhoCompletoResumoPublicadoApresentadoCongressos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('descricao', models.CharField(max_length=1500)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='TrabalhoCompletoPublicadoPeriodicoBoletimTecnico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('descricao', models.CharField(max_length=1500)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='SupervisaoAcademica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('nome_e_ou_matricula_discente', models.CharField(max_length=300)),
                ('curso', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=50)),
                ('nivel', models.CharField(max_length=50)),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='QualificacaoDocenteAcademicaProfissional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('atividades', models.CharField(max_length=1500)),
                ('portaria_e_ou_data_de_realizacao', models.CharField(max_length=100)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='ProjetoPesquisaProducaoIntelectual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('titulo', models.CharField(max_length=600)),
                ('funcao', models.CharField(choices=[('Coordenador', 'Coordenador'), ('Colaborador', 'Colaborador')], default='Coordenador', max_length=20)),
                ('cadastro_proped', models.CharField(max_length=100)),
                ('situacao_atual', models.CharField(choices=[('Concluída', 'CONCLUÍDA'), ('Em andamento', 'EM ANDAMENTO'), ('Em pausa', 'EM PAUSA')], default='Concluída', max_length=30)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='ProjetoExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('titulo', models.CharField(max_length=600)),
                ('funcao', models.CharField(choices=[('coordenador', 'Coordenador'), ('colaborador', 'Colaborador')], default='coordenador', max_length=20)),
                ('cadastro_proex', models.CharField(max_length=100)),
                ('situacao_atual', models.CharField(choices=[('concluida', 'CONCLUÍDA'), ('em_andamento', 'EM ANDAMENTO'), ('em_pausa', 'EM PAUSA')], default='concluida', max_length=30)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='PreceptoriaTutoriaResidencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('nome_e_ou_matricula_discente', models.CharField(max_length=300)),
                ('tipo', models.CharField(max_length=50)),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='OutraInformacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('atividades', models.CharField(max_length=1500)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='OutraAtividadePesquisaProducaoIntelectual',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('descricao', models.CharField(max_length=1500)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='OutraAtividadeExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('atividade', models.CharField(max_length=1500)),
                ('ch_total_primeiro_semestre', models.FloatField()),
                ('ch_semanal_primeiro_semestre', models.FloatField(null=True)),
                ('ch_total_segundo_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='LivroCapituloVerbetePublicado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('descricao', models.CharField(max_length=1500)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='EstagioExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('area_conhecimento', models.CharField(max_length=400)),
                ('insituicao_ou_local', models.CharField(max_length=400)),
                ('periodo', models.CharField(max_length=100)),
                ('ch_semanal', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='DistribuicaoCHSemanal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('ch_semanal_atividade_didatica', models.FloatField()),
                ('ch_semanal_administracao', models.FloatField()),
                ('ch_semanal_pesquisa', models.FloatField()),
                ('ch_semanal_extensao', models.FloatField()),
                ('ch_semanal_total', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='DescricaoOrientacaoCoorientacaoAcademica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('nome_e_ou_matricula_discente', models.CharField(max_length=300)),
                ('curso', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=50)),
                ('nivel', models.CharField(max_length=50)),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='CHSemanalAtividadesPesquisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CHSemanalAtividadesExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='CHSemanalAtividadeEnsino',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente', unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CalculoCHSemanalAulas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('ch_semanal_graduacao', models.FloatField()),
                ('ch_semanal_pos_graduacao', models.FloatField()),
                ('ch_semanal_total', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='BancaExaminadora',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('nome_candidato', models.CharField(max_length=400)),
                ('titulo_trabalho', models.CharField(max_length=500)),
                ('ies', models.CharField(max_length=50)),
                ('tipo', models.CharField(max_length=50)),
                ('ch_semanal_primeiro_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField()),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AvaliacaoDiscente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc_primeiro_semestre', models.IntegerField()),
                ('nota_primeiro_semestre', models.FloatField()),
                ('codigo_turma_primeiro_semestre', models.CharField(max_length=50)),
                ('numero_doc_segundo_semestre', models.IntegerField()),
                ('nota_segundo_semestre', models.FloatField()),
                ('codigo_turma_segundo_semestre', models.CharField(max_length=50)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadePedagogicaComplementar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('ch_semanal_graduacao', models.FloatField()),
                ('ch_semanal_pos_graduacao', models.FloatField()),
                ('ch_semanal_total', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeOrientacaoSupervisaoPreceptoriaTutoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('ch_semanal_orientacao', models.FloatField()),
                ('ch_semanal_coorientacao', models.FloatField()),
                ('ch_semanal_supervisao', models.FloatField()),
                ('ch_semanal_preceptoria_e_ou_tutoria', models.FloatField()),
                ('ch_semanal_total', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeLetiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('codigo_disciplina', models.CharField(max_length=20)),
                ('nome_disciplina', models.CharField(max_length=70)),
                ('ano_e_semestre', models.CharField(max_length=6)),
                ('curso', models.CharField(max_length=300)),
                ('nivel', models.CharField(max_length=250)),
                ('numero_turmas_teorico', models.IntegerField()),
                ('numero_turmas_pratico', models.IntegerField()),
                ('ch_turmas_teorico', models.FloatField()),
                ('ch_turmas_pratico', models.FloatField()),
                ('docentes_envolvidos_e_cargas_horarias', models.JSONField()),
                ('ch_total', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeGestaoRepresentacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo_e_ou_funcao', models.CharField(max_length=100)),
                ('semestre', models.IntegerField()),
                ('ch_semanal', models.FloatField()),
                ('ato_de_designacao', models.CharField(max_length=150)),
                ('periodo', models.CharField(max_length=100)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeEnsinoNaoFormal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('atividade', models.CharField(max_length=1500)),
                ('ch_total_primeiro_semestre', models.FloatField()),
                ('ch_semanal_primeiro_semestre', models.FloatField(null=True)),
                ('ch_total_segundo_semestre', models.FloatField()),
                ('ch_semanal_segundo_semestre', models.FloatField(null=True)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
        migrations.CreateModel(
            name='Afastamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_doc', models.IntegerField()),
                ('motivo', models.CharField(max_length=1500)),
                ('portaria', models.CharField(max_length=150)),
                ('relatorio_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.relatoriodocente')),
            ],
        ),
    ]
