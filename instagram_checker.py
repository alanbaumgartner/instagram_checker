import argparse, sys, asyncio, aiohttp, time

class checker:
    def __init__(self):

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

        self.loginurl = 'https://www.instagram.com/accounts/login/ajax/'
        self.url = 'https://www.instagram.com/{}'

    async def login(self, session, username, password):
        #Logs into instagram
        url = self.url.format('')

        async with session.get(url) as response:
            csrftoken = await response.text()

        csrftoken = csrftoken.split('csrf_token": "')[1].split('"')[0]

        async with session.post(
                self.loginurl,
                    headers={
                        'x-csrftoken': csrftoken,
                        'x-instagram-ajax':'1',
                        'x-requested-with': 'XMLHttpRequest',
                        'Origin': url,
                        'Referer': url,
                    },
                    data={
                        'username':username,
                        'password':password,
                    }
                ) as response:

                text = await response.json()
                if 'authenticated' in text:
                    print('Logged In.')
                else:
                    print(text)
                    sys.exit("Login Failed, closing program.")
        
    def get_usernames(self, input):
        #Gets username from file
        with open(input, "r") as f:
            usernames = f.read().split("\n")
            return usernames

    def save_username(self, username, output):
        #checks username and saves available usernames to new file
        with open(output, "a") as a:
            a.write(user+'\n')

    async def check_username(self, session, username):
        #checks username and saves available usernames to new file
        async with session.get(self.url.format(username)) as response:
            text = await response.text()
            text = text[text.find('<title>') + 7 :text.find('</title>')]
            if "Page Not Found" in text:
                return self.save_username(username, self.outputf)

    async def setup_usernames(self, session, usernames):
        #Sets up tasks to check usernames
        count = 0
        total = len(usernames)
        for username in usernames:
            count += 1
            await asyncio.ensure_future(self.check_username(session, username))
            if count % 25 == 0:
                print('Tested', count, 'of', total)

    async def main(self, session, loop):
        await self.login(session, self.username, self.password)
        usernames = self.get_usernames(self.inputf)
        await self.setup_usernames(session, usernames)

if __name__ == "__main__":
    check = checker()

    #Clears output file for new usernames
    with open(check.outputf, "w") as a:
        print('Output file cleared.')

    loop = asyncio.get_event_loop()

    session = aiohttp.ClientSession(loop=loop)

    tasks = [
        asyncio.ensure_future(check.main(session, loop))
    ]

    loop.run_until_complete(asyncio.wait(tasks))
