from django.shortcuts import render

# Create your views here.
from urllib import response
from rest_framework import status, viewsets
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.decorators import api_view

from .utils import render_to_pdf
from django.http import HttpResponse
import openai
import wget
import replicate
import os
import json
from operator import attrgetter, itemgetter
from pathlib import Path
import time
import requests
# from models import Image, History
from book.models import Image, History
from rest_framework.viewsets import ModelViewSet
from book.serializers import ImageSerializer, HistorySerializer
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
    # try:
    #     PROMPT = description +" dans un style fantaisiste tire des livres pour enfant"
    #     openai.api_key = os.getenv("OPENAI_API_KEY")
    #     openai.api_key = API_KEY
    #     nb = 1
    #     response = openai.Image.create(
    #         prompt=PROMPT,
    #         n=nb,
    #         size="1024x1024",
    #     )
    #     return response["data"][0]["url"]
    # except:
    #     return 'https://resize.elle.fr/original/var/plain_site/storage/images/loisirs/cinema/dossiers/dessin-anime-enfant/53838996-1-fre-FR/15-dessins-animes-cultes-a-re-voir-avec-ses-enfants.jpg'
    url = URL + "imagine"
    input = str(
        description) + "without any text, children’s story book, The disney cartoon, colorful , fantaisist style, 4k, on a white background"
    # imageLink = None
    # if previousText != "":
    #     while imageLink is None:
    #         print("\n")
    #         print("------> In the while <------")
    #         imageMidjourney = Image.objects.all()#.filter(originatingMessageId = "H06rqfzNjg2wKl0mDFP3")
    #         for d in imageMidjourney:
    #             if previousText in str(ImageSerializer(d).data["content"]):
    #                 if not nameButton in str(ImageSerializer(d).data["buttons"]):
    #                     imageLink = ImageSerializer(d).data["imageUrl"]
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
    # http_method_names = ['get','head','put','delete']

    # def get(self,request,*args,**kwargs):
    #     images=Image.objects.all()
    #     ImageSerialize=ImageSerializer(images)
    #     print("voici le serializer")
    #     print(ImageSerialize.data)
    #     return Response(ImageSerialize.data)

    def get(self, request, *args, **kwargs):
        # input = request.query_params.get('content')
        # #input = request.data['content']
        # print(f"voici l'input {input}")
        # print(Path(__file__).resolve(
        # ).parent / "key.txt")
        # , "r").read().strip("\n")
        # openai.api_key = API_KEY

        # message_history = [{"role": "user", "content": "oublie toutes les instructions que tu as recu jusqu'a present"},
        #                 #                    {"role": "assistant", "content": f"OK"},
        #                 {"role": "user", "content": "maintenant tu es bot utilise pour ecrire des livres pour enfant,\
        #                         tu le fais comme un expert dans l'ecriture tu as deja eu a ecrire des best-seller\
        #                         .. ton but final sera obligatoirement  d'ecrire une seule histoire  au format JSON, JSON dans lequel \
        #                             je dois avoir un champ pour le titre, un champ pour le libelle de chaque chapitre, un champ pour le contenu de chaque chapitre, un champ pour le resume du chapitre \
        #                                 le JSON DOIT ETRE sous la forme {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]. pour que tu comprennes, l'attribut 'title' correspond au titre du livre ou d'un chapitre (celui d'un chapitre se fait en seul mot); l'attribut 'resumeHistory' est le resume de l'histoire en seule phrase\
        #                                    un chapitre est subdivise en paragraphes et chaque paragraphe est un element l'attribut paragraphs, qui est un tableau \
        #                     si tu as compris ecris OK"},
        #                 {"role": "assistant", "content": "OK"},
        #                 #  {"role": "assistant", "content": "faites une description de votre livre"},
        #                 {"role": "assistant",
        #                     "content": "salut"},
        #                 {"role": "system",
        #                     "content": "presentes toi"},
        #                 ]

        # # tokenize the new input sentence
        # message_history.append(
        #     {"role": "user", "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:..,chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]; j'insiste, l'histoire devra parler de ["+str(input)+"] en minimum 12 chapitres et chaque chapitre doit avoir minimum 5 paragraphes. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et les titres des chapitres qui doivent etre des mots ne doivent pas etre numerotes. "})

        # print("---|>")
        # completion = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
        #     messages=message_history,
        #     temperature=0.3,
        #     max_tokens=3500,
        #     top_p=1,
        #     frequency_penalty=0.2,
        #     presence_penalty=0
        # )
        # #Just the reply:
        # # .replace('```python', '<pre>').replace('```', '</pre>')
        # reply_content = completion.choices[0].message.content
        # i = 0
        # print(reply_content)#.split('\n')[-1])
        # message_history.append(
        #     {"role": "assistant", "content": f"{reply_content}"})
        # try :
        #     history = json.loads(reply_content)
        # except:

        #     history = json.loads(extractJSON(reply_content))
        #     print("exception ici")
        # print("\n")
        # print("\n")
        # print("histoire avant ajout des images")
        # print(history)
        # print("\n")
        # print("\n")
        # print("\n")
        # print("phase d'ajout des images")
        # print("\n")
        # print("\n")
        # # try:
        # #     history["resumeImage"] = generateImage(history["resumeHistory"])
        # #     for index, chapter in enumerate(history["chapter"]):
        # #         print(history["chapter"][index])
        # #         history["chapter"][index]["image"] = generateImage(chapter["resume"], history["resumeImage"])
        # #         history["chapter"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','')
        # #         for ind, paragraph in enumerate(chapter["paragraphs"]):
        # #             print('that is text '+str(history["chapter"][index]["paragraphs"][ind]["text"]))
        # #             if ind == 0:
        # #                 paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["image"])
        # #             else:
        # #                 paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])
        # #             # try:
        # #             #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
        # #             # except : 
        # #             #     print('\n')
        # #             #     print('sleep :(')
        # #             #     print('\n')
        # #             #     time.sleep(63)
        # #             #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])

        # # except : #case which we have chapters instead of chapter
        # #     for index, chapter in enumerate(history["chapters"]):
        # #         print(history["chapters"][index])
        # #         history["chapters"][index]["image"] = generateImage(chapter["resume"], history["resumeHistory"])
        # #         history["chapters"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','') 
        # #         for ind, paragraph in enumerate(chapter["paragraphs"]):

        # #             print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
        # #             if ind == 0:
        # #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["image"])
        # #             else:
        # #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])

        # #             # try:
        # #             #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
        # #             # except : 
        # #             #     print('\n')
        # #             #     print('sleep :(')
        # #             #     print('\n')
        # #             #     time.sleep(63)
        # #             #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])

        # # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
        # responseChat = [(message_history[i]["content"], message_history[i+1]["content"])
        #             for i in range(5, len(message_history)-1, 2)]  # convert to tuples of list  Hayao Miyazaki's cartoon

        # new_history= History.objects.create(content = str(history))
        # new_history.save()

        # print("\n")
        # print("\n")
        # print("histoire apres ajout des images :)")
        # print(history)
        # print("\n")
        # print("\n")
        # print("\n")
        # print(history)

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
        # html = f'''{html}'''

        file_name = 'snakeeyes.pdf'
        pdf_path = "wonderbly.pdf"
        # options1 = {
        #     'page-size': 'A4',
        #     'disable-smart-shrinking': '',
        #     "enable-local-file-access": "",
        #     'margin-top': '0in',
        #     'margin-right': '0in',
        #     'margin-bottom': '0in',
        #     'margin-left': '0in',
        #     'encoding': "UTF-8",
        #     "load-error-handling": "ignore"

        # }
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

        # return Response({"statut": "bonjour snakeEyes"}, status=status.HTTP_200_OK)
        # pdf = pdfkit.from_string(html, False, options=options)

        # response = HttpResponse(pdf)
        # response['Content-Type'] = 'application/pdf'
        # # change attachment to inline if you want open file in browser tab instead downloading
        # response['Content-disposition'] = 'attachment;filename={}.pdf'.format("wonderbly.pdf")
        # return response


