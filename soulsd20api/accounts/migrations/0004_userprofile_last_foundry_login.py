from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_token_last_used_and_grandfather'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='last_foundry_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
