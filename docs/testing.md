# Stratégie de tests

## Objectif

La suite de tests vérifie que le pipeline peut fonctionner sans dépendre d’un modèle de langage.

## Exécuter tous les tests

```powershell
python -m pytest -v
```

## Catégories couvertes

### Schémas

Les tests contrôlent :

- les valeurs autorisées ;
- les bornes numériques ;
- les champs obligatoires ;
- les champs inconnus ;
- les conversions des dictionnaires imbriqués ;
- les validateurs de cohérence.

### Tools

Chaque outil est testé avec :

- des données valides ;
- des fichiers absents ;
- des formats invalides ;
- des fichiers vides ;
- des incohérences ;
- des relations invalides.

### Agents

Les tests vérifient :

- le nom ;
- le modèle ;
- la description ;
- le mode `task` ;
- l’outil métier ;
- le `FinishTaskTool` ;
- l’absence de sous-agents pour les spécialistes.

### Supervisor

Les tests vérifient :

- la liste des six spécialistes ;
- l’unicité des agents ;
- la relation parent-enfant ;
- la présence des instructions.

### Génération LookML

Les tests vérifient :

- les dimensions ;
- les clés primaires ;
- les mesures ;
- les jointures ;
- les Explores ;
- le fichier modèle ;
- l’absence de mesures sur les identifiants.

### Sécurité du writer

Les tests vérifient :

- les extensions autorisées ;
- les traversées de répertoire ;
- les chemins absolus ;
- les noms dupliqués ;
- l’écrasement refusé ;
- l’écrasement explicite ;
- l’écriture UTF-8.

### Tests end-to-end

Les tests end-to-end exécutent :

```text
sources
→ modèle sémantique
→ rendu LookML
→ validation
→ écriture
→ vérification du contenu
```

### API

Les tests API couvrent :

- la santé du service ;
- OpenAPI ;
- les analyses individuelles ;
- la prévisualisation ;
- la génération ;
- les codes HTTP ;
- les erreurs Pydantic ;
- la sécurité des chemins ;
- les identifiants de requête.

## Tests ADK Web

Les tests ADK Web nécessitent un quota Gemini.

Ils complètent les tests déterministes en vérifiant :

- le routage conversationnel ;
- les demandes de clarification ;
- la présentation des résultats ;
- l’absence de réutilisation involontaire du contexte.

Un indisponibilité temporaire du quota Gemini ne bloque pas les tests du pipeline déterministe.