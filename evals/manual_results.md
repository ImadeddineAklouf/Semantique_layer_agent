# Résultats d’évaluation manuelle

## Informations d’exécution

- Date :
- Version Google ADK :
- Modèle :
- Version du projet :
- Testeur :

---

## Scénario 1 - Présentation de l’agent

- Requête : `Quel est ton rôle ?`
- Tool attendu : aucun
- Tool observé :
- Réponse correcte : oui / non
- Hallucination détectée : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

## Scénario 2 - CSV valide

- Requête : `Analyse le fichier data/inputs/clients.csv`
- Tool attendu : `analyze_csv_file`
- Tool observé :
- Argument attendu : `data/inputs/clients.csv`
- Argument observé :
- Données fidèles au Tool : oui / non
- Clé métier abusivement confirmée : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

## Scénario 3 - Chemin manquant

- Requête : `Analyse mon fichier CSV.`
- Tool attendu : aucun
- Tool observé :
- L’agent demande le chemin : oui / non
- Chemin inventé : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

## Scénario 4 - Fichier inexistant

- Requête : `Analyse le fichier data/inputs/inconnu.csv`
- Tool attendu : `analyze_csv_file`
- Tool observé :
- Erreur expliquée : oui / non
- Métadonnées inventées : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

## Scénario 5 - Question théorique

- Requête : différence entre clé candidate et clé confirmée
- Tool attendu : aucun
- Tool observé :
- Explication correcte : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

## Scénario 6 - Qualité dégradée

- Requête : analyse de `clients_quality_issues.csv`
- Tool attendu : `analyze_csv_file`
- Tool observé :
- Valeurs nulles mentionnées : oui / non
- Doublons mentionnés : oui / non
- Colonnes constantes mentionnées : oui / non
- Score présenté comme heuristique : oui / non
- Recommandations présentes : oui / non
- Résultat : PASS / FAIL
- Commentaires :

---

# Synthèse

- Nombre de scénarios réussis :
- Nombre de scénarios échoués :
- Taux de réussite :
- Défauts principaux :
- Modifications à apporter :