# Generated by Django 4.1.10 on 2023-07-06 19:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_post_tag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="post",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="blog.post",
            ),
        ),
    ]
