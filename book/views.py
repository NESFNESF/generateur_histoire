import random
import string
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
        # input = request.data['content']
        print(f"voici l'input {input}")
        openai.api_key = API_KEY
        KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
        HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
        HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                           "authorization": "Bearer " + KEY_LEONARDO}
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
                           #  {"role": "assistant", "content": "faites une description de votre livre"},
                           {"role": "assistant",
                            "content": "salut"},
                           {"role": "system",
                            "content": "presentes toi"},
                           ]

        # tokenize the new input sentence
        message_history.append(
            {"role": "user",
             "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}]} j'insiste, l'histoire devra parler de [" + str(
                 input) + "] en 5 chapitres et chaque chapitre doit avoir minimum 5 paragraphes , l'histoire ne doit pas avoir une suite elle doit se terminée au dernier chapitre. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et les titres des chapitres qui doivent etre des mots ne doivent pas etre numerotes. "})

        print("---|>")
        payload = {"prompt": input}
        data = requests.post(HOST_LEONARDO + "generations", json=payload, headers=HEADER_LEONARDO)
        data2 = data.json()
        print(data2)
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
            messages=message_history,
            temperature=0.3,
            max_tokens=3500,
            top_p=1,
            frequency_penalty=0.2,
            presence_penalty=0
        )
        # Just the reply:
        # .replace('```python', '<pre>').replace('```', '</pre>')
        reply_content = completion.choices[0].message.content
        # i = 0
        reply_content = json.loads(reply_content)
        print(reply_content)  # .split('\n')[-1])
        # message_history.append(
        #     {"role": "assistant", "content": f"{reply_content}"})
        idGenerate = data2["sdGenerationJob"]["generationId"]
        # idGenerate = request.data.get('idGenerate')

        data3 = requests.get(HOST_LEONARDO + "generations/" + idGenerate, headers=HEADER_LEONARDO)
        data4 = data3.json()
        img = []
        for dt in data4['generations_by_pk']['generated_images']:
            img.append(dt['url'])

        for rp in reply_content['chapters']:
            for pr1 in rp['paragraphs']:
                pr1['illustration'] = img[random.randint(0, len(img) - 1)]

        print(reply_content)
        # Transformer le texte en une chaîne de caractères valide pour le nom de fichier
        text = reply_content["title"]
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.replace(' ', '_')
        text = text.replace("'", '')
        text = text.lower()

        template = get_template('book/wonderbly.html')

        html = template.render(reply_content)

        # Utiliser la configuration personnalisée lors de la génération du PDF


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

        # Retourner la réponse avec le fichier PDF
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
