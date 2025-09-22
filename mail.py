from imapclient import IMAPClient
import password
import base64
from email.header import decode_header
from email.parser import BytesParser
from email import policy
import yagmail
import quopri
import re
import ssl
import socket

class mail:
    def __init__(self):
        self.server = None
        self.reconnect()

    def reconnect(self):
        if self.server:
            try:
                self.server.logout()
            except:
                pass
        try:
            self.imap, self.port, self.user = password.pwd().imap()
            self.server = IMAPClient(self.imap, ssl=True, port=self.port)
            self.server.login(self.user, base64.b64decode(password.pwd().content()).decode('utf-8'))
            self.server.id_(password.pwd().id())
            self.server.select_folder("INBOX")
            return True

        except Exception as e:
            return False

    def decode_mime_words(self, s):
        if s is None:
            return ""
        decoded_bytes = decode_header(s)
        return ''.join([
            part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
            for part, charset in decoded_bytes
        ])


    def extract_content_from_raw(self, raw_email_bytes):
        raw_str = raw_email_bytes.decode('latin-1', errors='ignore')
        boundary_pattern = r'boundary="?([^"\s]+)"?'
        boundary_match = re.search(boundary_pattern, raw_str, re.IGNORECASE)
        boundary = boundary_match.group(1) if boundary_match else None
        if boundary:
            parts = re.split(f'--{boundary}', raw_str)
            for part in parts:
                if 'Content-Type: text/plain' in part:
                    return self.extract_text_from_part(part)
                elif 'Content-Type: text/html' in part:
                    return self.extract_text_from_part(part)
        encoding_match = re.search(r'Content-Transfer-Encoding:\s*(\S+)', raw_str, re.IGNORECASE)
        encoding = encoding_match.group(1).lower() if encoding_match else None
        body_match = re.search(r'\r?\n\r?\n(.*)', raw_str, re.DOTALL)
        if body_match:
            body = body_match.group(1)
            return self.decode_body(body, encoding)
        return "error"


    def extract_text_from_part(self, part_str):
        content_type_match = re.search(r'Content-Type:\s*([^;\r\n]+)', part_str, re.IGNORECASE)
        content_type = content_type_match.group(1).lower() if content_type_match else 'text/plain'
        charset_match = re.search(r'charset="?([^"\s]+)"?', part_str, re.IGNORECASE)
        charset = charset_match.group(1) if charset_match else 'utf-8'
        encoding_match = re.search(r'Content-Transfer-Encoding:\s*(\S+)', part_str, re.IGNORECASE)
        encoding = encoding_match.group(1).lower() if encoding_match else None
        body_match = re.search(r'\r?\n\r?\n(.*)', part_str, re.DOTALL)
        if not body_match:
            return ""
        body = body_match.group(1).strip()
        return self.decode_body(body, encoding, charset)

    def decode_body(self, body, encoding=None, charset='utf-8'):
        try:
            if encoding == 'base64':
                decoded = base64.b64decode(body)
                return decoded.decode(charset, errors='ignore')
            elif encoding == 'quoted-printable':
                decoded = quopri.decodestring(body)
                return decoded.decode(charset, errors='ignore')
            else:
                try:
                    return body.decode(charset, errors='ignore')
                except:
                    return body.encode('latin-1').decode(charset, errors='ignore')
        except Exception as e:
            print(f"Parse Failed: {e}")
            return body


    def get_mail_content(self, email_msg, raw_email_bytes):
        try:
            plain_content = None
            html_content = None
            for part in email_msg.walk():
                content_disposition = part.get("Content-Disposition", "")
                if "attachment" in content_disposition.lower():
                    continue
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            plain_content = payload.decode(charset, errors='ignore')
                        except:
                            plain_content = payload.decode('utf-8', errors='ignore')
                elif content_type == "text/html" and not html_content:
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            html_content = payload.decode(charset, errors='ignore')
                        except:
                            html_content = payload.decode('utf-8', errors='ignore')

            if plain_content:
                return plain_content
            if html_content:
                return html_content
            return self.extract_content_from_raw(raw_email_bytes)
        except Exception as e:
            print(f"Parse Failed: {e}")
            return self.extract_content_from_raw(raw_email_bytes)

    def pull_mail_list(self, israw=False, istest=False):
        ml = []
        try:
            if not istest:
                messages = self.server.search(["UNSEEN"])
            else:
                messages = self.server.search(["ALL"])
        except Exception as e:#(ssl.SSLEOFError, ConnectionResetError, socket.error) as e:
            print(f'Disconnected. {e} Now try to reconnect')
            if self.reconnect():
                return self.pull_mail_list(israw, istest)  # 重试
            else:
                return []
        if messages:
            msg_data = self.server.fetch(messages, ["RFC822"])
            for message in messages:
                raw_email_bytes = msg_data[message][b"RFC822"]
                try:
                    email_msg = BytesParser(policy=policy.default).parsebytes(raw_email_bytes)
                except Exception as e:
                    print(f"Parse Failed: {e}")
                    email_msg = None

                subject = self.decode_mime_words(email_msg.get("subject", "") if email_msg else "")
                from_ = self.decode_mime_words(email_msg.get("from", "") if email_msg else "")
                content = self.get_mail_content(email_msg, raw_email_bytes) if email_msg else self.extract_content_from_raw(
                    raw_email_bytes)

                now_content = re.sub(r'<[^>]*>', '', content.replace('<br>','\n')) if israw else content
                ml.append( {
                    "subject": subject,
                    "from": from_,
                    "date": email_msg.get('date', '') if email_msg else 'unknown',
                    "content": now_content
                })
        return ml

    def quit(self):
        self.server.logout()

class send:
    def __init__(self):
        self.host, self.port, self.user = password.pwd().smtp()
        self.yag = yagmail.SMTP(
            user=self.user,
            password=base64.b64decode(password.pwd().content()).decode('utf-8'),
            host=self.host,
            port=self.port,
            smtp_starttls=False,
            smtp_ssl=True
        )

    def send(self, to, subject, contents, attachments=None):
        try:
            self.yag.send(
                to=to,
                subject=subject,
                contents=contents,
                attachments=attachments
            )
            return True
        except Exception as e:
            print(f"Send Failed: {e}")
            return False

    def quit(self):
        self.yag.close()
