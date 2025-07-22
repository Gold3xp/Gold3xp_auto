from instagrapi import Client

def login_instagram(username, password):
    cl = Client()
    cl.login(username, password)
    return cl
