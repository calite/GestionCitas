from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Establishment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(unique=True)),
                ("email", models.EmailField(max_length=254)),
                ("auto_confirm", models.BooleanField(default=False)),
                ("interval_minutes", models.PositiveIntegerField(default=30)),
                ("simultaneous_capacity", models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("duration_minutes", models.PositiveIntegerField()),
                ("color", models.CharField(default="#3B82F6", max_length=20)),
                ("establishment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="services", to="core.establishment")),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                ("status", models.CharField(choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                ("client_name", models.CharField(max_length=200)),
                ("client_phone", models.CharField(max_length=50)),
                ("establishment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="core.establishment")),
                ("service", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="core.service")),
            ],
        ),
        migrations.CreateModel(
            name="Availability",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("weekday", models.PositiveSmallIntegerField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("establishment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="availabilities", to="core.establishment")),
            ],
        ),
        migrations.CreateModel(
            name="Block",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_datetime", models.DateTimeField()),
                ("end_datetime", models.DateTimeField()),
                ("reason", models.CharField(max_length=255)),
                ("establishment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocks", to="core.establishment")),
            ],
        ),
    ]
