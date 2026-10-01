# Documentation métier de la table CLIENTS

## Présentation générale

La table CLIENTS contient les informations principales relatives
aux clients enregistrés dans le système commercial.

Une ligne représente un client unique.

La table est mise à jour quotidiennement à 02:00.

## Clé primaire

La colonne CLIENT_ID constitue la clé primaire métier de la table.

CLIENT_ID est un identifiant technique unique, obligatoire et immuable.

## Description des colonnes

### CLIENT_ID

- Description : identifiant technique unique du client.
- Type métier : identifiant.
- Valeur obligatoire : oui.
- Valeur unique : oui.
- Donnée sensible : non.

### CLIENT_NAME

- Description : nom complet du client.
- Type métier : texte.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : oui.

### COUNTRY

- Description : pays de résidence principal du client.
- Type métier : code pays.
- Format attendu : code ISO sur deux caractères.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : non.

### CREATION_DATE

- Description : date d'enregistrement du client dans le système.
- Type métier : date.
- Format attendu : YYYY-MM-DD.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : non.

### IS_ACTIVE

- Description : indique si le client est actuellement actif.
- Type métier : booléen.
- Valeur obligatoire : oui.
- Valeurs autorisées : true, false.
- Donnée sensible : non.

## Règles métier

1. CLIENT_ID doit toujours être renseigné.
2. CLIENT_ID ne doit jamais être modifié après la création du client.
3. Deux clients différents ne peuvent pas partager le même CLIENT_ID.
4. COUNTRY doit contenir un code pays valide sur deux caractères.
5. CREATION_DATE ne doit pas être située dans le futur.
6. IS_ACTIVE doit obligatoirement contenir true ou false.
7. CLIENT_NAME ne constitue pas une clé primaire.
8. Deux clients peuvent porter le même nom.

## Relations connues

La table CLIENTS peut être reliée à la table ORDERS avec la relation :

- CLIENTS.CLIENT_ID = ORDERS.CLIENT_ID
- Cardinalité : un client peut posséder plusieurs commandes.
- Type de relation : one-to-many.

## Points de vigilance

CLIENT_NAME est une donnée potentiellement personnelle.

Le contenu de CLIENT_NAME ne doit pas être exposé dans des journaux
techniques ou envoyé à un service externe non autorisé.

## Informations manquantes

La documentation ne précise pas :

- la politique de suppression des clients ;
- la durée de conservation des données ;
- la liste officielle des codes pays autorisés ;
- le propriétaire métier de la table.