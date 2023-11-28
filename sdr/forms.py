from django import forms
from core.models import UserProfile,Company
from .models import Campaign,Product,Prospect,Conversion,EmailActivity,EmailProvider,AIGeneratedEmail



class CampaignForm(forms.ModelForm):
    
    class Meta:
        model = Campaign
        fields = ("campaign_summary","company","prospect","product")



class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ("property_name","property_sector","property_description","property_url")

class ProspectForm(forms.ModelForm):
    
    class Meta:
        model = Prospect
        fields = ("source_identifier","source","first_name",
                  "last_name","current_title","current_company",
                  "email","photo_url","facebook_url","twitter_url","linkedin_url")


class CompanyForm(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = ("company_name","company_website")











