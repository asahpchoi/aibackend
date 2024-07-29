from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from openai import AzureOpenAI
from bs4 import BeautifulSoup
import os, sys, base64

load_dotenv(override=True)

client = AzureOpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("AZURE_OAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
)

if __name__ == "__main__":
    url = sys.argv[1]
    with sync_playwright() as playwright:
        chrome = playwright.chromium
        browser = chrome.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state()
        html = page.content()
        # screenshot = page.screenshot(full_page=True)
        # screenshot = base64.b64encode(screenshot).decode('utf-8')
        browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.text
        try:
            web_page_report = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {
                        'role':'system',
                        'content':"""### Role
    You are a helpful assistant for extracting as much information from a webpage as possible.

    ### Instruction
    You will be given raw text from a webpage. 
    You will distill the main content and render only the main content. 
    Do not attempt to give summary and include all important details.
    Respond in the original language on the webpage."""
                    },
                    {
                        'role':'user',
                        'content':[
                            {
                                "type":"text",
                                "text":text
                            },
                            # {
                            #     "type":"image_url",
                            #     "image_url":{
                            #         "url":f"data:image/png;base64,{screenshot}"
                            #     }
                            # }
                        ]
                    }
                ]
            )
        except Exception as e:
            print(e)
    
    print(web_page_report.choices[0].message.content)