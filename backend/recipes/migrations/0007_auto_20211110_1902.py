# Generated by Django 2.2.6 on 2021-11-10 16:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20211109_2143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favourites',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite', to='recipes.Recipe'),
        ),
    ]
