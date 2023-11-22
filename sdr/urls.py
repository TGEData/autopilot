from django.urls import path,include
from .views import (dashboard,
                    CreateProductView,
                    CreateCompanyView,
                    CreateProspectView,
                    CreateCampaignView,
                    )

urlpatterns = [
    path("dashboard/",dashboard,name='user-dashbord'),
    path("product/add/",CreateProductView.as_view(),name="product-add"),
    path("company/add/",CreateCompanyView.as_view(),name='company-add'),
    path("prospect/add/",CreateProspectView.as_view(),name="prospect-add"),
    path("campaign/add/",CreateCampaignView.as_view(),name="campaign-add"),


 
]