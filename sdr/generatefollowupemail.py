from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from background_task import background
from . import models
import os
import resend


from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

## send email with resend
#@background(schedule=60)
def send_email(subject,message,recipient_list:list,api_key,host,port,EmailMessage,get_connection,username="resend",from_email="onboarding@resend.dev"):
    subject =  subject
    recipient_list =  recipient_list
    from_email = from_email
    message = message

    with get_connection(
        host=host,
        port=port,
        username=username,
        password=api_key,
        use_tls=True,
        ) as connection:
            r = EmailMessage(
                  subject=subject,
                  body=message,
                  to=recipient_list,
                  from_email=from_email,
                  connection=connection).send()
    return  {"status": "ok"}


def send_batch_email(messages:list,api_key):
     # send batch email.......
    resend.api_key = api_key
    email = resend.Batch.send(messages)
    print(email)

    return 


#@background(schedule=60)
def generate_emails_leads(openai_api_key=None,
                          campaign_summary=None,
                          property_name=None,
                          property_description=None,
                          company_name=None,company_website=None,
                          sales_lead_username=None,
                          campaign=None,
                          ):
   
   
   chat_model = ChatOpenAI(openai_api_key=openai_api_key)
   

   messages = [
    SystemMessage(
        content="You are a helpful assistant"
    ),
    ]
   
   template_samples = f"""
    {campaign_summary} 
     {property_name}
    {property_description} — 
   
    {sales_lead_username}
    {company_name}
    {company_website}
    """
   augmented_prompt = f"""Use the following infomation to generate short informal latter email lead and make sure you add my website link if you find one on the information provide please make it a very short and descriptive and intutive email that a client will love.
    Email Template:
    {template_samples}
    """

   prompt = HumanMessage(content=augmented_prompt)

   messages.append(prompt)

   response_email = chat_model(messages)

   # save the generated email to the data base
   campaigns_data = models.Campaign.objects.get(pk=campaign)
   models.AIGeneratedEmail.objects.create(
    campaign = campaigns_data,
    campaign_generated_email_template = response_email.content,
   )
   





#email_leads = generate_emails_leads(openai_api_key="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",
                              #campaign_summary="it crisma day",property_name="nike",
                               #property_description="nice company",company_name="fashion",
                               #company_website="owolabi.com",prospect_fullName="owolabi akintan",
                              # prospect_current_title="mr",prospect_current_company="lion",
                               #sales_lead_username="gaga"
                               #)

