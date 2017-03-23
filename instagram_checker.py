import aiohttp, asyncio, argparse

async def check_usernames(igname, igpass, username, sem, session, loop=None):
    async with sem:
        try:
            url = 'https://www.instagram.com/{}'
            url = url.format(username)
            async with session.get(url) as resp:
                text = await resp.text()
                if "Page Not Found" in text:
                    save_username(username, outputfile)
        except Exception:
            print(Exception)

async def start_check(igname, igpass, usernames, conns=50, loop=None):
    sem = asyncio.BoundedSemaphore(conns)
    async with aiohttp.ClientSession(loop=loop) as session:
        await login(igname, igpass, session)
        tasks = [check_usernames(igname, igpass, username, sem, session, loop=loop) for username in usernames]
        await asyncio.gather(*tasks)

def get_usernames(inputfile):
    with open(inputfile, "r") as f:
        usernames = f.read().split("\n")
        return usernames

def save_username(username, outputfile):
    with open(outputfile, "a") as a:
        a.write(username+'\n')

async def login(username, password, session):
    loginurl = 'https://www.instagram.com/accounts/login/ajax/'
    url = 'https://www.instagram.com/{}'
    url = url.format('')

    async with session.get(url) as response:
        csrftoken = await response.text()

    csrftoken = csrftoken.split('csrf_token": "')[1].split('"')[0]

    async with session.post(
            loginurl,
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
                pass
            else:
                print(text)

def main(igname, igpass):
    loop = asyncio.get_event_loop()
    usernames = get_usernames(inputfile)
    try:
        loop.run_until_complete(start_check(igname, igpass, usernames))
    finally:
        loop.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest='username', help="Instagram username",
                        action="store")
    parser.add_argument("-p", dest='password', help="Instagram password",
                        action="store")
    parser.add_argument("-i", dest='inputfile', help="Textfile with usernames",
                        action="store")
    parser.add_argument("-o", dest='outputfile', help="Output textfile",
                        action="store")
    args = parser.parse_args()

    igname = args.username
    igpass = args.password
    inputfile = args.inputfile
    outputfile = args.outputfile

    with open(outputfile, "w") as a:
        print('Output file cleared.')

    main(igname, igpass)
