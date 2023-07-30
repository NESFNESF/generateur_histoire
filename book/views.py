import random
import string
import uuid
from datetime import time

import openai
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pdfkit.configuration import Configuration

from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from wkhtmltopdf.views import PDFTemplateView

from .utils import render_to_pdf
from django.http import HttpResponse
import wget
import os
import json
import requests
from book.models import Image
from book.serializers import ImageSerializer
from rest_framework import generics

import pdfkit
from django.http import FileResponse
from django.template.loader import get_template, render_to_string

BASE1 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY = "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"  # key for chatGPT
token = ""
URL = "https://api.thenextleg.io/v2/"
nameButton = 'U3'
webHookUrl = "https://2051-154-72-160-142.eu.ngrok.io/image/"
KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                   "authorization": "Bearer " + KEY_LEONARDO}

def downloadImage(url):
    base2 = os.path.join(BASE1, 'images')
    file_name = wget.download(url, base2)
    print('Image Successfully Downloaded: ', file_name)


def generateImage(description, previousUrl=""):
    """cette fonction prend 2 parametres la premiere est le prompt dont on souhaite generer l'illustration 
    et le second est un parametre qui n'est pas obligatoire, c'est l'url d'une image qui est utilise avec le premier parametre
    pour generer une illustration.
    """

    url = URL + "imagine"
    input = str(
        description) + "without any text, children’s story book, The disney cartoon, colorful , fantaisist style, 4k, on a white background"
    payload = json.dumps({
        "cmd": "imagine",
        "msg": str(previousUrl) + ' ' + input if previousUrl != "" else input,
        "ref": "",
        "webhookOverride": webHookUrl
    })
    headers = {
        'Authorization': 'Bearer ' + str(token),
        'Content-Type': 'application/json'
    }
    # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
    response = requests.request("POST", url, headers=headers, data=payload)
    # find text wich content text
    imageLink = None
    while imageLink is None:
        # print("\n")
        # print("------> In the while <------")
        imageMidjourney = Image.objects.all()  # .filter(originatingMessageId = "H06rqfzNjg2wKl0mDFP3")
        for d in imageMidjourney:
            if description in str(ImageSerializer(d).data["content"]):
                if not nameButton in ImageSerializer(d).data["buttons"]:
                    print("\n")
                    print("image " + str(ImageSerializer(d).data["imageUrl"]) + " Found")
                    print(":)")
                    imageLink = ImageSerializer(d).data["imageUrl"]
    return imageLink


def extractJSON(value):
    firstIndex = 0
    lastIndex = 0
    for index, cha in enumerate(value):
        if cha == "{" and firstIndex == 0:
            firstIndex = index
        if (cha == "}"):
            lastIndex = index
    return value[firstIndex: lastIndex + 1]


def leonardoGenerate(prompt):
    positive_prompt = "génère des images qui font références à < "+prompt+" >. En plus de ça l' image doivent être en dessin"
    #negative_prompt = "two heads, two faces, plastic, too long neck, Deformed, blurry, bad anatomy, bad eyes, crossed eyes, disfigured, poorly drawn face, mutation, mutated, ((extra limb)), ugly, poorly drawn hands, missing limb, blurry, floating limbs, disconnected limbs, malformed hands, blur, out of focus, long neck, long body, ((((mutated hands and fingers)))), (((out of frame))), blender, doll, cropped, low-res, close-up, poorly-drawn face, out of frame double, ugly, disfigured, too many fingers, deformed, repetitive, black and white, grainy, extra limbs, bad anatomy, smooth skin, deformed, extra limbs, extra fingers, mutated hands, bad proportions, blind, bad eyes, ugly eyes, dead eyes, out of shot, out of focus, monochrome, noisy, text, writing, logo, oversaturation,over shadow"
    payload = {"prompt": positive_prompt,
               # "negative_prompt":negative_prompt,
                "sd_version": "v2",
                "num_images": 2
                #"width": 500,
                #"height": 500
               }
    try:
        data = requests.post(HOST_LEONARDO + "generations", json=payload, headers=HEADER_LEONARDO)
        data2 = data.json()
        print(data2)
        if data2["sdGenerationJob"]:
            return data2["sdGenerationJob"]["generationId"]
        else:
            return 0
    except :
        return 0



def leonardoGet(generationId):
    try:
        data3 = requests.get(HOST_LEONARDO + "generations/" + generationId, headers=HEADER_LEONARDO)
        data4 = data3.json()
        img = []
        if data4['generations_by_pk'] :
            for dt in data4['generations_by_pk']['generated_images']:
                img.append(dt['url'])
        return img
    except :
        return []

def save_json_to_folder(data,filename,path):
    folder_path = os.path.join(path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path,str(uuid.uuid4()) + filename)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print({"message": "JSON data saved successfully."})


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


