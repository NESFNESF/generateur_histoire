import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

path = "story_model.joblib"




# Exemple d'utilisation
input_sentence = "Il était une fois..."

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


