from django.db import models
from pgvector.django import HnswIndex, VectorField


class Manual(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Section(models.Model):
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)
    embedding = VectorField(dimensions=1024, null=True, blank=True)

    class Meta:
        ordering = ["manual", "order"]
        indexes = [
            HnswIndex(
                name="section_embedding_hnsw",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            )
        ]

    def __str__(self):
        return f"{self.manual.title} - {self.title}"