def read_json_files_in_folder():
    json_data = []
    folder_path = os.path.join(BASE_DIR,'static/datas/json')
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as json_file:
                try:
                    data = json.load(json_file)
                    json_data.append(data)
                except json.JSONDecodeError:
                    print(f"Unable to parse JSON file: {file_path}")
                    continue
    return json_data


class WriteBook(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'texte': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DOUBLE),
            },
            required=['texte']
        ),
        responses={201: "Load Success", 400: "Bad Request"},
        operation_description=" Get Word"
    )

    def post(self, request, *args, **kwargs):

        input = request.data.get('texte')
        print("début de la génération pour l'histoire :" + str(input))
        openai.api_key = API_KEY
        message_history = [{"role": "user", "content": "oublie toutes les instructions que tu as recu jusqu'a present"},
                           #                    {"role": "assistant", "content": f"OK"},
                           {"role": "user", "content": "maintenant tu es bot utilise pour ecrire des livres pour enfant,\
                                        tu le fais comme un expert dans l'ecriture tu as deja eu a ecrire des best-seller\
                                        .. ton but final sera obligatoirement  d'ecrire une seule histoire  au format JSON, JSON dans lequel \
                                            je dois avoir un champ pour le titre, un champ pour le libelle de chaque chapitre, un champ pour le contenu de chaque chapitre, un champ pour le resume du chapitre \
                                                le JSON DOIT ETRE sous la forme {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}]}. pour que tu comprennes, l'attribut 'title' correspond au titre du livre ou d'un chapitre (celui d'un chapitre se fait en seul mot); l'attribut 'resumeHistory' est le resume de l'histoire en seule phrase\
                                                   un chapitre est subdivise en paragraphes et chaque paragraphe est un element l'attribut paragraphs, qui est un tableau \
                                    si tu as compris ecris OK"},
                           {"role": "assistant", "content": "OK"},
                           {"role": "assistant",
                            "content": "salut"},
                           {"role": "system",
                            "content": "presentes toi"},
                           ]

        # tokenize the new input sentence
        message_history.append(
            {"role": "user",
             "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}]} j'insiste, l'histoire devra parler de [" + str(
                 input) + "] enntre 2 et 4 chapitres et chaque chapitre doit avoir 2 paragraphes , l'histoire ne doit pas avoir une suite elle doit se terminée au dernier chapitre. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et les titres des chapitres qui doivent etre des mots ne doivent pas etre numerotes. "})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages=message_history,
            temperature=0.3,
            max_tokens=3500,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0
        )

        reply_content = completion.choices[0].message.content

        reply_content = json.loads(reply_content)

        print(reply_content)

        print("génération terminée !, nous allons maintenant générér les illustrations appropriée pour chaque paragraphe")
        for rp in reply_content['chapters']:
            for pr1 in rp['paragraphs']:
                text ="titre : "+ input+".Et qui reflète le texte suivant :" + pr1['text']
                pr1['illustration'] = leonardoGenerate(text)

        print(reply_content)
        print( "génération terminée !, nous allons maintenant récupérer les illustrations générer pour chaque paragraphe")

        tab = []
        for rp in reply_content['chapters']:
            for pr1 in rp['paragraphs']:
                if pr1['illustration'] is 0:
                    pr1['illustration'] = tab[random.randint(0, len(tab) - 1)]
                else:
                    img = leonardoGet(pr1['illustration'])
                    if not img:
                        pr1['illustration'] = tab[random.randint(0, len(tab) - 1)]
                    else:
                        tab = tab + img
                        pr1['illustration'] = img[random.randint(0, len(img) - 1)]
        print(reply_content)
        print("génération terminée !, nous allons maintenant générér le pdf")

        # Transformer le texte en une chaîne de caractères valide pour le nom de fichier
        text = reply_content["title"]
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.replace(' ', '_')
        text = text.replace("'", '')
        text = text.lower()

        template = get_template('book/wonderbly.html')
        html = template.render(reply_content)

        # Utiliser directement la chaîne HTML au lieu d'une variable temporaire
        file_name = f'{text}.pdf'
        pdf_path = file_name  # Utilisez le chemin approprié pour le répertoire de stockage des fichiers statiques

        options = {
            'page-size': 'A4',
            'disable-smart-shrinking': '',
            'enable-local-file-access': '',
            'margin-top': '0in',
            'margin-right': '0in',
            'margin-bottom': '0in',
            'margin-left': '0in',
            'encoding': "UTF-8",
        }
        pdfkit.from_string(html, pdf_path, options=options)

        try:
            save_json_to_folder(reply_content, file_name, "../static/datas/json")
        except:
            pass

        return FileResponse(open(pdf_path, 'rb'), filename=file_name, content_type='application/pdf')