# class WriteBook(APIView):
#     #http_method_names = ['get','head','put','delete']

#     # def get(self,request,*args,**kwargs):
#     #     images=Image.objects.all()
#     #     ImageSerialize=ImageSerializer(images)
#     #     print("voici le serializer")
#     #     print(ImageSerialize.data)
#     #     return Response(ImageSerialize.data)

#     def get(self, request, *args, **kwargs) :
#         # input = request.query_params.get('content')
#         # #input = request.data['content']
#         # print(f"voici l'input {input}")
#         # print(Path(__file__).resolve(
#         # ).parent / "key.txt")
#         # , "r").read().strip("\n")
#         # openai.api_key = API_KEY

#         # message_history = [{"role": "user", "content": "oublie toutes les instructions que tu as recu jusqu'a present"},
#         #                 #                    {"role": "assistant", "content": f"OK"},
#         #                 {"role": "user", "content": "maintenant tu es bot utilise pour ecrire des livres pour enfant,\
#         #                         tu le fais comme un expert dans l'ecriture tu as deja eu a ecrire des best-seller\
#         #                         .. ton but final sera obligatoirement  d'ecrire une seule histoire  au format JSON, JSON dans lequel \
#         #                             je dois avoir un champ pour le titre, un champ pour le libelle de chaque chapitre, un champ pour le contenu de chaque chapitre, un champ pour le resume du chapitre \
#         #                                 le JSON DOIT ETRE sous la forme {title:..,resumeHistory:.., chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]. pour que tu comprennes, l'attribut 'title' correspond au titre du livre ou d'un chapitre (celui d'un chapitre se fait en seul mot); l'attribut 'resumeHistory' est le resume de l'histoire en seule phrase\
#         #                                    un chapitre est subdivise en paragraphes et chaque paragraphe est un element l'attribut paragraphs, qui est un tableau \
#         #                     si tu as compris ecris OK"},
#         #                 {"role": "assistant", "content": "OK"},
#         #                 #  {"role": "assistant", "content": "faites une description de votre livre"},
#         #                 {"role": "assistant",
#         #                     "content": "salut"},
#         #                 {"role": "system",
#         #                     "content": "presentes toi"},
#         #                 ]


