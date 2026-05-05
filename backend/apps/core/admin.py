from django.contrib import admin
from .models import Appointment, Availability, Block, Establishment, Service

admin.site.register(Establishment)
admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(Availability)
admin.site.register(Block)
