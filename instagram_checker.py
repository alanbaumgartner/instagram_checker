import requests, argparse, sys

class checker:
    def __init__(self):

        #Declare some variables
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.loginurl = 'https://www.instagram.com/accounts/login/ajax/'
        self.url = 'https://www.instagram.com/'

        #Start a session and update headers
        self.s = requests.session()
        self.s.headers.update(self.headers)


        #Gets username, password, textfile to check usernames, and output file for available usernames.
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", dest='username', help="Instagram username",
                            action="store")
        parser.add_argument("-p", dest='password', help="Instagram password",
                            action="store")
        parser.add_argument("-i", dest='inputf', help="Textfile with usernames",
                            action="store")
        parser.add_argument("-o", dest='outputf', help="Output textfile",
                            action="store")
        args = parser.parse_args()

        #Save variables from argparse
        self.username = args.username
        self.password = args.password
        self.inputf = args.inputf
        self.outputf = args.outputf

    def login(self, username, password):
        #Logs into instagram
        loginRequest = self.s.post(
                self.loginurl,
                    headers={
                        'x-csrftoken': self.s.get(self.url).text.split('csrf_token": "')[1].split('"')[0],
                        'x-instagram-ajax':'1',
                        'x-requested-with': 'XMLHttpRequest',
                        'Origin': self.url,
                        'Referer': self.url,
                    },
                    data={
                        'username':username,
                        'password':password,
                    }
                )
            
        if loginRequest.json()['authenticated']:
            print('Logged In.')
        else:
            sys.exit("Login Failed, closing program.")

    def get_usernames(self, filename):
        #Gets username from file
        with open(filename, "r") as f:
            usernames = f.read().split("\n")
            return usernames

    def check_usernames(self, username, output):
        #checks username and saves available usernames to new file
        for user in usernames:
            r = self.s.get(self.url+user)
            al = r.text
            text = al[al.find('<title>') + 7 :al.find('</title>')]
            if "Page Not Found" in text:
                with open(output, "a") as a:
                    a.write(user+'\n')

if __name__ == "__main__":
    check = checker()
    check.login(check.username, check.password)

    #Clears output file for new usernames
    with open(check.outputf, "w") as a:
        print('Output file cleared.')
        
    usernames = check.get_usernames(check.inputf)
    check.check_usernames(usernames, check.outputf)
