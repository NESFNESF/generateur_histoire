
import os
import json
import uuid
import re

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

path = "story_model.joblib"

child_friendly_words = [
    "chat", "chien", "oiseau", "soleil", "arc-en-ciel",
    "fleur", "arbre", "voiture", "train", "bateau",
    "ballon", "papillon", "lapin", "ours", "poupée",
    "étoile", "gateau", "bonbons", "jouet", "ballon",
    "jardin", "plage", "forêt", "maison", "école",
    "ami", "rire", "danse", "chante", "aime", "pomme", "banane", "orange", "poire", "fraise",
    "chocolat", "glace", "gâteau", "cookie", "bonbon",
    "abeille", "papillon", "coccinelle", "escargot", "tortue",
    "ours", "chien", "chat", "lapin", "canard",
    "soleil", "lune", "étoile", "nuage", "arc-en-ciel",
    "fleur", "arbre", "jardin", "forêt", "plage",
    "bateau", "voiture", "train", "avion", "vélo",
    "jouet", "poupée", "ours en peluche", "ballon", "toupie",
    "livre", "crayon", "pinceau", "couleurs", "musique",
    "ami", "famille", "rire", "danse", "câlin",
    "douceur", "magie", "merveilleux", "aventure", "rêve",   "dragon", "fée", "licorne", "sirène", "dinosaure",
    "magicien", "princesse", "chevalier", "pirate", "explorateur",
    "château", "trésor", "baguette magique", "épée", "carte au trésor",
    "vaisseau spatial", "extraterrestre", "galaxie", "astronaute", "étoile filante",
    "super-héros", "pouvoir magique", "robot", "monstre", "géant",
    "monde enchanté", "forêt mystérieuse", "océan merveilleux", "île secrète", "volcan magique",
    "livre enchanté", "portail magique", "rêve", "imagination", "merveilleux",
    "aventure fantastique", "conte de fées", "créature magique", "amulette", "sortilège",
    "baguette enchantée", "potion magique", "mystère", "trésor caché", "secret magique",
    "légende", "mythe", "fabuleux", "merveille", "fantaisie",   "baguette magique", "loufoque", "farfelu", "magique", "mystérieux",
    "extraordinaire", "gigantesque", "fabuleux", "merveilleux", "extraordinaire",
    "incroyable", "fantastique", "époustouflant", "émerveillé", "enchanteur",
    "insolite", "imaginatif", "intriguant", "féérique", "prodigieux",
    "surréaliste", "lumineux", "vibrant", "captivant", "ensorcelant",
    "éblouissant", "joyeux", "amusant", "rigolo", "étincelant",
    "éclatant", "coloré", "vif", "gai", "jovial",
    "fantaisiste", "délicieux", "doux", "douillet", "magicien",
    "magnifique", "fascinant", "curieux", "intrépide", "palpitant",
    "inventif", "créatif", "inimaginable", "charmant", "mystique",
    "enchanté", "merveilleusement", "extraordinairement", "drôle", "heureux",  "virevoltant", "farfadet", "cocasse", "énigmatique", "frétillant",
    "ludique", "splendide", "joyeusement", "rayonnant", "féerique",
    "délectable", "sensationnel", "radieux", "étourdissant", "pétillant",
    "magistralement", "fantasmagorique", "incroyablement", "bluffant", "jubilant",
    "craquant", "prodige", "miraculeux", "bouleversant", "fabuleusement",
    "mirifique", "harmonieux", "trépidant", "épique", "ravissant",
    "débordant", "sublime", "étonnant", "souriant", "prodigieux",
    "intriguant", "délirant", "amusant", "exubérant", "malicieux",
    "crépitant", "merveilleusement", "magnifiquement", "éblouissant", "extraordinairement",
    "fantaisiste", "somptueux", "joyeusement", "brillamment", "enchanteur",
    "mystérieusement", "vibrant", "génial", "plaisant", "divertissant", "bouillonnant", "cocooning", "merveilloscope", "charivari", "chatoyant",
    "fantaisie", "émerveillement", "hilarant", "épatant", "faribole",
    "festif", "fripon", "fabulation", "fugace", "fougueux",
    "gargantuesque", "gribouillis", "grincheux", "hibou", "hiberner",
    "huluberlu", "impertinent", "insolite", "intrépide", "jubilatoire",
    "ludique", "loustic", "lézarder", "lunaire", "macaron",
    "marmelade", "nacré", "naïf", "nichoir", "nocturne",
    "obstiné", "ocelot", "orchestrer", "osmose", "palpitant",
    "papillonner", "paradis", "pirouette", "plénitude", "polichinelle",
    "quenotte", "ratatiner", "rizière", "rocambolesque", "rocaille",
    "rugissant", "saperlipopette", "sensation", "siffloter", "sidéral",
    "sourire", "tambouriner", "tintinnabuler", "tournesol", "troubadour", "cocorico", "zinzinuler", "zigzaguer", "brindille", "cacahuète",
    "farfelu", "chiffonner", "cacophonie", "chatouiller", "froufrou",
    "gigoter", "hibou", "joyeux", "gribouillis", "mimosa",
    "papillonner", "hurluberlu", "ruban", "lilliputien", "cabrioler",
    "bambou", "pétiller", "sorbet", "tambouriner", "zèbre",
    "chaton", "cotillon", "frimousse", "croquer", "ronronner",
    "trottiner", "farandole", "hiberner", "zigzaguer", "girafe",
    "croquemitaine", "mascotte", "zigoto", "moustache", "sautiller",
    "fantômette", "guimauve", "chenapan", "guignol", "cacahouète",
    "libellule", "malicieux", "mimique", "loufoque", "rocambolesque",
    "chamailler", "babouche", "zigzag", "palabrer", "froufrouter"

]