#         # # tokenize the new input sentence
#         # message_history.append(
#         #     {"role": "user", "content": "ne me pose pas de question ecris juste une seule histoire au format JSON {title:..,resumeHistory:..,chapters:[{title:..,paragraphs: [{text:...,illustration:...}],resume:..}}]; j'insiste, l'histoire devra parler de ["+str(input)+"] en minimum 12 chapitres et chaque chapitre doit avoir minimum 5 paragraphes. Le contenu de chaque paragraphes devra etre une narration detaillee de plus de 1000 mots avec un vocabulaire émotif et dans ta reponse je ne veux voir que l'histoire au format JSON tout respectant les specifications que j'ai donne rien d'autre et les titres des chapitres qui doivent etre des mots ne doivent pas etre numerotes. "})

#         # print("---|>")
#         # completion = openai.ChatCompletion.create(
#         #     model="gpt-3.5-turbo",  # 10x cheaper than davinci, and better. $0.002 per 1k tokens
#         #     messages=message_history,
#         #     temperature=0.3,
#         #     max_tokens=3500,
#         #     top_p=1,
#         #     frequency_penalty=0.2,
#         #     presence_penalty=0
#         # )
#         # #Just the reply:
#         # # .replace('```python', '<pre>').replace('```', '</pre>')
#         # reply_content = completion.choices[0].message.content
#         # i = 0
#         # print(reply_content)#.split('\n')[-1])
#         # message_history.append(
#         #     {"role": "assistant", "content": f"{reply_content}"})
#         # try :
#         #     history = json.loads(reply_content)
#         # except:

#         #     history = json.loads(extractJSON(reply_content))
#         #     print("exception ici")
#         # print("\n")
#         # print("\n")
#         # print("histoire avant ajout des images")
#         # print(history)
#         # print("\n")
#         # print("\n")
#         # print("\n")
#         # print("phase d'ajout des images")
#         # print("\n")
#         # print("\n")
#         # # try:
#         # #     history["resumeImage"] = generateImage(history["resumeHistory"])
#         # #     for index, chapter in enumerate(history["chapter"]):
#         # #         print(history["chapter"][index])
#         # #         history["chapter"][index]["image"] = generateImage(chapter["resume"], history["resumeImage"])
#         # #         history["chapter"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','')
#         # #         for ind, paragraph in enumerate(chapter["paragraphs"]):
#         # #             print('that is text '+str(history["chapter"][index]["paragraphs"][ind]["text"]))
#         # #             if ind == 0:
#         # #                 paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["image"])
#         # #             else:
#         # #                 paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])
#         # #             # try:
#         # #             #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])
#         # #             # except : 
#         # #             #     print('\n')
#         # #             #     print('sleep :(')
#         # #             #     print('\n')
#         # #             #     time.sleep(63)
#         # #             #     paragraph["illustration"] = generateImage(history["chapter"][index]["paragraphs"][ind]["text"])

