from django import forms
from core.models import UserProfile,Company
from .models import Campaign,Product,Prospect,Conversion,EmailActivity,EmailProvider,AIGeneratedEmail



class CampaignForm(forms.ModelForm):
    
    class Meta:
        model = Campaign
        fields = ("campaign_summary","user_company","prospect","product")



class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ("property_name","property_sector","property_description","property_url")



class ProspectForm(forms.ModelForm):
    
    class Meta:
        model = Prospect
        fields = ("user_company","source_identifier","source","first_name",
                  "last_name","current_title","current_company",
                  "email","photo_url","facebook_url","twitter_url","linkedin_url")
        
    def __init__(self, userprofile, *args, **kwargs):
        super(ProspectForm, self).__init__(*args, **kwargs)
        self.fields['user_company'].queryset =Company.objects.filter(userprofile__in=userprofile)


class CompanyForm(forms.ModelForm):
    
    class Meta:
        model = Company
        fields = ("company_name","company_website")



class UploadProspectForm(forms.Form):
    user_company = forms.ModelChoiceField(queryset=None)
    file = forms.FileField()

    def __init__(self, userprofile,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user_company"].queryset = Company.objects.filter(userprofile__in=userprofile)









