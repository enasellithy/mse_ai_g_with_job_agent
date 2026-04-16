import os
import asyncio
import google.generativeai as genai
import requests
from playwright.async_api import async_playwright

genai.configure(api_key=os.getenv("GEMINI_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

async def fetch_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        search_query = "Python Developer jobs in Riyadh"
        await page.goto(f"https://www.google.com/search?q={search_query}&ibp=htl;jobs")
        await page.wait_for_timeout(5000) 
        job_titles = await page.locator('[role="heading"]').all_inner_texts()
        await browser.close()
        return job_titles[:5] 

def analyze_and_notify(jobs):
    summary = "\n".join(jobs)
    prompt = f"هذه قائمة وظائف: {summary}. لخصها في نقاط سريعة وأخبرني أيها الأفضل لمبرمج بايثون خبير."
    
    response = model.generate_content(prompt)
    
    webhook_url = os.getenv("DISCORD_URL")
    data = {
        "content": f"🚀 **تقرير البحث (كل 6 ساعات):**\n\n{response.text}"
    }
    requests.post(webhook_url, json=data)

if __name__ == "__main__":
    jobs_found = asyncio.run(fetch_jobs())
    analyze_and_notify(jobs_found)
