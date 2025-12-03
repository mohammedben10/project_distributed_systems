from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home'),
    path('dashbord/',views.dashbord,name='dashbord'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("history/", views.history, name="history"),
    path("history/delete/<int:pk>/", views.delete_history, name="delete_history"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)