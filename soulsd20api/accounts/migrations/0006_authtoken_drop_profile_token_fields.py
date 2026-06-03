from django.conf import settings
from django.db import migrations, models


def copy_existing_drf_tokens_to_authtoken(apps, schema_editor):
    """Migrate every existing DRF Token row to an equivalent AuthToken with
    source='app'. Lets already-signed-in users stay signed in across the
    deploy instead of all getting kicked at once."""
    try:
        Token = apps.get_model('authtoken', 'Token')
    except LookupError:
        return
    AuthToken = apps.get_model('accounts', 'AuthToken')
    UserProfile = apps.get_model('accounts', 'UserProfile')

    profile_token_last_used = {
        profile.user_id: getattr(profile, 'token_last_used', None)
        for profile in UserProfile.objects.all()
    }

    for token in Token.objects.all():
        if AuthToken.objects.filter(key=token.key).exists():
            continue
        AuthToken.objects.create(
            user=token.user,
            key=token.key,
            source='app',
            created=token.created,
            last_used=profile_token_last_used.get(token.user_id) or token.created,
        )


def reverse_copy(apps, schema_editor):
    AuthToken = apps.get_model('accounts', 'AuthToken')
    AuthToken.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_pairingcode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=40, unique=True)),
                ('source', models.CharField(choices=[('app', 'App'), ('foundry', 'Foundry')], db_index=True, default='app', max_length=10)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('label', models.CharField(blank=True, default='', max_length=80)),
                ('user', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='auth_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.AddIndex(
            model_name='authtoken',
            index=models.Index(fields=['user', 'source'], name='accounts_au_user_id_source_idx'),
        ),
        migrations.RunPython(copy_existing_drf_tokens_to_authtoken, reverse_copy),
        migrations.RemoveField(
            model_name='userprofile',
            name='token_last_used',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_foundry_login',
        ),
    ]
