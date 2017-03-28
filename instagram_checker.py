import aiohttp, asyncio, argparse, os, sys

__author__ = "Alan Baumgartner"

def get_usernames(inputfile):
    #Gets usernames to check from a file
    try:
        with open(inputfile, "r") as f:
            usernames = f.read().split("\n")
            return usernames
    except:
        sys.exit(str(inputfile) + ' does not exists')

def save_username(username, outputfile):
    #Saves available usernames
    with open(outputfile, "a") as a:
        a.write(username+'\n')

async def check_usernames(username, sem, session, loop=None):
    #Checks username availability
    async with sem:
        try:
            async with session.get(URL.format(username)) as resp:
                text = await resp.text()
                if "Page Not Found" in text:
                    save_username(username, outputfile)
        except Exception:
            print(Exception)

async def start_check(igname, igpass, conns=50, loop=None):
    #Packs all usernames into a tasklist
    sem = asyncio.BoundedSemaphore(conns)
    async with aiohttp.ClientSession(loop=loop) as session:
        await login(igname, igpass, session)
        usernames = get_usernames(inputfile)
        tasks = [check_usernames(username, sem, session, loop=loop) for username in usernames]
        await asyncio.gather(*tasks)

async def login(username, password, session):
    #Logs into Instagram
    async with session.get(URL.format('')) as response:
        csrftoken = await response.text()

    csrftoken = csrftoken.split('csrf_token": "')[1].split('"')[0]

    async with session.post(
            LOGIN_URL,
                headers={
                    'x-csrftoken': csrftoken, 'x-instagram-ajax':'1',
                    'x-requested-with': 'XMLHttpRequest',
                    'Origin': URL, 'Referer': URL
                    },
                data={
                    'username':username, 'password':password
                }
            ) as response:

            text = await response.json()
            if 'authenticated' in text:
                pass
            else:
                sys.exit(text)

def main(igname, igpass):
    #Starts the loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_check(igname, igpass))
    finally:
        loop.close()

if __name__ == "__main__":
    #Command line parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest='username', action="store")
    parser.add_argument("-p", dest='password', action="store")
    parser.add_argument("-i", dest='inputfile', action="store")
    parser.add_argument("-o", dest='outputfile', action="store")
    args = parser.parse_args()

    #Assign command line values to variables
    igname = args.username
    igpass = args.password
    inputfile = args.inputfile
    outputfile = args.outputfile

    #Global constants
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    URL = 'https://www.instagram.com/{}'

    if os.path.exists(outputfile):
        #Clears output files
        with open(outputfile, "w") as a:
            print('Output file cleared.')

    #Starts downloading
    main(igname, igpass)
