import requests
from RequestFunctions import add_user, delete_user, add_group, delete_group


f = open("URLS.txt", "r")
lb_url = f.read()
URL = f'http://{lb_url}/admin/login/?next=/admin/'
URL_add_user = f"http://{lb_url}/admin/auth/user/add/"
URL_add_group = f"http://{lb_url}/admin/auth/group/add/"

client = requests.session()
client.get(URL) 
csrftoken = client.cookies['csrftoken']
login_data = dict(username='cloud', password='cloud', csrfmiddlewaretoken=csrftoken, next='/admin/')
r = client.post(URL, data=login_data, headers=dict(Referer=URL))
cookies = dict(sessionid=client.cookies.get('sessionid'))


print(URL)
print(cookies)

input_options = [1,2,3,4]




finish = False


while not finish:
    print("Choose an option: 1 - Add user, 2- Delete user, 3- Add Group, 4- Delete group")
    option = int(input())

    while option not in input_options:
        print("Please choose a valid option")
        option = int(input())

    if option == 1:
        print("Choose a username:")
        username = str(input())
        print("Choose a password:")
        password = str(input())
        add_user(URL_add_user, username, password, password, cookies)
        print(f"User {username} created")

    elif option == 2:
        print("Choose the id of the user you want to delete:")
        user_id = int(input())
        delete_user(user_id, cookies)
        print(f"User deleted")

    elif option == 3:
        print("Choose a groupname:")
        groupname = str(input())
        add_group(URL_add_group, groupname ,cookies)
        print(f"Group {groupname} created")

    elif option == 4:
        print("Choose the id of the group you want to delete:")
        group_id = int(input())
        delete_group(group_id, cookies)
        print(f"Group deleted")
    
    print("Do you want to continue? y/n")
    finish_input = input()
    if finish_input == 'n':
        finish = True

print("Done")


