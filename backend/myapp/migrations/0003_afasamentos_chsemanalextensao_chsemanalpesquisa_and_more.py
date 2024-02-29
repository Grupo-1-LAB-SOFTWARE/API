# Generated by Django 4.1.13 on 2024-02-29 19:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_avaliacaodiscente_chsemanalaulas_supervisaoacademica_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Afasamentos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_proex', models.CharField(max_length=50)),
                ('motivo', models.CharField(max_length=500)),
                ('portaria', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CHSemanalExtensao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CHSemanalPesquisa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DistribuicaoCHSemanal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semestre', models.IntegerField()),
                ('atividade_didatica', models.IntegerField()),
                ('administracao', models.IntegerField()),
                ('pesquisa', models.IntegerField()),
                ('extensao', models.IntegerField()),
                ('total', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='OutrasInformacoes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cod_proex', models.CharField(max_length=50)),
                ('decricao', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='ProgressaoPromocao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progressao_promocao', models.CharField(choices=[('sim', 'Sim'), ('nao', 'Não')], max_length=3)),
            ],
        ),
        migrations.RemoveField(
            model_name='docente',
            name='email',
        ),
        migrations.RemoveField(
            model_name='projetodepesquisa',
            name='periodo_do_projeto',
        ),
        migrations.RemoveField(
            model_name='qualificacaodocente',
            name='ano_de_referencia',
        ),
        migrations.RemoveField(
            model_name='qualificacaodocente',
            name='nivel_academico',
        ),
        migrations.RemoveField(
            model_name='qualificacaodocente',
            name='semestre_de_referencia',
        ),
        migrations.AddField(
            model_name='atividadeextensao',
            name='ano',
            field=models.DateField(default='2024-02-19'),
        ),
        migrations.AddField(
            model_name='atividadeextensao',
            name='situacao',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='atividadegestaorepresentacao',
            name='ano',
            field=models.DateField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='atividadegestaorepresentacao',
            name='ato_designacao',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ensinonaoformal',
            name='ch_semanal_1',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ensinonaoformal',
            name='ch_semanal_2',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='estagioextensao',
            name='ch_semanal',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outrasatividadesextensao',
            name='ch_semanal_1',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='outrasatividadesextensao',
            name='ch_semanal_2',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projetodepesquisa',
            name='ano',
            field=models.DateField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projetodepesquisa',
            name='situacao',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='qualificacaodocente',
            name='atividades',
            field=models.CharField(default=1, max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='qualificacaodocente',
            name='cod_proex',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='qualificacaodocente',
            name='portaria_data_realizacao',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='supervisaoacademica',
            name='atividade',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='myapp.atividadepedagogicacomplementar'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='docente',
            name='classe',
            field=models.CharField(choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E')], default='a', max_length=30),
        ),
        migrations.AlterField(
            model_name='docente',
            name='regime_de_trabalho',
            field=models.CharField(choices=[('exclusivo', 'Dedicação Exclusiva'), ('integral', '40h'), ('parcial', '20h')], default='exclusivo', max_length=50),
        ),
        migrations.AlterField(
            model_name='docente',
            name='titulacao',
            field=models.CharField(choices=[('graduacao', 'Graduação'), ('especializacao', 'Especiallização'), ('mestre', 'Mestre'), ('doutor', 'Doutor')], max_length=50),
        ),
        migrations.AlterField(
            model_name='docente',
            name='vinculo',
            field=models.CharField(choices=[('estatuario', 'Estatuário'), ('não selecionado', 'Não selecionado')], max_length=100),
        ),
    ]
