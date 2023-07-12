from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from socket import gaierror
from pretty_html_table import build_table, pretty_html_table



class MailerClass(): 
    ''' Emails team on a daily/weekly basis the results of the port scanning '''

    def __init__(self, html_open, html_continued, html_closed, recentfilename, todayfilename):
        self.html_closed_table = html_closed
        self.html_continued_table = html_continued
        self.html_open_table = html_open
        self.yfname = recentfilename
        self.tfname = todayfilename

        self.port = 25
        self.smtp_server = '' # SMTP Server
        self.login_username = '' # Login Username
        self.login_password = '' # Login Password 
        self.sender_email = '' # Sender Email 
        self.email_list = []
        self.date = date.today().strftime('%d %B, %Y')
    
    def email_results(self):
        ''' Send results of daily diff to team '''
    
        today_date = self.tfname.split("/")[-1].split(".")[0]
        yesterday_date = self.yfname.split("/")[-1].split(".")[0]


        try:
            message = MIMEMultipart('related')

            message['Subject'] = f'Internal Network Port Scan Results: {yesterday_date} - {today_date}'
            message['From'] = self.sender_email
            recipients = [''] # Recipients of email
            message['To'] = ", ".join(recipients)

            html = """\
            <html>
            <head></head>
            <body style="font-family:Calibri;font-size:14.5px">
                <p>Hi,</p>
                <p>Attached below are the results from the Internal Network Port Scan.</p>
                <p>This scan was completed on {0} and is comparing to the most recent scan completed on {1}</p>
                <p>Here are newly opened ports: </p>
                {2}
                <p>Here are ports that have been closed: </p>
                {3}
                <p>Here are ports that have stayed open: </p>
                {4}

                <br><p>Regards,</p>
                <p>Palaash </p>

                
            </body>
            </html>

            """.format(today_date, yesterday_date, self.html_open_table, self.html_closed_table, self.html_continued_table)
            partHTML = MIMEText(html, 'html')
            message.attach(partHTML)
            self.send_email(message, message['To'])
        except Exception as e: 
            print('Could not email contents' + str(e))
        
    def send_email(self, message, receiver_email):
        ''' Send email over RBA SMTP '''
        try: 
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.login(self.login_username, self.login_password)
                server.send_message(message)
                print('Message sent!')
        except (gaierror, ConnectionRefusedError):
            print('Failed to connect to the server. Bad connection settings')
        except smtplib.SMTPServerDisconnected:
            print('Failed to connect to the server. Wrong user/password')
        except smtplib.SMTPException as e: 
            print('SMTP error pccured: ' + str(e))

    def main(self):
        self.email_results()

def main():
    MailerClass.main()

if __name__ == "__main__": 
    main()