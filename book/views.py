from datetime import time

from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView

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
from django.template.loader import get_template

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

    def get(self, request, *args, **kwargs):
        print("return the pdf file in drf")
        history = {
            "title": "Jibaro et Sirène",
            "resumeHistory": "Jibaro, un jeune garçon intrépide, rencontre une sirène mystérieuse dans les profondeurs de l'océan. Ensemble, ils vont vivre des aventures incroyables.",
            "chapters": [
                {
                    "title": "La rencontre",
                    "paragraphs": [
                        {
                            "text": "Jibaro était un jeune garçon qui aimait explorer les profondeurs de l'océan. Un jour, il rencontra une sirène mystérieuse qui n'avait jamais vu d'humain auparavant. Elle était belle et gracieuse, avec des cheveux dorés et une queue de poisson scintillante.",
                            "illustration": "https://example.com/illustration1.jpg"
                        },
                        {
                            "text": "Jibaro était émerveillé par la beauté de la sirène et il lui demanda son nom. Elle répondit qu'elle s'appelait Sirena et qu'elle venait d'un royaume sous-marin caché aux yeux des humains.",
                            "illustration": "https://example.com/illustration2.jpg"
                        },
                        {
                            "text": "Sirena était curieuse de découvrir le monde des humains et elle proposa à Jibaro de l'accompagner dans ses aventures. Jibaro accepta avec enthousiasme et ensemble, ils commencèrent leur voyage.",
                            "illustration": "https://example.com/illustration3.jpg"
                        },
                        {
                            "text": "Ils nageaient à travers les récifs de corail et les bancs de poissons colorés, explorant des grottes cachées et découvrant des trésors perdus. Jibaro était fasciné par la beauté de l'océan et Sirena était heureuse de partager ce monde avec lui.",
                            "illustration": "https://example.com/illustration4.jpg"
                        },
                        {
                            "text": "Au fil des jours, Jibaro et Sirena devinrent amis proches. Ils partageaient des histoires et des rires, et Jibaro apprit beaucoup sur la vie sous-marine grâce à Sirena. Mais leur voyage n'était pas sans danger, car il y avait des créatures malveillantes dans les profondeurs de l'océan qui étaient jalouses de leur amitié.",
                            "illustration": "https://example.com/illustration5.jpg"
                        }
                    ],
                    "resume": "Jibaro rencontre Sirena, une sirène mystérieuse, et ils commencent leur voyage ensemble."
                },
                {
                    "title": "Le danger",
                    "paragraphs": [
                        {
                            "text": "Un jour, alors qu'ils nageaient dans une grotte sombre, ils furent attaqués par une pieuvre géante. La pieuvre avait des tentacules puissants et elle était déterminée à capturer Sirena.",
                            "illustration": "https://example.com/illustration6.jpg"
                        },
                        {
                            "text": "Jibaro était terrifié, mais il ne voulait pas abandonner son amie. Il se battit courageusement contre la pieuvre, utilisant toutes les compétences qu'il avait apprises en explorant l'océan. Finalement, il réussit à sauver Sirena et ils s'enfuirent de la grotte.",
                            "illustration": "https://example.com/illustration7.jpg"
                        },
                        {
                            "text": "Cependant, la pieuvre n'était pas la seule créature malveillante dans l'océan. Ils furent également attaqués par des requins affamés et des méduses venimeuses. Mais Jibaro et Sirena travaillaient ensemble, utilisant leur intelligence et leur force pour surmonter chaque obstacle.",
                            "illustration": "https://example.com/illustration8.jpg"
                        },
                        {
                            "text": "Finalement, ils atteignirent le royaume sous-marin de Sirena. C'était un endroit magnifique, rempli de coraux colorés et de créatures étranges. Jibaro était émerveillé par tout ce qu'il voyait.",
                            "illustration": "https://example.com/illustration9.jpg"
                        },
                        {
                            "text": "Mais leur voyage n'était pas encore terminé. Ils avaient encore beaucoup à découvrir et beaucoup d'aventures à vivre ensemble.",
                            "illustration": "https://example.com/illustration10.jpg"
                        }
                    ],
                    "resume": "Jibaro et Sirena doivent faire face à des créatures malveillantes dans les profondeurs de l'océan."
                },
                {
                    "title": "Le royaume sous-marin",
                    "paragraphs": [
                        {
                            "text": "Jibaro était émerveillé par le royaume sous-marin de Sirena. Il y avait des palais en coquillage, des jardins de corail et des fontaines d'eau de mer cristalline. Il y avait aussi des sirènes et des tritons qui nageaient gracieusement dans les rues.",
                            "illustration": "https://example.com/illustration11.jpg"
                        },
                        {
                            "text": "Sirena présenta Jibaro à sa famille et à ses amis. Ils étaient tous curieux de rencontrer un humain et ils posaient beaucoup de questions à Jibaro. Jibaro était heureux de répondre à toutes leurs questions et de partager ses connaissances sur le monde des humains.",
                            "illustration": "https://example.com/illustration12.jpg"
                        },
                        {
                            "text": "Mais bientôt, Jibaro commença à se sentir un peu seul. Il était le seul humain dans un monde de sirènes et de tritons, et il ne pouvait pas s'empêcher de penser à sa famille et à ses amis sur la terre ferme.",
                            "illustration": "https://example.com/illustration13.jpg"
                        },
                        {
                            "text": "Sirena remarqua que Jibaro était triste et elle lui proposa de l'emmener voir quelque chose qui pourrait le rendre heureux. Elle l'emmena dans une grotte secrète où il y avait une source d'eau douce. L'eau était claire et pure, et elle avait un goût délicieux.",
                            "illustration": "https://example.com/illustration14.jpg"
                        },
                        {
                            "text": "Jibaro était ravi de découvrir cette source d'eau douce. Il se sentait comme s'il avait trouvé un petit morceau de chez lui dans ce monde étrange. Il remercia Sirena pour son amitié et pour toutes les aventures qu'ils avaient vécues ensemble.",
                            "illustration": "https://example.com/illustration15.jpg"
                        }
                    ],
                    "resume": "Jibaro découvre le royaume sous-marin de Sirena et rencontre sa famille et ses amis."
                },
                {
                    "title": "Le retour",
                    "paragraphs": [
                        {
                            "text": "Finalement, il était temps pour Jibaro de retourner sur la terre ferme. Il avait appris beaucoup de choses sur l'océan et sur lui-même, mais il avait aussi hâte de retrouver sa famille et ses amis.",
                            "illustration": "https://example.com/illustration16.jpg"
                        },
                        {
                            "text": "Sirena était triste de voir Jibaro partir, mais elle savait qu'ils seraient toujours amis. Elle lui donna un coquillage magique qui lui permettrait de communiquer avec elle à tout moment, où qu'il soit.",
                            "illustration": "https://example.com/illustration17.jpg"
                        },
                        {
                            "text": "Jibaro remercia Sirena pour tout ce qu'elle avait fait pour lui et il promit de revenir la voir un jour. Il n'oublierait jamais les aventures incroyables qu'ils avaient vécues ensemble.",
                            "illustration": "https://example.com/illustration18.jpg"
                        },
                        {
                            "text": "Finalement, Jibaro retourna sur la terre ferme, mais il emporta avec lui des souvenirs incroyables de son voyage avec Sirena. Il savait qu'il avait trouvé un ami pour la vie dans cette sirène mystérieuse.",
                            "illustration": "https://example.com/illustration19.jpg"
                        },
                        {
                            "text": "Et ainsi se termine l'histoire de Jibaro et Sirène, une histoire d'amitié et d'aventure qui ne sera jamais oubliée.",
                            "illustration": "https://example.com/illustration20.jpg"
                        }
                    ],
                    "resume": "Jibaro doit dire au revoir à Sirena et retourner sur la terre ferme."
                }
            ]
        }

        data = history
        print("------->")
        print(data)

        # Define url
        template = get_template('book/wonderbly.html')

        html = template.render(data)

        file_name = 'snakeeyes.pdf'
        pdf_path = "wonderbly.pdf"
        options = {
            'page-size': 'A4',
            'disable-smart-shrinking': '',
            "enable-local-file-access": "",
            'margin-top': '0in',
            'margin-right': '0in',
            'margin-bottom': '0in',
            'margin-left': '0in',
            'encoding': "UTF-8",
        }
        pdfkit.from_string(html, pdf_path, options=options)


        return FileResponse(open(pdf_path, 'rb'), filename=file_name, content_type='application/pdf')



