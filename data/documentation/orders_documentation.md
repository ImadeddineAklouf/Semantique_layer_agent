# Documentation métier de la table ORDERS

## Présentation générale

La table ORDERS contient les commandes enregistrées dans le système commercial.

Une ligne représente une commande unique.

La table est mise à jour quotidiennement à 03:00.

## Clé primaire

La colonne ORDER_ID constitue la clé primaire métier de la table.

ORDER_ID est un identifiant technique unique, obligatoire et immuable.

## Description des colonnes

### ORDER_ID

- Description : identifiant technique unique de la commande.
- Type métier : identifiant.
- Valeur obligatoire : oui.
- Valeur unique : oui.
- Donnée sensible : non.

### CLIENT_ID

- Description : identifiant du client ayant effectué la commande.
- Type métier : identifiant.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : non.

### ORDER_DATE

- Description : date de création de la commande.
- Type métier : date.
- Format attendu : YYYY-MM-DD.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : non.

### AMOUNT

- Description : montant total de la commande.
- Type métier : nombre décimal.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Donnée sensible : non.

### STATUS

- Description : statut actuel de la commande.
- Type métier : texte.
- Valeur obligatoire : oui.
- Valeur unique : non.
- Valeurs autorisées : PROCESSING, COMPLETED, CANCELLED.
- Donnée sensible : non.

## Règles métier

1. ORDER_ID doit toujours être renseigné.
2. ORDER_ID doit être unique.
3. CLIENT_ID doit toujours être renseigné.
4. CLIENT_ID doit correspondre à un client existant dans la table CLIENTS.
5. ORDER_DATE ne doit pas être située dans le futur.
6. AMOUNT doit être supérieur ou égal à zéro.
7. STATUS doit contenir PROCESSING, COMPLETED ou CANCELLED.
8. Une commande appartient à un seul client.
9. Un client peut posséder plusieurs commandes.

## Relations connues

La table ORDERS est reliée à la table CLIENTS avec la relation :

- ORDERS.CLIENT_ID = CLIENTS.CLIENT_ID
- Cardinalité : plusieurs commandes peuvent appartenir à un client.
- Type de relation : many-to-one.

Du point de vue de la table CLIENTS, cette relation est de type one-to-many.

## Points de vigilance

CLIENT_ID doit toujours correspondre à un client existant.

Une commande dont CLIENT_ID n'existe pas dans CLIENTS est considérée
comme une commande orpheline.

## Informations manquantes

La documentation ne précise pas :

- la devise associée à AMOUNT ;
- la politique de suppression des commandes ;
- la durée de conservation des commandes ;
- le propriétaire métier de la table.