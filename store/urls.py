# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.store, name='store'),
#     path('search/', views.search, name='search'),

#     path('<slug:category_slug>/', views.store, name='products_by_category'),
#     path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
#     path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),

# ]
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.store, name='store'),
#     path('search/', views.search, name='search'),
#     path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),  # ← This must be BEFORE the slug paths
#     path('<slug:category_slug>/', views.store, name='products_by_category'),
#     path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.store, name='store'),
    path('search/', views.search, name='search'),

    # Specific routes go above dynamic slug routes
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    # Dynamic slug-based routes should come last
    path('<slug:category_slug>/', views.store, name='products_by_category'),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
]
