from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="establishment",
            name="owners",
            field=models.ManyToManyField(blank=True, related_name="owned_establishments", to="auth.user"),
        )
    ]
