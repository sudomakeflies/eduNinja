from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Question, Option

@receiver(post_delete, sender=Question)
def delete_orphaned_options(sender, instance, **kwargs):
    # Obtener todas las Options que no están relacionadas con ninguna Question
    orphaned_options = Option.objects.filter(question=None)
    # Eliminar las Options huérfanas
    orphaned_options.delete()
