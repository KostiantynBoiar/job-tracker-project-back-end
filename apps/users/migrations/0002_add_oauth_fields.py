from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_provider',
            field=models.CharField(
                choices=[('email', 'Email'), ('google', 'Google'), ('github', 'Github')],
                default='email',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='provider_id',
            field=models.CharField(
                blank=True,
                help_text='User ID from OAuth provider (Google/GitHub)',
                max_length=255,
                null=True,
            ),
        ),
    ]
