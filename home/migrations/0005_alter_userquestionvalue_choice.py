# Generated by Django 4.2.6 on 2023-10-25 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_alter_userquestionvalue_choice"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userquestionvalue",
            name="choice",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.CASCADE, to="home.choice"
            ),
        ),
    ]