class GenerateImageMidjourney(generics.ListAPIView):
    def get(self, request):
        url = URL + "imagine"
        #input = str(request.data['content']) + " " + "without any text, children’s story book, The little prince cartoon, colorful , fantaisist style, 4k, on a white background"
        input =  "super fascinante without any text, children’s story book, The little prince cartoon, colorful , fantaisist style, 4k, on a white background"
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


class  GetWordToPictureGenerate(APIView):
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
        try:
            texte = request.data.get('texte')
            KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
            HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
            HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                               "authorization": "Bearer " + KEY_LEONARDO}
            payload = {"prompt": texte}
            data = requests.post(HOST_LEONARDO + "generations", json=payload, headers=HEADER_LEONARDO)
            data2 = data.json()
            return Response(data2, status=status.HTTP_200_OK)
        except :
            return Response(status=status.HTTP_404_NOT_FOUND)


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
        try:
            idGenerate = request.data.get('idGenerate')
            KEY_LEONARDO = "64a2692f-9ab7-44c9-b056-acafa9f5be50"
            HOST_LEONARDO = "https://cloud.leonardo.ai/api/rest/v1/"
            HEADER_LEONARDO = {"accept": "application/json", "content-type": "application/json",
                               "authorization": "Bearer " + KEY_LEONARDO}
            data3 = requests.get(HOST_LEONARDO + "generations/"+idGenerate, headers=HEADER_LEONARDO)
            data4 = data3.json()
            return Response(data4, status=status.HTTP_200_OK)
        except :
            return Response(status=status.HTTP_404_NOT_FOUND)

