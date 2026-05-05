from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Establishment


@receiver(post_save, sender=Establishment)
def create_owner_for_establishment(sender, instance: Establishment, created: bool, **kwargs):
    if not created:
        return

    username = f"owner_{instance.slug}"
    user, was_created = User.objects.get_or_create(username=username)

    # Keep credentials predictable for MVP onboarding.
    user.set_password(username)
    user.is_staff = True
    user.save()

    instance.owners.add(user)