class CoreAi :
    def __init__(self):
        if os.path.exists(path):
            self.rf_model = self.load_model()
        else:
            self.rf_model = None

    def train_random_forest(self, story_structure,possible_sentences, num_iterations=5):
        # Charger les données de test (vous devez avoir un ensemble de données de test séparé)
        X_test = np.array([np.random.choice([0, 1], len(possible_sentences)) for _ in range(len(story_structure["chapters"]))])
        y_test = np.array([np.random.choice([0, 1], len(possible_sentences)) for _ in range(len(story_structure["chapters"]))])

        best_accuracy = 0.0

        for i in range(num_iterations):
            # Générer des données d'entraînement aléatoires pour l'exemple
            X_train = np.array([np.random.choice([0, 1], len(possible_sentences)) for _ in range(len(story_structure["chapters"]))])
            y_train = np.array([np.random.choice([0, 1], len(possible_sentences)) for _ in range(len(story_structure["chapters"]))])

            # Entraîner le modèle Random Forest
            rf_model = RandomForestClassifier()
            rf_model.fit(X_train, y_train)

            # Évaluer le modèle sur les données de test
            y_pred = rf_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            # Sauvegarder le meilleur modèle (celui avec la meilleure précision sur les données de test)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                self.rf_model = rf_model

        joblib.dump(self.rf_model, path)

        return best_accuracy


    def save_model(self):
        joblib.dump(self.rf_model, path)



    # Fonction pour générer une histoire à partir d'une phrase d'entrée
    def generate_story(self, rf_model,input_sentence, possible_sentences):
        input_data = np.array([[1 if s in input_sentence else 0 for s in self.possible_sentences]])
        # Utiliser le modèle Random Forest pour prédire les chapitres
        predicted_chapters = rf_model.predict(input_data)
        # Construire l'histoire générée en fonction des prédictions
        generated_story = {
            "title": predicted_chapters["title"],
            "resumeHistory": predicted_chapters["resumeHistory"],
            "chapters": []
        }
        for i, chapter in enumerate(predicted_chapters["chapters"]):
            chapter_title = chapter["title"]
            generated_paragraphs = []
            for j, paragraph in enumerate(chapter["paragraphs"]):
                if predicted_chapters[i][j] == 1:
                    generated_paragraphs.append({"text": possible_sentences[j], "illustration": ""})
            generated_chapter = {
                "title": chapter_title,
                "paragraphs": generated_paragraphs,
                "resume": chapter["resume"]
            }
            generated_story["chapters"]= generated_chapter
        return generated_story



def train_model():
    coreIa = CoreAi()
    story_structure = read_json_files_in_folder('../../static/datas/json')
    possible_sentences = read_json_files_in_folder('../../static/datas')[0]
    accurency = []
    for dt in story_structure:
        accurency.append(coreIa.train_random_forest(dt,possible_sentences,50))

    print(accurency)



def read_json_files_in_folder(path):
    json_data = []
    #folder_path = os.path.join('../../static/datas/json')
    folder_path = os.path.join(path)
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


def save_json_to_folder(data,filename,path):
    folder_path = os.path.join(path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    #file_path = os.path.join(folder_path, str(uuid.uuid4()) +".json")
    file_path = os.path.join(folder_path, filename)
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print({"message": "JSON data saved successfully."})


def remove_articles_and_create_word_array(text, existing_array):
    # Définir une liste d'articles à supprimer
    articles = ["le", "la", "les", "un", "une", "des"]

    # Retirer les articles de la phrase
    words = re.findall(r'\b\w+\b', text)
    filtered_words = [word for word in words if word.lower() not in articles]

    # Supprimer les espaces et mettre les mots en minuscules
    filtered_words = [word.lower().strip() for word in filtered_words]

    # Ajouter les mots restants au tableau existant
    existing_array.extend(filtered_words)

    return existing_array



#save_json_to_folder(child_friendly_words,"list_mot_pour_compte.json","../../static/datas")

train_model()