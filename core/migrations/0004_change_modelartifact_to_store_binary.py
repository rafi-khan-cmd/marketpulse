# Generated manually to change ModelArtifact to store model as binary blob

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_newsarticle_options_newsarticle_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelartifact',
            name='path',
        ),
        migrations.AddField(
            model_name='modelartifact',
            name='data',
            field=models.BinaryField(default=b''),
            preserve_default=False,
        ),
    ]

