import requests

def add_user(URL, username, password1, password2,cookies):
    client = requests.session()
    client.get(URL)  # sets cookie
    csrftoken = client.cookies['csrftoken']
    post_data = dict(csrfmiddlewaretoken=csrftoken, username=username, password1=password1,
                     password2 =password2, _save = "Save")
    r2 = client.post(URL, data=post_data, headers=dict(Referer=URL), cookies = cookies)
    return r2


def delete_user(user_id, cookies):
    URL_delete = f"http://{lb_url}/admin/auth/user/{user_id}/delete/"
    client = requests.session()
    client.get(URL_delete)  # sets cookie
    csrftoken = client.cookies['csrftoken']
    post_data = dict(csrfmiddlewaretoken=csrftoken,post = "yes")
    r2 = client.post(URL_delete, data=post_data, headers=dict(Referer=URL_delete), cookies = cookies)
    return r2


def add_group(URL, groupname ,cookies):
    client = requests.session()
    client.get(URL)  # sets cookie
    csrftoken = client.cookies['csrftoken']
    post_data = dict(csrfmiddlewaretoken=csrftoken, name=groupname, _save = "Save")
    r2 = client.post(URL, data=post_data, headers=dict(Referer=URL), cookies = cookies)
    return r2


def delete_group(group_id, cookies):
    URL_delete = f"http://{lb_url}/admin/auth/group/{group_id}/delete/"
    client = requests.session()
    client.get(URL_delete)  # sets cookie
    csrftoken = client.cookies['csrftoken']
    post_data = dict(csrfmiddlewaretoken=csrftoken,post = "yes")
    r2 = client.post(URL_delete, data=post_data, headers=dict(Referer=URL_delete), cookies = cookies)
    return r2