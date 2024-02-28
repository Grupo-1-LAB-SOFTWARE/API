# Generated by Django 4.1.13 on 2024-02-27 18:35

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
            name='AtividadeExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_proex', models.CharField(max_length=50)),
                ('titulo', models.CharField(max_length=100)),
                ('inicio_projeto', models.DateField()),
                ('fim_projeto', models.DateField()),
                ('tipo_de_colaboracao', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeGestaoRepresentacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo', models.CharField(max_length=50)),
                ('inicio_projeto', models.DateField()),
                ('fim_projeto', models.DateField()),
                ('carga_horaria_semanal', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeOrientacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('semestre', models.IntegerField()),
                ('carga_horaria', models.IntegerField()),
                ('tipo', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='AtividadePedagogicaComplementar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.DateField()),
                ('semestre', models.IntegerField()),
                ('carga_horaria_semanal', models.IntegerField()),
                ('docentes_envolvidos', models.JSONField()),
                ('carga_horaria_docentes_envolvidos', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='BancaExaminacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_candidato', models.CharField(max_length=100)),
                ('titulo_trabalho', models.CharField(max_length=100)),
                ('ies', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=50)),
                ('ano', models.IntegerField()),
                ('semestre', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Campus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('cidade', models.CharField(choices=[('belem', 'Belém'), ('capitao_poco', 'Capitão Poço')], default='belem', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Docente',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('classe', models.CharField(choices=[('auxiliar_1', 'Auxiliar 1'), ('assistente_a_1', 'Assistente A-1'), ('adjunto_a_1', 'Adjunto A-1'), ('auxiliar_2', 'Auxiliar 2'), ('assistente_a_2', 'Assistente A-2'), ('adjunto_a_2', 'Adjunto A-2'), ('assistente_b_1', 'Assistente B-1'), ('assistente_b_2', 'Assistente B-2'), ('adjunto_c_1', 'Adjunto C-1'), ('adjunto_c_2', 'Adjunto C-2'), ('adjunto_c_3', 'Adjunto C-3'), ('adjunto_c_4', 'Adjunto C-4'), ('associado_d_1', 'Associado D-1'), ('associado_d_2', 'Associado D-2'), ('associado_d_3', 'Associado D-3'), ('associado_d_4', 'Associado D-4'), ('titular', 'Titular')], default='auxiliar_1', max_length=30)),
                ('vinculo', models.CharField(max_length=100)),
                ('regime_de_trabalho', models.CharField(choices=[('exclusivo', 'Dedicação Exclusiva'), ('integral', 'Tempo Integral'), ('parcial', 'Tempo Parcial')], default='exclusivo', max_length=50)),
                ('titulacao', models.CharField(max_length=50)),
                ('campus', models.CharField(max_length=50)),
                ('instituto', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ProjetoDePesquisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_proped', models.CharField(max_length=10)),
                ('titulo', models.CharField(max_length=100)),
                ('periodo_do_projeto', models.JSONField()),
                ('tipo_de_colaboracao', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Publicacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('ano', models.IntegerField()),
                ('veiculo_de_publicacao', models.CharField(max_length=100)),
                ('tipo', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='QualificacaoDocente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano_de_referencia', models.IntegerField()),
                ('semestre_de_referencia', models.CharField(choices=[('1', '1'), ('2', '2')], default='1', max_length=1)),
                ('nivel_academico', models.CharField(choices=[('graduacao', 'Graduação'), ('pos', 'Pós-graduação'), ('mestrado', 'Mestrado'), ('doutorado', 'Doutorado')], default='pos', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='RelatorioDocente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateField()),
                ('ano_relatorio', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EnsinoNaoFormal',
            fields=[
                ('atividadeextensao_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.atividadeextensao')),
            ],
            bases=('myapp.atividadeextensao',),
        ),
        migrations.CreateModel(
            name='EstagioExtensao',
            fields=[
                ('atividadeextensao_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.atividadeextensao')),
            ],
            bases=('myapp.atividadeextensao',),
        ),
        migrations.CreateModel(
            name='OutrasAtividadesExtensao',
            fields=[
                ('atividadeextensao_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.atividadeextensao')),
            ],
            bases=('myapp.atividadeextensao',),
        ),
        migrations.CreateModel(
            name='ProjetoExtensao',
            fields=[
                ('atividadeextensao_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='myapp.atividadeextensao')),
            ],
            bases=('myapp.atividadeextensao',),
        ),
        migrations.CreateModel(
            name='Orientando',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.IntegerField()),
                ('semestre', models.IntegerField()),
                ('nome', models.CharField(max_length=100)),
                ('matricula', models.CharField(max_length=30)),
                ('curso', models.CharField(max_length=60)),
                ('tipo', models.CharField(max_length=50)),
                ('nivel', models.CharField(max_length=50)),
                ('atividade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.atividadeorientacao')),
            ],
        ),
        migrations.CreateModel(
            name='Instituto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('sigla', models.CharField(max_length=3)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.campus')),
            ],
        ),
        migrations.CreateModel(
            name='Curso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nivel', models.CharField(choices=[('bacharelado', 'Bacharelado'), ('licenciatura', 'Licenciatura'), ('tecnologo', 'Tecnólogo')], default='bacharelado', max_length=30)),
                ('campus', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.campus')),
                ('instituto', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='myapp.instituto')),
            ],
        ),
        migrations.CreateModel(
            name='AtividadeLetiva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_disciplina', models.CharField(max_length=10)),
                ('nome_disciplina', models.CharField(max_length=70)),
                ('ano', models.DateField()),
                ('semestre', models.IntegerField()),
                ('carga_horaria_disciplina', models.IntegerField()),
                ('docentes_envolvidos', models.JSONField()),
                ('carga_horaria_docentes_envolvidos', models.JSONField()),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.curso')),
            ],
        ),
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
                ('perfil', models.CharField(choices=[('docente', 'Docente'), ('admin', 'Administrador')], default='docente', max_length=10)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('docente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docente', to='myapp.docente')),
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
    ]