#         # # except : #case which we have chapters instead of chapter
#         # #     for index, chapter in enumerate(history["chapters"]):
#         # #         print(history["chapters"][index])
#         # #         history["chapters"][index]["image"] = generateImage(chapter["resume"], history["resumeHistory"])
#         # #         history["chapters"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','') 
#         # #         for ind, paragraph in enumerate(chapter["paragraphs"]):

#         # #             print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
#         # #             if ind == 0:
#         # #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["image"])
#         # #             else:
#         # #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["illustration"], chapter["paragraphs"][ind-1]["illustration"])

#         # #             # try:
#         # #             #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])
#         # #             # except : 
#         # #             #     print('\n')
#         # #             #     print('sleep :(')
#         # #             #     print('\n')
#         # #             #     time.sleep(63)
#         # #             #     paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"])

#         # # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
#         # responseChat = [(message_history[i]["content"], message_history[i+1]["content"])
#         #             for i in range(5, len(message_history)-1, 2)]  # convert to tuples of list  Hayao Miyazaki's cartoon

#         # new_history= History.objects.create(content = str(history))
#         # new_history.save()


#         # print("\n")
#         # print("\n")
#         # print("histoire apres ajout des images :)")
#         # print(history)
#         # print("\n")
#         # print("\n")
#         # print("\n")
#         # print(history)

