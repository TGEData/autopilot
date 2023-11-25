from typing import Any
from django.forms.models import BaseModelForm
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, UpdateView,DeleteView,DetailView
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models.signals import post_save
from django.conf import settings
from core.models import UserProfile,Company
from .models import Product,Prospect,Conversion,CompanyEmailProvider,EmailActivity,Campaign,AIGeneratedEmail
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from background_task import background
from .generatefollowupemail import generate_emails_leads,send_email
from django.core.mail import EmailMessage, get_connection
import os
from . forms import CampaignForm
from django.urls import reverse




# Create your views here.
def create_userprofile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
  
post_save.connect(create_userprofile,sender=settings.AUTH_USER_MODEL)


class CreateCompanyView(LoginRequiredMixin,CreateView,ListView):
     model = Company
     template_name = "registration/company.html"
     success_url = reverse_lazy("company-add")
     fields = ['company_name','company_website']
   

     def form_valid(self,form):
          userprofile = get_object_or_404(UserProfile,user=self.request.user)
          form.instance.userprofile = userprofile        
          return super().form_valid(form)


class CreateProductView(LoginRequiredMixin,CreateView,ListView):
     model = Product
     context_object_name = "user_products"
     success_url = reverse_lazy("product-add")
     template_name = "registration/product.html"
     fields =["property_name",
              "property_sector",
              "property_description",
              "property_url",
              "user_company"
              ]

class CreateProspectView(LoginRequiredMixin,CreateView,ListView):
     model = Prospect
     context_object_name = "user_prospect"
     success_url = reverse_lazy("prospect-add")
     template_name = "registration/prospect.html"
     fields = ["source_identifier","source",
               "first_name","last_name",
               "current_title","current_company",
               "email","photo_url","facebook_url",
               "twitter_url", "linkedin_url",
               "user_company"]
        
     def get_form(self, form_class=None):
        userprofile = get_object_or_404(UserProfile,user=self.request.user)
        form = super().get_form(form_class)
        form.fields["user_company"].queryset = Company.objects.filter(userprofile=userprofile)
        return form
@login_required
def invoice_view(request):
     return render(request,"registration/invoice.html")


@login_required
def profile_view(request,username):
     template_name ="registration/profile.html"

     return render(request,template_name)

@login_required
def create_campaignview(request):
     template_name = "registration/campaign.html"
     userprofile = get_object_or_404(UserProfile,user=request.user)
     
     campaign_object_data = Campaign.objects.filter(userprofile=userprofile)
     if request.method == "POST":
          form = CampaignForm(request.POST)
          if  form.is_valid():
               campaign_instance =  form.save(commit=False)
             
               campaign_instance.userprofile = userprofile
               campaign_instance.save()
               print()
          
               # get all the form data 
               campaign_summary = form.cleaned_data.get('campaign_summary')
               cmp_user_company = form.cleaned_data.get('user_company')
               cmp_prospect = form.cleaned_data.get('prospect')
               cmp_product = form.cleaned_data.get('product')
          #print(str(cmp_product).split(":")[1])
               # filter data for to AI generate email


          #get product data
               products = Product.objects.filter(property_name=str(str(cmp_product).split(sep=":")[1]).split(" ")[1]).first()
               ai_property_description = products.property_description

          # get company data 
               companies = Company.objects.filter(company_name=cmp_user_company).first()
               ai_company_name = companies.company_name
               ai_company_website = companies.company_website
               #ai_company_identifier = companies.company_identifier

          #get prospect data
               user_prospect = Prospect.objects.filter(user_company=cmp_user_company).first()
              
               ai_prospect_fullname = f"{user_prospect.first_name} {user_prospect.last_name}"
               ai_prospect_current_title = user_prospect.current_title
               ai_prospect_current_company = user_prospect.current_company
               ai_prospect_email = user_prospect.email

               generate_emails_leads(openai_api_key="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",
                                   campaign_summary=campaign_summary,
                                   property_name=ai_company_name,
                                   property_description=ai_property_description,
                                   company_name=ai_company_name,
                                   company_website=ai_company_website,
                                   prospect_fullName=ai_prospect_fullname,
                                   prospect_current_title=ai_prospect_current_title,
                                   prospect_current_company=ai_prospect_current_company,
                                   sales_lead_username=request.user,
                                   campaign=campaign_instance,
                                   ai_prospect_email=ai_prospect_email
                                   )

     else:
         form = CampaignForm()

     return render(request,template_name,{"form":form,"user_campaigns":campaign_object_data})
          



def send_prospect_email(request,campaign_id):
     ## get campaign by id
     campaign = get_object_or_404(Campaign,pk=campaign_id)
     ## get generated email template
     aigenerated_email = AIGeneratedEmail.objects.get(campaign=campaign_id)
     prospect_email = aigenerated_email.prospect_email
     property_name = Product.objects.get(campaign=campaign)
     #print(property_name.property_name)

     ## extract the first line as subject
     subject =str(aigenerated_email.campaign_generated_email_template[0:38+len(campaign.campaign_summary)].split(":")[1])
     messsage = f"{aigenerated_email.campaign_generated_email_template[len(subject):]}"
     send_email(subject=subject,
                message=messsage,
                recipient_list=[prospect_email],
                api_key=os.environ.get('RESEND_API_KEY'),
                host=settings.RESEND_SMTP_HOST,
                port=settings.RESEND_SMTP_PORT,
                EmailMessage=EmailMessage,
                get_connection=get_connection
                )
     
     campaign.approval_status =True
     campaign.save()
      ## delete AIgeneratedEmail message
     AIGeneratedEmail.objects.get(campaign=campaign).delete()
     
     return  HttpResponseRedirect(reverse("campaign-add"))





class CampaignDetailsView(LoginRequiredMixin,DetailView):
     model = Campaign
     context_object_name = "campaign_details"
     template_name ="registration/campaign_detail.html"   

     def get_context_data(self, **kwargs) :
          context = super().get_context_data(**kwargs)
        

          return context





@login_required
def dashboard(request):
    return render(request,'registration/dashboard.html')

@login_required
def conversation(request):
     template_name ="registration/conversation.html"
     return render(request,template_name)



##
def resend_email_webhook_reciever(request):
     if request.method == "POST":
          print(request.POST)

     return HttpResponse()
     





