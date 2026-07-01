from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0003_remove_campaign_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='compendium_version',
            field=models.IntegerField(default=1),
        ),
    ]
