from django.urls import path
from django.urls.conf import include
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('crear/', views.crearPost, name='crear'),
    path('registrarse/', views.registrarUsuario,name='register',),
    path('post/<int:pk>', views.verPost, name='post'),
    path('actualizar/<int:pk>', views.actualizarPost, name='actualizar'),
    path('eliminar/<int:pk>', views.eliminarPost, name='eliminar'),
    path('likes/<int:pk>', views.darLike, name='dar_like'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('quiz_gcp/<int:pk>', views.dash_view, name='quiz_gcp'),
    path('test/<int:pk>', views.test, name='test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)