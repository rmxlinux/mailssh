import mail
import password
import base64
import time
from openai import OpenAI
import re
import console

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
        self.consoles = {}

    def findcon(self, mail):
        if mail.strip() not in self.consoles:
            self.consoles[mail.strip()] = console.console()
        return self.consoles[mail.strip()]
    def familiar(self, mail):
        self.consoles[mail].is_first = False

    def extract(self, header):
        match = re.search(r'<([^>]+)>', header)
        if match:
            return match.group(1)
        else:
            return header

    def makeprompt(self, query):
        system = ""
        who = self.extract(query["from"]).strip()
        console = self.findcon(who)
        with open(f'{console.which()}.txt', 'r', encoding='utf-8', errors='ignore') as f:
            system = f.read()

        system = system.replace('{users}', query["from"])
        return system

    def run(self):
        try:
            while True:
                query = self.mail.pull_mail_list(istest=False)
                if query:
                    for q in query:
                        who = self.extract(q["from"]).strip()
                        console = self.findcon(who)
                        isspecial, results = console.refresh(q['content'])
                        if not isspecial:
                            prompt = self.makeprompt(q)
                            reply = self.ai.make(prompt, f"主题：{q['subject']}\n\n{q['content']}")
                            print(reply)
                        else:
                            reply = '\n'.join(results)
                            print(reply)

                        self.send.send(who, f'Re: {q["subject"]}', reply)
                        if console.is_first:
                            self.send.send(who, f'使用教程', console.tutor())
                            self.familiar(who)

                time.sleep(polling_delay)

        except KeyboardInterrupt:
            self.mail.quit()
            self.send.quit()