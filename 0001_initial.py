from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MockWebSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True)),
                ('exam_type', models.CharField(max_length=30)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(
                    choices=[('active','Faol'),('completed','Tugallangan'),('abandoned','Tashlab ketilgan')],
                    default='active', max_length=15)),
                ('answers', models.JSONField(default=dict)),
                ('correct', models.IntegerField(default=0)),
                ('total', models.IntegerField(default=0)),
                ('score_raw', models.FloatField(default=0)),
                ('score_label', models.CharField(blank=True, max_length=30)),
                ('ai_feedback', models.TextField(blank=True)),
                ('time_taken', models.IntegerField(default=0)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='web_sessions',
                    to='users.user'
                )),
            ],
            options={
                'verbose_name': 'Veb Mock Sessiya',
                'ordering': ['-started_at'],
            },
        ),
    ]