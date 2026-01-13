from django.contrib import admin

from order.models.payment import SSLCommerzData
from order.models.repair_order import RepairOrder


admin.site.register(SSLCommerzData)
admin.site.register(RepairOrder)