#         print("return the pdf file in drf")
#         history = {
#     "title": "Jibaro et Sirène",
#     "resumeHistory": "Jibaro, un jeune garçon intrépide, rencontre une sirène mystérieuse dans les profondeurs de l'océan. Ensemble, ils vont vivre des aventures incroyables.",
#     "chapters": [
#         {
#             "title": "La rencontre",
#             "paragraphs": [
#                 {
#                     "text": "Jibaro était un jeune garçon qui aimait explorer les profondeurs de l'océan. Un jour, il rencontra une sirène mystérieuse qui n'avait jamais vu d'humain auparavant. Elle était belle et gracieuse, avec des cheveux dorés et une queue de poisson scintillante.",
#                     "illustration": "https://example.com/illustration1.jpg"
#                 },
#                 {
#                     "text": "Jibaro était émerveillé par la beauté de la sirène et il lui demanda son nom. Elle répondit qu'elle s'appelait Sirena et qu'elle venait d'un royaume sous-marin caché aux yeux des humains.",
#                     "illustration": "https://example.com/illustration2.jpg"
#                 },
#                 {
#                     "text": "Sirena était curieuse de découvrir le monde des humains et elle proposa à Jibaro de l'accompagner dans ses aventures. Jibaro accepta avec enthousiasme et ensemble, ils commencèrent leur voyage.",
#                     "illustration": "https://example.com/illustration3.jpg"
#                 },
#                 {
#                     "text": "Ils nageaient à travers les récifs de corail et les bancs de poissons colorés, explorant des grottes cachées et découvrant des trésors perdus. Jibaro était fasciné par la beauté de l'océan et Sirena était heureuse de partager ce monde avec lui.",
#                     "illustration": "https://example.com/illustration4.jpg"
#                 },
#                 {
#                     "text": "Au fil des jours, Jibaro et Sirena devinrent amis proches. Ils partageaient des histoires et des rires, et Jibaro apprit beaucoup sur la vie sous-marine grâce à Sirena. Mais leur voyage n'était pas sans danger, car il y avait des créatures malveillantes dans les profondeurs de l'océan qui étaient jalouses de leur amitié.",
#                     "illustration": "https://example.com/illustration5.jpg"
#                 }
#             ],
#             "resume": "Jibaro rencontre Sirena, une sirène mystérieuse, et ils commencent leur voyage ensemble."
#         },
#         {
#             "title": "Le danger",
#             "paragraphs": [
#                 {
#                     "text": "Un jour, alors qu'ils nageaient dans une grotte sombre, ils furent attaqués par une pieuvre géante. La pieuvre avait des tentacules puissants et elle était déterminée à capturer Sirena.",
#                     "illustration": "https://example.com/illustration6.jpg"
#                 },
#                 {
#                     "text": "Jibaro était terrifié, mais il ne voulait pas abandonner son amie. Il se battit courageusement contre la pieuvre, utilisant toutes les compétences qu'il avait apprises en explorant l'océan. Finalement, il réussit à sauver Sirena et ils s'enfuirent de la grotte.",
#                     "illustration": "https://example.com/illustration7.jpg"
#                 },
#                 {
#                     "text": "Cependant, la pieuvre n'était pas la seule créature malveillante dans l'océan. Ils furent également attaqués par des requins affamés et des méduses venimeuses. Mais Jibaro et Sirena travaillaient ensemble, utilisant leur intelligence et leur force pour surmonter chaque obstacle.",
#                     "illustration": "https://example.com/illustration8.jpg"
#                 },
#                 {
#                     "text": "Finalement, ils atteignirent le royaume sous-marin de Sirena. C'était un endroit magnifique, rempli de coraux colorés et de créatures étranges. Jibaro était émerveillé par tout ce qu'il voyait.",
#                     "illustration": "https://example.com/illustration9.jpg"
#                 },
#                 {
#                     "text": "Mais leur voyage n'était pas encore terminé. Ils avaient encore beaucoup à découvrir et beaucoup d'aventures à vivre ensemble.",
#                     "illustration": "https://example.com/illustration10.jpg"
#                 }
#             ],
#             "resume": "Jibaro et Sirena doivent faire face à des créatures malveillantes dans les profondeurs de l'océan."
#         },
#         {
#             "title": "Le royaume sous-marin",
#             "paragraphs": [
#                 {
#                     "text": "Jibaro était émerveillé par le royaume sous-marin de Sirena. Il y avait des palais en coquillage, des jardins de corail et des fontaines d'eau de mer cristalline. Il y avait aussi des sirènes et des tritons qui nageaient gracieusement dans les rues.",
#                     "illustration": "https://example.com/illustration11.jpg"
#                 },
#                 {
#                     "text": "Sirena présenta Jibaro à sa famille et à ses amis. Ils étaient tous curieux de rencontrer un humain et ils posaient beaucoup de questions à Jibaro. Jibaro était heureux de répondre à toutes leurs questions et de partager ses connaissances sur le monde des humains.",
#                     "illustration": "https://example.com/illustration12.jpg"
#                 },
#                 {
#                     "text": "Mais bientôt, Jibaro commença à se sentir un peu seul. Il était le seul humain dans un monde de sirènes et de tritons, et il ne pouvait pas s'empêcher de penser à sa famille et à ses amis sur la terre ferme.",
#                     "illustration": "https://example.com/illustration13.jpg"
#                 },
#                 {
#                     "text": "Sirena remarqua que Jibaro était triste et elle lui proposa de l'emmener voir quelque chose qui pourrait le rendre heureux. Elle l'emmena dans une grotte secrète où il y avait une source d'eau douce. L'eau était claire et pure, et elle avait un goût délicieux.",
#                     "illustration": "https://example.com/illustration14.jpg"
#                 },
#                 {
#                     "text": "Jibaro était ravi de découvrir cette source d'eau douce. Il se sentait comme s'il avait trouvé un petit morceau de chez lui dans ce monde étrange. Il remercia Sirena pour son amitié et pour toutes les aventures qu'ils avaient vécues ensemble.",
#                     "illustration": "https://example.com/illustration15.jpg"
#                 }
#             ],
#             "resume": "Jibaro découvre le royaume sous-marin de Sirena et rencontre sa famille et ses amis."
#         },
#         {
#             "title": "Le retour",
#             "paragraphs": [
#                 {
#                     "text": "Finalement, il était temps pour Jibaro de retourner sur la terre ferme. Il avait appris beaucoup de choses sur l'océan et sur lui-même, mais il avait aussi hâte de retrouver sa famille et ses amis.",
#                     "illustration": "https://example.com/illustration16.jpg"
#                 },
#                 {
#                     "text": "Sirena était triste de voir Jibaro partir, mais elle savait qu'ils seraient toujours amis. Elle lui donna un coquillage magique qui lui permettrait de communiquer avec elle à tout moment, où qu'il soit.",
#                     "illustration": "https://example.com/illustration17.jpg"
#                 },
#                 {
#                     "text": "Jibaro remercia Sirena pour tout ce qu'elle avait fait pour lui et il promit de revenir la voir un jour. Il n'oublierait jamais les aventures incroyables qu'ils avaient vécues ensemble.",
#                     "illustration": "https://example.com/illustration18.jpg"
#                 },
#                 {
#                     "text": "Finalement, Jibaro retourna sur la terre ferme, mais il emporta avec lui des souvenirs incroyables de son voyage avec Sirena. Il savait qu'il avait trouvé un ami pour la vie dans cette sirène mystérieuse.",
#                     "illustration": "https://example.com/illustration19.jpg"
#                 },
#                 {
#                     "text": "Et ainsi se termine l'histoire de Jibaro et Sirène, une histoire d'amitié et d'aventure qui ne sera jamais oubliée.",
#                     "illustration": "https://example.com/illustration20.jpg"
#                 }
#             ],
#             "resume": "Jibaro doit dire au revoir à Sirena et retourner sur la terre ferme."
#         }
#     ]
# }

