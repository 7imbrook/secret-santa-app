from django.conf.urls import re_path

import register.api.views as views

urlpatterns = [
    re_path(r"^inbound$", views.incoming_message, name="incoming_message"),
    re_path(r"^register$", views.register, name="register"),
]
