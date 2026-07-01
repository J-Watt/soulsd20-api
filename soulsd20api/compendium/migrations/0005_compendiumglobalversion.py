from django.db import migrations, models


def seed_singleton(apps, schema_editor):
    Model = apps.get_model('compendium', 'CompendiumGlobalVersion')
    Model.objects.get_or_create(pk=1, defaults={'version': 1})


class Migration(migrations.Migration):

    dependencies = [
        ('compendium', '0004_add_campaign_fields_to_weaponskill'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompendiumGlobalVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.IntegerField(default=1)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RunPython(seed_singleton, migrations.RunPython.noop),
    ]
