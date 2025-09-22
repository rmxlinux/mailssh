class pwd:
    def content(self):
        return b'' #email password b64
    def api(self):
        return b'' #api key b64
    def imap(self):
        return "imap.126.com", 993, "remote_test@126.com" #imap server, your address
    def smtp(self):
        return "smtp.126.com", 465, "remote_test@126.com" #smtp server, your address
    def id(self):
        return {'name': '', 'version': '1.0', 'vendor': ''} #mail app id
    def console(self):
        return b'' #consolemode password b64

'''
import base64
print(base64.b64encode(''.encode('utf-8')))
'''