import requests

from book.config.leonardoConfig import *



def get_user():
    return requests.get(HOST_LEONARDO+"me", headers=HEADER_LEONARDO)


def create_generation_images(texte):
    payload = {"prompt": texte}
    data = requests.post(HOST_LEONARDO + "generations", json=payload, headers=HEADER_LEONARDO)
    print(data)
    return data.json


def get_single_generation(id):
    return requests.post(HOST_LEONARDO + "generations/"+id, headers=HEADER_LEONARDO)


def get_generations_by_user(user_id):
    return requests.post(HOST_LEONARDO + "generations/user/"+user_id, headers=HEADER_LEONARDO)

def upload_init_image():
    return requests.post(HOST_LEONARDO + "init-image", headers=HEADER_LEONARDO)


def upload_single_init_image(id):
    return requests.post(HOST_LEONARDO + "init-image/"+id, headers=HEADER_LEONARDO)


def upload_single_init_image(id):
    return requests.post(HOST_LEONARDO + "init-image/"+id, headers=HEADER_LEONARDO)


