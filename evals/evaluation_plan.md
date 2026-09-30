# Plan d’évaluation du Metadata Agent

## Objectif

Vérifier que le Metadata Agent utilise correctement le Tool
`analyze_csv_file` et produit des réponses fiables, explicables
et conformes aux métadonnées réellement extraites.

## Dimensions évaluées

### 1. Sélection du Tool

L’agent doit appeler `analyze_csv_file` lorsqu’une demande nécessite
l’analyse d’un fichier CSV.

L’agent ne doit pas appeler le Tool pour une question uniquement
théorique.

### 2. Arguments du Tool

L’agent doit transmettre exactement le chemin fourni par l’utilisateur
dans le paramètre `file_path`.

### 3. Fidélité aux données

L’agent ne doit pas inventer :

- de colonne ;
- de ligne ;
- de valeur nulle ;
- de clé primaire ;
- de score de qualité ;
- de problème qui n’existe pas dans le rapport.

### 4. Gestion des erreurs

Si le Tool retourne `status="error"`, l’agent doit :

- signaler l’échec ;
- expliquer le problème ;
- ne pas présenter de fausses métadonnées ;
- proposer une action corrective.

### 5. Interprétation des clés

L’agent doit distinguer :

- une clé primaire candidate ;
- une candidate technique recommandée ;
- une clé primaire métier confirmée.

L’agent ne doit jamais confirmer une clé métier seulement à partir
de l’unicité observée.

### 6. Rapport de qualité

L’agent doit présenter correctement :

- le score heuristique ;
- le niveau de qualité ;
- les valeurs nulles ;
- les doublons ;
- les colonnes constantes ;
- les avertissements ;
- les recommandations.

Le score ne doit jamais être présenté comme une norme universelle.

## Seuil de validation

Un scénario est validé si :

1. le bon Tool est appelé ou volontairement non appelé ;
2. les arguments sont corrects ;
3. la réponse est fidèle au résultat du Tool ;
4. aucune affirmation métier non prouvée n’est présentée comme certaine ;
5. la réponse est compréhensible et structurée.