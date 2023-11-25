from django.urls import path,include
from .views import (dashboard,
                    CreateProductView,
                    CreateCompanyView,
                    CreateProspectView,
                    create_campaignview,
                    profile_view,
                    invoice_view,
                    conversation,
                    resend_email_webhook_reciever,
                    CampaignDetailsView,
                    send_prospect_email
                    )

urlpatterns = [
    path("dashboard/",dashboard,name='user-dashboard'),
    path("invioce/", invoice_view,name="invoice"),
    path("conversation/",conversation,name="conversation-inbox"),
    path("profile/user/<username>/",profile_view,name="profile-view"),
    path("product/add/",CreateProductView.as_view(),name="product-add"),
    path("company/add/",CreateCompanyView.as_view(),name='company-add'),
    path("prospect/add/",CreateProspectView.as_view(),name="prospect-add"),
    path("campaign/add/",create_campaignview,name="campaign-add"),
    path("campaign/details/<int:pk>/",CampaignDetailsView.as_view(),name="campaign-details"),
    path("webhook/reciever/",resend_email_webhook_reciever,name="resend-webhook"),
    path("send/email/<int:campaign_id>/",send_prospect_email,name="send-email")


 
]