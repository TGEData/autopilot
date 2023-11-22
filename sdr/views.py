from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, ListView, UpdateView,DeleteView
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
from .generate_followup_email import generate_emails_leads


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




class CreateCampaignView(LoginRequiredMixin,CreateView,ListView):
     model = Campaign
     form_class = None
     context_object_name = "user_campaigns"
     success_url = reverse_lazy("campaign-add")
     template_name = "registration/campaign.html"
     fields = ["campaign_summary","user_company",
               "prospect","product",]
     
     
     def get_form(self, form_class=None):
        userprofile = get_object_or_404(UserProfile,user=self.request.user)
        companie = Company.objects.filter(userprofile=userprofile)
        form = super().get_form(form_class)
        form.fields["user_company"].queryset = Company.objects.filter(userprofile=userprofile)
        form.fields["product"].queryset = Product.objects.filter(user_company__in=companie)
        form.fields["prospect"].queryset = Prospect.objects.filter(user_company__in=companie)
        return form
     
     def form_valid(self, form):

          try:

               userprofile = get_object_or_404(UserProfile,user=self.request.user)
               form.instance.userprofile = userprofile  
          
               # get all the form data 
               campaign_summary = form.cleaned_data.get('campaign_summary')
               cmp_user_company = form.cleaned_data.get('user_company')
               cmp_prospect = form.cleaned_data.get('prospect')
               cmp_product = form.cleaned_data.get('product')
          #print(str(cmp_product).split(":")[1])
               # filter data for to AI generate email


          #get product data
               products = Product.objects.filter(property_name=str(str(cmp_product).split(sep=":")[1]).split(" ")[1]).first()
               ai_property_name = products.property_name
               ai_property_description = products.property_description

          # get company data 
               companies = Company.objects.filter(company_name=cmp_user_company).first()
               ai_company_name = companies.company_name
               ai_company_website = companies.company_website
               ai_campaign_identifier = companies.company_identifier

          #get prospect data
               user_prospect = Prospect.objects.filter(user_company=cmp_user_company).first()
               ai_prospect_fullname = "{} {}".format(user_prospect.first_name,user_prospect.last_name)
               ai_prospect_current_title = user_prospect.current_title
               ai_prospect_current_company = user_prospect.current_company
               ai_prospect_email = user_prospect.email


          # openai function to generate email base on the following context product, prospect,company

               generate_emails_leads(openai_api_key="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",
                                   campaign_summary=campaign_summary,property_name=ai_company_name,
                                   property_description=ai_property_description,company_name=ai_company_name,
                                   company_website=ai_company_website,prospect_fullName=ai_prospect_fullname,
                                   prospect_current_title=ai_prospect_current_title,prospect_current_company=ai_prospect_current_company,
                                   sales_lead_username=self.request.user.username,
                                   ai_prospect_email=ai_prospect_email
                                   )     
          except:
              pass
          return super().form_valid(form)



     





@login_required
def dashboard(request):
    return render(request,'registration/dashboard.html')