#         data = history
#         print("------->")
#         print(data)
#         # pdf = render_to_pdf('app/report.html', data)
#         # print('define response')
#         # reponse = HttpResponse(pdf, content_type = 'application/pdf')
#         # filename = "sample_%s.pdf"%("12345678")
#         # content = "attachment; filename='%s'"%(filename)
#         # reponse['content-Disposition'] = content

#         #Define path to wkhtmltopdf.exe
#         #path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

#         #Define url
#         template = get_template('app/wonderbly.html')

#         html = template.render(data)
#         #html = f'''{html}'''

#         file_name = 'invoice.pdf'
#         pdf_path = "wonderbly.pdf"
#         # options1 = {
#         #     'page-size': 'A4',
#         #     'disable-smart-shrinking': '',
#         #     "enable-local-file-access": "",
#         #     'margin-top': '0in',
#         #     'margin-right': '0in',
#         #     'margin-bottom': '0in',
#         #     'margin-left': '0in',
#         #     'encoding': "UTF-8",
#         #     "load-error-handling": "ignore"

#         # }
#         options = {
#             'page-size': 'A4',
#             'disable-smart-shrinking': '',
#             "enable-local-file-access": "",
#             'margin-top': '0in',
#             'margin-right': '0in',
#             'margin-bottom': '0in',
#             'margin-left': '0in',
#             'encoding': "UTF-8"   
#         }
#         print(html)
#         pdfkit.from_string(html, pdf_path, options=options)
#         return FileResponse(open(pdf_path, 'rb'), filename=file_name, content_type='application/pdf')


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
        # return Response(ImageSerializer(imageMidjourney, many=True).data)

        # history = request.data
        # history["resumeImage"] = generateImage(history["resumeHistory"])
        # for index, chapter in enumerate(history["chapters"]):
        #         print(history["chapters"][index])
        #         history["chapters"][index]["image"] = generateImage(chapter["resume"], history["resumeHistory"])
        #         history["chapters"][index]["title"] = str(history["chapters"][index]["title"]).lower().replace('chapitre ','') 
        #         for ind, paragraph in enumerate(chapter["paragraphs"]):

        #             print('that is text '+str(history["chapters"][index]["paragraphs"][ind]["text"]))
        #             if ind == 0:
        #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"], chapter["image"])
        #             else:
        #                 paragraph["illustration"] = generateImage(history["chapters"][index]["paragraphs"][ind]["text"], chapter["paragraphs"][ind-1]["illustration"])

        # return history

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
            # token : https://hook.eu1.make.com/20r1hloyjc991zcbrgqd5jn4fon4hfxs
            response = requests.request("POST", url, headers=headers, data=payload)
            # new_image= Image.objects.create(buttons = webHookData["buttons"],
            #                                 imageUrl = webHookData["imageUrl"],
            #                                 buttonMessageId = webHookData["buttonMessageId"],
            #                                 originatingMessageId = webHookData["originatingMessageId"],
            #                                 content = webHookData["content"],
            #                                 )

            # new_image.save()
        return Response(webHookData["imageUrl"], status=status.HTTP_200_OK)


def index(request):
    return render(request, 'index.html')


class GeneratePDF(APIView):
    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('sample.html')
        return HttpResponse(pdf, content_type='application/pdf')
