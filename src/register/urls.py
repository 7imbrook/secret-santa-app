from django.conf.urls import re_path

import register.views as views

urlpatterns = [re_path(r"^$", views.index, name="index")]
