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
from .models import Product,Prospect,Conversion,CompanyEmailProvider,EmailActivity,Campaign,AIGeneratedEmail,Contacts
from django.views.generic.edit import CreateView,DeleteView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from background_task import background
from .generatefollowupemail import generate_emails_leads,send_email,send_batch_email
from django.core.mail import EmailMessage, get_connection
import os
from . forms import CampaignForm,UploadProspectForm,ProspectForm,ContactForm
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import clean_upload_data
from django.contrib import messages
import shutil
from django.core.paginator import Paginator



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
     paginate_by = 10
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
     def form_valid(self, form):
         messages.success(self.request, "Product created successfull")
         return super().form_valid(form)
     


        
     def get_form(self, form_class=None):
        userprofile = get_object_or_404(UserProfile,user=self.request.user)
        form = super().get_form(form_class)
        form.fields["user_company"].queryset = Company.objects.filter(userprofile=userprofile)
        return form
     

@login_required 
def prospect_upload_view(request):
     userprofile = UserProfile.objects.filter(user=request.user)
     user_company = Company.objects.filter(userprofile__in=userprofile)
     user_prospect = Prospect.objects.filter(user_company__in=user_company)
     prospectcreate_form = ProspectForm(userprofile=userprofile)
     prospect_uploadform = UploadProspectForm(userprofile=userprofile)

     template_name = "registration/prospect.html"

     db_column = ['source_identifier',
             'source','first_name',
             'last_name','current_title',
             'current_company','email',
             'photo_url','facebook_url',
             'twitter_url','linkedin_url'
             ]

     if request.method == "POST":
          prospect_uploadform = UploadProspectForm(userprofile,request.POST,request.FILES)

          if prospect_uploadform.is_valid():
               file = request.FILES['file']
               company = prospect_uploadform.cleaned_data['user_company']
               company_obj = get_object_or_404(Company,company_name=company)

               response = clean_upload_data(file,company_obj=company_obj,dbcolumn=db_column,Prospect=Prospect)
               if response == True:
                    messages.success(request, "Prospect document uploaded successfull")
                    return render(request,template_name,{'user_prospect':user_prospect,
                                                         'form':prospectcreate_form,
                                                         "prospect_uploadform": prospect_uploadform})
               elif response == False:
                    messages.error(request, "unable to upload the document you provide please check to make sure it match with our database the document field and try again")
                    return render(request,template_name,{'user_prospect':user_prospect,
                                                         'form':prospectcreate_form,
                                                         "prospect_uploadform": prospect_uploadform})
                    

     return  HttpResponseRedirect(reverse("prospect-add"))


@login_required   
def create_prospect_view(request):
     userprofile = UserProfile.objects.filter(user=request.user)
     user_company = Company.objects.filter(userprofile__in=userprofile)
     user_prospect = Prospect.objects.filter(user_company__in=user_company)
     template_name = "registration/prospect.html"
     paginator = Paginator(user_prospect,8)  # Show 25 contacts per page.
     page_number = request.GET.get("page")
     prospect_page_obj = paginator.get_page(page_number)
     
     
     if request.method == "POST":
          prospectcreate_form = ProspectForm(userprofile,request.POST)
          prospect_uploadform = UploadProspectForm(userprofile,request.POST,request.FILES)
          
          if prospectcreate_form.is_valid():
               prospectcreate_form.save()
               messages.success(request, "Prospect created successfull")
               HttpResponseRedirect(reverse("prospect-add"))

     else:
          prospectcreate_form = ProspectForm(userprofile=userprofile)
          prospect_uploadform = UploadProspectForm(userprofile=userprofile)
        
     return render(request,template_name,{'form':prospectcreate_form,
                                          "prospect_uploadform": prospect_uploadform,"prospect_page_obj":prospect_page_obj})

     

class ContactView(LoginRequiredMixin,CreateView,ListView):
     paginate_by = 10
     model = Contacts
     form_class = ContactForm
     context_object_name = "contacts_obj"
     template_name ="registration/contacts.html"
     success_url = reverse_lazy("contact-add")

     def form_valid(self, form):
          userprofile = get_object_or_404(UserProfile,user=self.request.user)
          form.instance.user = userprofile
          return super().form_valid(form)
     
     def get_form(self, form_class=None) -> BaseModelForm:
          userprofile = get_object_or_404(UserProfile,user=self.request.user)
          user_company = Company.objects.filter(userprofile=userprofile)
          form = super().get_form(form_class)
          form.fields['prospect'].queryset = Prospect.objects.filter(user_company__in=user_company)
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
     userprofileform = UserProfile.objects.filter(user=request.user)
     campaign_object_data = Campaign.objects.filter(userprofile__in=userprofileform)

     paginator = Paginator(campaign_object_data,8)  # Show 25 contacts per page.
     page_number = request.GET.get("page")
     campaign_page_obj = paginator.get_page(page_number)
     
     if request.method == "POST":
          form = CampaignForm(userprofileform,request.POST)
          if  form.is_valid():
               campaign_instance =  form.save(commit=False)
               campaign_instance.userprofile = userprofile
               campaign_instance.save()
              
          
               # get all the form data 
               campaign_summary = form.cleaned_data.get('campaign_summary')
               cmp_user_company = form.cleaned_data.get('user_company')
               cmp_contacts = form.cleaned_data.get('contacts')
               cmp_product = form.cleaned_data.get('product')
          
               


          #get product data
               products = Product.objects.filter(property_name=cmp_product).first()
               ai_property_description = products.property_description
               ai_property_name = products.property_name
               #print(ai_property_description)

          # get company data 
               companies = Company.objects.filter(company_name=cmp_user_company).first()
               ai_company_name = companies.company_name
               ai_company_website = companies.company_website
               #ai_company_identifier = companies.company_identifier

          #get prospect data
               #user_prospect = Prospect.objects.filter(user_company=cmp_user_company).first()
              
             
               #ai_prospect_current_title = user_prospect.current_title
               #ai_prospect_current_company = user_prospect.current_company
               #ai_prospect_email = user_prospect.email

               generate_emails_leads(openai_api_key="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",
                                  campaign_summary=campaign_summary,
                                  property_name=ai_property_name,
                                  property_description=ai_property_description,
                                  company_name=ai_company_name,
                                  company_website=ai_company_website,
                                  sales_lead_username=request.user.username,
                                  campaign=campaign_instance.id,
                                 
                                   )

               messages.success(request, "Campaign created successfull")
               HttpResponseRedirect(reverse("campaign-add"))

     else:
         form = CampaignForm(userprofileform)

     return render(request,template_name,{"form":form,"user_campaigns":campaign_page_obj})
          



