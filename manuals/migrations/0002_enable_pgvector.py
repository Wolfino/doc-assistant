from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    dependencies = [
        ("manuals", "0001_initial"),
    ]

    operations = [
        VectorExtension(),
    ]