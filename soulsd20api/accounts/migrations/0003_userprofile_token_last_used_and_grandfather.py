from django.db import migrations, models
from django.utils import timezone


def grandfather_existing_tokens(apps, schema_editor):
    """Reset existing tokens' creation time to deploy time so the new
    ExpiringTokenAuthentication does not log everyone out at once. Also stamp
    profile.token_last_used so the sliding window starts from now.
    """
    Token = apps.get_model('authtoken', 'Token')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    now = timezone.now()

    Token.objects.all().update(created=now)
    UserProfile.objects.all().update(token_last_used=now)


def reverse_grandfather(apps, schema_editor):
    # No-op: we cannot recover the original creation times.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile_last_login'),
        ('authtoken', '0003_tokenproxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='token_last_used',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(grandfather_existing_tokens, reverse_grandfather),
    ]
