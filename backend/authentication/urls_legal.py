"""
URL patterns for legal compliance endpoints
"""
from django.urls import path
from . import views_legal

urlpatterns = [
    # Legal documents
    path('legal/documents/', views_legal.get_legal_documents, name='get_legal_documents'),
    path('legal/accept/', views_legal.accept_legal_document, name='accept_legal_document'),
    
    # GDPR/CCPA Data Rights
    path('legal/data/export/', views_legal.request_data_export, name='request_data_export'),
    path('legal/data/export/status/', views_legal.get_data_export_status, name='get_data_export_status'),
    path('legal/data/delete/', views_legal.request_data_deletion, name='request_data_deletion'),
    path('legal/data/delete/cancel/', views_legal.cancel_data_deletion, name='cancel_data_deletion'),
    path('legal/data/summary/', views_legal.get_my_data_summary, name='get_my_data_summary'),
    
    # Age verification
    path('legal/age/verify/', views_legal.verify_age, name='verify_age'),
    
    # Content appeals
    path('legal/appeals/', views_legal.get_my_appeals, name='get_my_appeals'),
    path('legal/appeals/submit/', views_legal.submit_content_appeal, name='submit_content_appeal'),
]
