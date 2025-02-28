import requests
from models import create_login, get_login

url = "https://login.emaktab.uz"
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
}

async def login():
    wrong_logins = ''
    l = 0
    for login in (await get_login()):
        r = requests.post(url, headers=headers, data={"login": login.login, "password": login.password})
        if len(r.cookies) == 1:
            wrong_logins+=f"Login: {login.login} 🔑 Password: {login.password},\n"
            await create_login(login=login.login, password=login.password,status=False)
        else:
            await create_login(login=login.login, password=login.password,status=True)
            l += 1
    return wrong_logins, l


async def login_main(data):
    wrong_logins = ''
    l = 0
    for login in data:
        r = requests.post(url, headers=headers, data={"login": login.split(":")[0], "password": login.split(":")[1]})
        if len(r.cookies) == 1:
            wrong_logins+=f"Login: {login.split(':')[0]} 🔑 Password: {login.split(':')[1]}\n"
        else:
            await create_login(login=login.split(":")[0], password=login.split(":")[1],status=True)
            l += 1
    return wrong_logins, l