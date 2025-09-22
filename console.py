import password
import base64
import state
import os
import subprocess
import mail

class console:
    def __init__(self):
        self.patterns = ["----------回复的邮件信息----------", "-----Original Messages-----"]
        self.password = base64.b64decode(password.pwd().console()).decode('utf-8').strip()
        self.state = state.state()
        self.timeout = 30
        self.is_first = True

    def is_console(self):
        return self.state.is_console
    def which(self):
        return self.state.agent

    def cut(self, content):
        for pattern in self.patterns:
            if content.find(pattern) != -1:
                return content[:content.find(pattern)]
        return content

    def menu(self):
        op_list = os.listdir('.')
        menu = []
        for op in op_list:
            if op.endswith('.txt'):
                menu.append(op[:op.find('.txt')])
        return ','.join(menu)

    def tutor(self):
        return f"""
----------------------------------------------
远程邮件聊天及操控程序 02.0922
您可以通过"change_to [角色名]"来切换智能体。注意：新的智能体在下一封邮件开始生效。
可用的智能体有：{self.menu()}。
您可以用"helpme"来重新发送此邮件。
----------------------------------------------   
        """
    def run(self, command):
        if not command:
            return ""
        try:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            output = f"----Output of command {command}----\n"
            output += f"With exit:  {result.returncode}\n"
            if result.stdout:
                output += f"\n{result.stdout}\n"
            if result.stderr:
                output += f"Error:\n{result.stderr}\n"
            return output

        except subprocess.TimeoutExpired:
            return (f"Time exceed {self.timeout}ms : {command}")
        except Exception as e:
            return (f"Failed: {command}\nError(s): {str(e)}")

    def refresh(self, content):
        contents = self.cut(content).strip().split('\n')
        results = []
        for line in contents:
            line = line.strip()
            if line.find(f"console{self.password}") != -1:
                self.state.is_console = True
                results.append("Console mode on")

            elif line.find(f"turn{self.password}") != -1 or line.find(f"change_to") != -1:
                parts = line.split()
                if len(parts) >= 2:
                    if os.path.exists(f'{parts[1]}.txt'):
                        self.state.agent = parts[1]
                results.append(f"The agent turn to {parts[1]}")

            elif line.find(f"end{self.password}") != -1:
                self.state.is_console = False
                results.append("Console mode off")

            elif line.find('helpme') != -1:
                results.append(self.tutor())

            #the command below is only allowed in console mode.
            elif self.is_console() and line[0] == '!':
                results.append(self.run(line[1:].strip()))

            elif self.is_console() and line.find(f"which"):
                results.append(self.state.agent)

        if results or self.is_console():
            return True, results
        else:
            return False, results