def send_prospect_email(request,campaign_id):
     ## get campaign by id
     campaign = get_object_or_404(Campaign,pk=campaign_id)
    
     ## get contact data and prospect
     prospect_emails = [emails.email for emails in campaign.contacts.prospect.all()]

     ## get generated email template
     aigenerated_email = AIGeneratedEmail.objects.get(campaign=campaign_id)
     property_name = Product.objects.get(campaign=campaign)
     #print(property_name.property_name)

     ## extract the first line as subject
     subject = campaign.campaign_summary
     messsage = f"{aigenerated_email.campaign_generated_email_template}"
     for emails in prospect_emails:
      
      
      send_email(subject=subject,
              message=messsage,
               recipient_list=[emails],
               api_key=os.environ.get('RESEND_API_KEY'),
               host=settings.RESEND_SMTP_HOST,
               port=settings.RESEND_SMTP_PORT,
                EmailMessage=EmailMessage,
                get_connection=get_connection
               )
     
     campaign.approval_status =True
     campaign.save()
      ## delete AIgeneratedEmail message
     #AIGeneratedEmail.objects.get(campaign=campaign).delete()
     
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



@csrf_exempt
def resend_email_webhook_reciever(request):
     prospect_emails = Prospect.objects.all()
    
     if request.method == "POST":
         
          emailresponse = json.loads(request.body.decode('utf-8'))
          prospect_emails_address = [email.email for email in prospect_emails]
          #print(prospect_emails_address)
         
           
          if emailresponse['type'] == "email.sent":
               sent_email = [email for email in emailresponse.get('data')['to'] for email in prospect_emails_address if email in email]

               unique_prospect_email = set(sent_email)

               if len(unique_prospect_email)<=1:
                    # send email 
                    send_email()
               else:
                    ## send batch email
                    send_batch_email()

     
     
          elif emailresponse['type'] == "email.opened":
                # generate customize email using openai and resend to the prospect 
               opened_emails =[email for email in emailresponse.get('data')['to'] for email in prospect_emails_address if email in email]
               unique_prospect_email =  set(sent_email)

               if len(unique_prospect_email)<=1:
                    # send email 
                    send_email()
               else:
                    ## send batch email
                    send_batch_email()

          
               
          elif emailresponse['type'] == "email.clicked":
                
                # generate customize email using openai and resend to the prospect 
                click_emails =[email for email in emailresponse.get('data')['to'] for email in prospect_emails_address if email in email]
                unique_prospect_email =  set(sent_email)

                if len(unique_prospect_email)<=1:
                    # send email 
                    send_email()
                else:
                    ## send batch email
                    send_batch_email()

          elif "email.clicked" in emailresponse['type'] and "email.opened" in emailresponse['type']:
                opened_click_emails =[email for email in emailresponse.get('data')['to'] for email in prospect_emails_address if email in email]
                unique_prospect_email =  set(sent_email)

                if len(unique_prospect_email)<=1:
                    # send email 
                    send_email()
                else:
                    ## send batch email
                    send_batch_email()
                
          else:
               print("email Delievered")

          

     return JsonResponse({"status":"200 : success"})
     

def usersview(request):
     template_name ="registration/users.html"
     return render(request,template_name)


###update views.....................................

class AIGeneratedEmailView(LoginRequiredMixin,UpdateView):
     template_name ="registration/generated_email_edit.html"
     model = AIGeneratedEmail
     fields = ["campaign_generated_email_template"]
     
     success_url = reverse_lazy('campaign-details')

     def get_success_url(self):
        email_pk = get_object_or_404(AIGeneratedEmail,pk=self.object.pk)  
        return reverse_lazy('campaign-details', kwargs={'pk':email_pk.campaign.id})
     

###update views.....................................





#### delete views.......................

def productdelete(request,product_id):
     get_object_or_404(Product,pk=product_id).delete()
     return  HttpResponseRedirect(reverse("product-add"))


def prospectdelete(request,prospect_id):
     get_object_or_404(Prospect,pk=prospect_id).delete()
     return  HttpResponseRedirect(reverse("prospect-add"))



def campaigndelete(request,campaign_id):
     get_object_or_404(Campaign,pk=campaign_id).delete()
     return  HttpResponseRedirect(reverse("campaign-add"))


def contactdelete(request,contact_id):
     get_object_or_404(Contacts,pk=contact_id).delete()
   
     return  HttpResponseRedirect(reverse("contact-add"))


def companydelete(request,company_id):
     get_object_or_404(Company,pk=company_id).delete()
    
     return  HttpResponseRedirect(reverse("company-add"))

#### delete views..........................