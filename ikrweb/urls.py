# ikrweb/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('education/', views.education, name='education'),
    path('contact/', views.contact, name='contact'),
    path('business-card/', views.business_card, name='bussiness_card'),   # URL fixed (was bussiness), name kept for template compatibility
    path('tip/', views.tipping, name='tipping'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]