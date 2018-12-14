# Generated by Django 2.1.3 on 2018-12-06 06:50

from django.db import migrations, models
import django.db.models.deletion
import matching.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("register", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Owner",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("owner_name", models.CharField(max_length=140, null=True)),
                ("foundation_message", models.CharField(max_length=240, null=True)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("initial", "Initial, request foundation"),
                            ("foundation", "Has foundation, request name"),
                            ("name", "Has name"),
                        ],
                        default="initial",
                        max_length=20,
                    ),
                ),
                (
                    "excluded_from_matching_with",
                    models.ManyToManyField(
                        related_name="_owner_excluded_from_matching_with_+",
                        to="matching.Owner",
                    ),
                ),
                (
                    "number",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner",
                        to="register.PhoneNumber",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SecretSantaGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                )
            ],
        ),
        migrations.AddField(
            model_name="owner",
            name="secret_santa_group",
            field=models.ForeignKey(
                null=True,
                on_delete=matching.models.ALSO_CLEAR_YOUR_SECRET,
                to="matching.SecretSantaGroup",
            ),
        ),
        migrations.AddField(
            model_name="owner",
            name="your_secret",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="matching.Owner",
            ),
        ),
    ]
