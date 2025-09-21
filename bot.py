import mail
import password
import base64
import time
from openai import OpenAI
import re

polling_delay = 60.0

class gpt:
    def __init__(self, API_KEY):
        self.client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

    def make(self, system, prompt):
        messages = [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': prompt}
        ]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False,
            temperature=1.5
        )
        reply = response.choices[0].message.content
        return reply

class bot:
    def __init__(self):
        self.mail = mail.mail()
        self.send = mail.send()
        self.api_key = base64.b64decode(password.pwd().api()).decode('utf-8')
        self.ai = gpt(self.api_key)

    def extract(self, header):
        match = re.search(r'<([^>]+)>', header)
        if match:
            return match.group(1)
        else:
            return header

    def makeprompt(self, query):
        system = ""
        with open('kalts.txt', 'r', encoding='utf-8', errors='ignore') as f:
            system = f.read()

        system = system.replace('{users}', query["from"])
        return system

    def run(self):
        try:
            while True:
                query = self.mail.pull_mail_list(istest=False)
                if query:
                    for q in query:
                        prompt = self.makeprompt(q)
                        reply = self.ai.make(prompt, f"主题：{q['subject']}\n\n{q['content']}")
                        self.send.send(self.extract(q['from']), f'Re: {q["subject"]}', reply)
                        print(reply)

                time.sleep(polling_delay)

        except KeyboardInterrupt:
            self.mail.quit()
            self.send.quit()