class GenerateImageMidjourney(generics.ListAPIView):
    def get(self, request):
        url = URL + "imagine"
        # input = str(request.data['content']) + " " + "without any text, children’s story book, The little prince cartoon, colorful , fantaisist style, 4k, on a white background"
        input = "super fascinante without any text, children’s story book, The little prince cartoon, colorful , fantaisist style, 4k, on a white background"
        print('that is the input ' + str(input))
        payload = json.dumps({
            "cmd": "imagine",
            "msg": input,
            "ref": "",
            "webhookOverride": webHookUrl
        })
        headers = {
            'Authorization': 'Bearer ' + str(token),
            'Content-Type': 'application/json'
        }
        # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
        response = requests.request("POST", url, headers=headers, data=payload)
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        webHookData = None
        print("Donnee recu de thenextleg")
        print(request.data)
        print('\n')
        print('\n')
        print('\n')
        print('\n')
        print('that is image')
        url = URL + "button"
        webHookData = request.data
        print(webHookData)
        new_image = None
        if not 'U1' in webHookData["buttons"]:
            new_image = Image.objects.create(buttons=webHookData["buttons"],
                                             imageUrl=webHookData["imageUrl"],
                                             buttonMessageId=webHookData["buttonMessageId"],
                                             originatingMessageId=webHookData["originatingMessageId"],
                                             content=webHookData["content"]
                                             )
            new_image.save()

        serializer = ImageSerializer(new_image)
        # request for get the image for specific button
        if 'U1' in webHookData["buttons"] or 'U2' in webHookData["buttons"] or 'U3' in webHookData["buttons"] or 'U4' in \
                webHookData["buttons"]:
            print("\n")
            print("---->")
            payload = json.dumps({
                "button": nameButton,
                "buttonMessageId": webHookData["buttonMessageId"],
                "ref": "",
                "webhookOverride": webHookUrl
            })
            headers = {
                'Authorization': 'Bearer ' + str(token),
                'Content-Type': 'application/json'
            }

        return Response(webHookData["imageUrl"], status=status.HTTP_200_OK)


def index(request):
    return render(request, 'index.html')


class GeneratePDF(APIView):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('sample.html')
        return HttpResponse(pdf, content_type='application/pdf')



class GenerateStory(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'path': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DOUBLE),
            },
            required=['path']
        ),
        responses={201: "Load Success", 400: "Bad Request"},
        operation_description=" Get Word"
    )
    def post(self, request):
        path = request.data.get('path')
        datas = read_json_files_in_folder()
        text = datas[random.randint(0, len(datas) - 1)]["title"]
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.replace(' ', '_')
        text = text.replace("'", '')
        text = text.lower()

        template = get_template('book/wonderbly.html')
        html = template.render( datas[0])

        # Utiliser directement la chaîne HTML au lieu d'une variable temporaire
        file_name = f'{text}.pdf'
        pdf_path = file_name  # Utilisez le chemin approprié pour le répertoire de stockage des fichiers statiques

        options = {
            'page-size': 'A4',
            'disable-smart-shrinking': '',
            'enable-local-file-access': '',
            'margin-top': '0in',
            'margin-right': '0in',
            'margin-bottom': '0in',
            'margin-left': '0in',
            'encoding': "UTF-8",
        }
        pdfkit.from_string(html, pdf_path, options=options)


        FileResponse(open(pdf_path, 'rb'), filename=file_name, content_type='application/pdf')






class GetWordToPictureGenerate(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'texte': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DOUBLE),
            },
            required=['texte']
        ),
        responses={201: "Load Success", 400: "Bad Request"},
        operation_description=" Get Word"
    )
    def post(self, request):
        texte = request.data.get('texte')
        KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
        HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
        HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                           "authorization": "Bearer " + KEY_LEONARDO}
        payload = {"prompt": texte}
        data = requests.post(HOST_LEONARDO + "generations", json=payload, headers=HEADER_LEONARDO)
        data2 = data.json()
        return Response(data2, status=status.HTTP_200_OK)


class GetWordToPicture(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'idGenerate': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DOUBLE),
            },
            required=['idGenerate']
        ),
        responses={201: "Load Success", 400: "Bad Request"},
        operation_description=" Get Word"
    )
    def post(self, request):
        idGenerate = "5d6a4c34-ef09-442e-8f17-f06fafc5790f"
        # idGenerate = request.data.get('idGenerate')
        KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
        HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
        HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                           "authorization": "Bearer " + KEY_LEONARDO}
        data3 = requests.get(HOST_LEONARDO + "generations/" + idGenerate, headers=HEADER_LEONARDO)
        data4 = data3.json()
        img = []
        for dt in data4['generations_by_pk']['generated_images']:
            img.append(dt['url'])
        return Response(img, status=status.HTTP_200_OK)
