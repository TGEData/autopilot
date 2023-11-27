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
                          prospect_fullName=None,
                          prospect_current_title=None,
                          prospect_current_company =None,
                          sales_lead_username=None,
                          campaign=None,
                          ai_prospect_email=None
                          ):
   
   
   chat_model = ChatOpenAI(openai_api_key=openai_api_key)
   

   messages = [
    SystemMessage(
        content="You are a helpful assistant  that generate Customer Relationship Management (CRM) email in  English "
    ),
    ]
   
   template_samples = f"""
    Subject: Unlock Exclusive Benefits in {campaign_summary} - Elevate with {property_name}

    Hi {prospect_current_title} {prospect_fullName},

    I hope this email finds you thriving! I'm {sales_lead_username}, representing {company_name}, the driving force behind transformative solutions in [industry or relevant field].

    I'm reaching out to you with excitement, especially considering your pivotal role at {prospect_current_company}. As a forward-thinking leader, you're ideally positioned to leverage 
    the innovation we're introducing in our current campaign, "{campaign_summary}."

    At the heart of this campaign is our groundbreaking product, "{property_name}." Imagine {property_description} — 
    a true game-changer in the {prospect_current_company} landscape. What sets {company_name} apart?

    We understand the unique challenges faced by {prospect_current_company}, and {property_name} is meticulously crafted to address these pain points.

    Here's the exciting part: By joining forces with us in {campaign_summary}, you unlock exclusive benefits, including [Highlight 1], [Highlight 2], and [Highlight 3].

    I'm eager to discuss how {property_name} aligned with the {campaign_summary} initiative can seamlessly integrate into {company_name}'s operations, boost efficiency, and drive notable ROI.

    Can we carve out 15 minutes for a conversation next week? Your insights are invaluable, and I believe this could be the start of something truly impactful.

    Feel free to pick a slot from my calendar , or suggest a time that suits you best.

    Let's embark on this journey together and elevate {company_name} to new heights!

    Best regards,

    {sales_lead_username}
    Head of sales at {company_name}
    {company_name}
    {company_website}
    """
   augmented_prompt = f"""Use the following email template sample to generate email lead for a crm platform.
    Email Template:
    {template_samples}
    """

   prompt = HumanMessage(content=augmented_prompt)

   messages.append(prompt)

   response_email = chat_model(messages)

   # save the generated email to the data base

   models.AIGeneratedEmail.objects.create(
    campaign = campaign,
    campaign_generated_email_template = response_email.content,
    prospect_email=ai_prospect_email
   )
   return





#email_leads = generate_emails_leads(openai_api_key="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",
                              #campaign_summary="it crisma day",property_name="nike",
                               #property_description="nice company",company_name="fashion",
                               #company_website="owolabi.com",prospect_fullName="owolabi akintan",
                              # prospect_current_title="mr",prospect_current_company="lion",
                               #sales_lead_username="gaga"
                               #)

