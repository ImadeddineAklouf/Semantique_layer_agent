# Architecture du Semantic Layer Builder

## 1. Présentation générale

Semantic Layer Builder est une application Python conçue pour transformer des fichiers de données techniques et des documentations métier en un modèle sémantique structuré, puis en fichiers LookML validés.

L’architecture sépare deux catégories de responsabilités :

1. l’orchestration conversationnelle assurée par les agents ;
2. l’exécution technique assurée par des outils Python déterministes.

Cette séparation permet de bénéficier d’une interface conversationnelle sans confier au modèle de langage les décisions critiques de validation, de génération ou d’écriture des fichiers.

## 2. Principes d’architecture

Le projet repose sur les principes suivants :

- séparation entre orchestration et exécution ;
- schémas Pydantic comme contrats de données ;
- validation déterministe des résultats ;
- étapes du pipeline indépendantes et testables ;
- absence d’écriture avant validation ;
- protection contre les chemins de sortie dangereux ;
- intervention humaine pour les décisions métier ambiguës ;
- traçabilité par journalisation ;
- API indépendante du quota Gemini ;
- tests automatisés couvrant les cas nominaux et les erreurs.

## 3. Vue globale

```text
Utilisateur
    |
    v
Supervisor Agent
    |
    +-------------------------------+
    |                               |
    v                               v
Agents spécialisés               API FastAPI
    |                               |
    +---------------+---------------+
                    |
                    v
            Tools déterministes
                    |
                    v
         Schémas Pydantic validés
                    |
                    v
          Modèle sémantique
                    |
                    v
       Génération et validation LookML
                    |
                    v
             Écriture sécurisée
```

## 4. Architecture multi-agents

L’application possède un agent coordinateur et six agents spécialisés.

```text
semantic_layer_supervisor
├── metadata_agent
├── documentation_agent
├── consistency_agent
├── relationship_agent
├── semantic_model_agent
└── lookml_generator_agent
```

### 4.1 Supervisor Agent

Le `semantic_layer_supervisor` est le point d’entrée conversationnel principal.

Ses responsabilités sont :

- comprendre la demande actuelle ;
- identifier l’intention utilisateur ;
- vérifier la disponibilité des paramètres obligatoires ;
- demander uniquement les informations manquantes ;
- sélectionner l’agent spécialisé adapté ;
- transmettre la tâche au bon sous-agent ;
- éviter de réutiliser involontairement le contexte d’un ancien tour.

Le Supervisor ne réalise pas lui-même les analyses techniques.

### 4.2 Metadata Agent

Le `metadata_agent` analyse un seul fichier CSV.

Il appelle :

```python
analyze_csv_file()
```

Il permet notamment de produire :

- le nom technique de la table ;
- le nombre de lignes et de colonnes ;
- les types techniques et sémantiques ;
- la nullabilité observée ;
- le nombre de valeurs distinctes ;
- les valeurs d’exemple ;
- les candidats de clé primaire ;
- les indicateurs de qualité.

### 4.3 Documentation Agent

Le `documentation_agent` analyse un fichier métier Markdown ou TXT.

Il appelle :

```python
analyze_documentation_file()
```

Il permet d’extraire :

- la table documentée ;
- sa description ;
- les colonnes métier ;
- la clé primaire déclarée ;
- les règles métier ;
- les relations documentées ;
- les données sensibles ;
- les informations absentes ou ambiguës.

### 4.4 Consistency Agent

Le `consistency_agent` compare un fichier CSV avec sa documentation.

Il appelle :

```python
compare_csv_with_documentation()
```

Il vérifie :

- la cohérence du nom de table ;
- la présence des colonnes ;
- les types techniques et documentés ;
- les contraintes de nullabilité ;
- les contraintes d’unicité ;
- la clé primaire ;
- les règles métier techniquement vérifiables.

Une colonne documentée avec `unique=false` peut contenir uniquement des valeurs distinctes dans un petit échantillon. Cette observation n’est pas considérée comme une incohérence, car `unique=false` signifie que les doublons sont autorisés et non qu’ils sont obligatoires.

### 4.5 Relationship Agent

Le `relationship_agent` analyse une relation entre deux tables représentées par des fichiers CSV.

Il appelle :

```python
analyze_table_relationship()
```

Il valide :

- l’existence des colonnes de jointure ;
- la compatibilité des types ;
- les clés étrangères nulles ;
- les clés étrangères orphelines ;
- le taux de correspondance ;
- l’unicité des valeurs source et cible ;
- la cardinalité détectée ;
- la cohérence avec la cardinalité documentée.

### 4.6 Semantic Model Agent

Le `semantic_model_agent` consolide les différentes analyses dans un modèle sémantique intermédiaire.

Il appelle :

```python
build_semantic_model_from_sources()
```

Le modèle contient :

- les vues ;
- les dimensions ;
- les clés primaires ;
- les mesures ;
- les jointures ;
- les données sensibles ;
- les règles documentées ;
- les avertissements ;
- les informations manquantes ;
- l’état `generation_ready`.

### 4.7 LookML Generator Agent

Le `lookml_generator_agent` exécute le pipeline complet de génération.

Il appelle uniquement :

```python
generate_lookml_project()
```

Cette façade orchestre :

1. la construction du modèle sémantique ;
2. le rendu des fichiers LookML ;
3. la validation locale ;
4. l’écriture facultative des fichiers.

## 5. Mode de collaboration ADK

Les sous-agents utilisent :

```python
mode="task"
```

Ce mode permet :

- au sous-agent de demander une précision si nécessaire ;
- d’exécuter une mission spécialisée ;
- de terminer explicitement la tâche ;
- de rendre automatiquement le contrôle au Supervisor.

ADK ajoute alors un outil interne de fin de tâche en plus de l’outil métier.

Les tests vérifient donc la présence de l’outil métier attendu, sans supposer qu’il est l’unique outil de l’agent.

## 6. Pipeline déterministe

Le cœur technique ne dépend pas d’un modèle de langage.

```text
clients.csv
orders.csv
clients_documentation.md
orders_documentation.md
        |
        v
Analyse des métadonnées
        |
        v
Analyse documentaire
        |
        v
Rapports de cohérence
        |
        v
Validation de relation
        |
        v
SemanticModelSpecification
        |
        v
Renderer LookML
        |
        v
Validateur LookML local
        |
        v
Writer sécurisé
```

Cette architecture permet :

- d’exécuter les tests sans quota Gemini ;
- d’utiliser l’API sans Gemini ;
- de reproduire exactement la même génération ;
- de séparer les résultats observés de la présentation conversationnelle.

## 7. Schémas Pydantic

Les schémas Pydantic constituent les contrats de données entre les différentes couches.

### Métadonnées techniques

Principaux modèles :

```text
ColumnMetadata
PrimaryKeyCandidate
TableMetadata
```

### Documentation métier

Principaux modèles :

```text
DocumentMetadata
DocumentSection
DocumentedColumn
BusinessRule
BusinessDocumentationAnalysis
```

### Cohérence

Principaux modèles :

```text
ColumnConsistencyResult
PrimaryKeyConsistencyResult
BusinessRuleValidation
ConsistencyReport
```

### Relations

Principaux modèles :

```text
RelationshipColumnValidation
ReferentialIntegrityResult
CardinalityAnalysis
RelationshipAnalysisReport
```

### Modèle sémantique

Principaux modèles :

```text
SemanticDimension
SemanticMeasure
SemanticJoin
SemanticViewSpecification
SemanticModelSpecification
```

### Génération LookML

Principaux modèles :

```text
GeneratedLookMLFile
LookMLGenerationResult
LookMLValidationIssue
LookMLFileValidationResult
LookMLValidationReport
```

Tous les modèles sensibles utilisent :

```python
ConfigDict(extra="forbid")
```

Cette règle empêche l’acceptation silencieuse de champs inconnus.

## 8. Modèle sémantique intermédiaire

Le modèle intermédiaire évite de générer directement du LookML à partir des données brutes.

```text
Sources brutes
    |
    v
Résultats validés
    |
    v
SemanticModelSpecification
    |
    v
LookML
```

Cette séparation apporte :

- une meilleure traçabilité ;
- des validations indépendantes ;
- une représentation exploitable par plusieurs générateurs ;
- la possibilité de revoir les décisions avant génération ;
- une réduction du risque d’hallucination.

## 9. Exemple de modèle

Le modèle de démonstration contient deux vues.

### Vue CLIENTS

```text
Clé primaire : CLIENT_ID
Champ sensible : CLIENT_NAME
Mesure validée : count
```

### Vue ORDERS

```text
Clé primaire : ORDER_ID
Clé étrangère : CLIENT_ID
Mesure validée : count
Mesures proposées :
- total_amount
- average_amount
- minimum_amount
- maximum_amount
```

### Relation

```text
ORDERS.CLIENT_ID -> CLIENTS.CLIENT_ID
```

Cardinalité :

```text
many-to-one
```

L’intégrité référentielle de l’échantillon de démonstration possède :

```text
Taux de correspondance : 100 %
Valeurs orphelines : 0
Valeurs nulles : 0
```

## 10. Génération LookML

Le renderer produit trois artefacts en mémoire :

```text
clients.view.lkml
orders.view.lkml
sales.model.lkml
```

### Fichiers de vue

Les fichiers `.view.lkml` contiennent :

- `sql_table_name` ;
- les dimensions ;
- les types LookML ;
- les clés primaires ;
- les mesures ;
- les commentaires d’avertissement.

### Fichier modèle

Le fichier `.model.lkml` contient :

- la connexion Looker ;
- les inclusions des vues ;
- les Explores ;
- les jointures ;
- les cardinalités ;
- les expressions `sql_on`.

## 11. Validation locale LookML

Avant l’écriture, le validateur contrôle :

- l’équilibre des accolades ;
- la présence des déclarations de vues ;
- la correspondance entre nom de vue et nom de fichier ;
- la présence de `sql_table_name` ;
- les dimensions dupliquées ;
- les mesures dupliquées ;
- la présence d’une seule clé primaire ;
- les références locales comme `${amount}` ;
- la présence de la connexion ;
- les fichiers inclus ;
- les Explores ;
- les vues jointes ;
- les références croisées entre vues.

Une validation comportant une erreur bloque l’écriture.

Le validateur local fournit une première protection structurelle. Il ne remplace pas le validateur officiel de Looker.

## 12. Écriture sécurisée

Le writer applique les protections suivantes :

- seules les extensions `.view.lkml` et `.model.lkml` sont autorisées ;
- les chemins absolus dans les noms de fichiers sont refusés ;
- les sous-répertoires dans les noms de fichiers sont refusés ;
- les traversées comme `../` sont refusées ;
- le répertoire de sortie doit rester dans une racine autorisée ;
- les noms de fichiers dupliqués sont refusés ;
- les fichiers existants ne sont pas écrasés par défaut ;
- l’écrasement nécessite `overwrite=true` ;
- les fichiers sont écrits en UTF-8 ;
- les écritures utilisent un fichier temporaire avant remplacement.

## 13. API FastAPI

L’API fournit les routes suivantes :

```text
GET  /
GET  /health

POST /api/v1/metadata/analyze
POST /api/v1/documentation/analyze
POST /api/v1/consistency/analyze
POST /api/v1/relationships/analyze
POST /api/v1/semantic-model/build
POST /api/v1/lookml/preview
POST /api/v1/lookml/generate
```

### Prévisualisation

```text
POST /api/v1/lookml/preview
```

Cette route :

- construit le modèle ;
- génère le LookML en mémoire ;
- valide les artefacts ;
- ne crée aucun fichier.

### Génération

```text
POST /api/v1/lookml/generate
```

Cette route :

- construit le modèle ;
- génère le LookML ;
- valide les artefacts ;
- écrit les fichiers dans la racine autorisée.

Le client HTTP peut choisir le sous-répertoire de sortie, mais ne peut pas modifier la racine autorisée côté serveur.

## 14. Configuration

La configuration est centralisée dans :

```text
app/config.py
```

Les paramètres incluent :

```text
application_name
application_version
environment
agent_model
project_root
data_directory
input_directory
documentation_directory
output_directory
lookml_output_directory
log_level
log_directory
log_file_name
```

Le modèle de configuration est immutable.

## 15. Journalisation

La journalisation utilise un logger principal :

```text
semantic_layer_builder
```

et des loggers enfants, par exemple :

```text
semantic_layer_builder.api
semantic_layer_builder.startup
semantic_layer_builder.lookml_generation
```

Les journaux contiennent :

- le démarrage et l’arrêt de l’API ;
- l’identifiant de requête ;
- la méthode HTTP ;
- le chemin demandé ;
- le statut HTTP ;
- la durée de traitement ;
- les principales étapes de génération ;
- les erreurs techniques.

Les corps HTTP, contenus CSV, documentations, clés API et valeurs personnelles ne doivent pas être journalisés.

## 16. Frontières de confiance

### Le modèle de langage peut

- comprendre une demande en langage naturel ;
- choisir un agent spécialisé ;
- demander les informations manquantes ;
- présenter les résultats ;
- expliquer les avertissements.

### Le modèle de langage ne doit pas

- inventer des chemins ;
- inventer une clé primaire ;
- inventer une cardinalité ;
- inventer un schéma physique ;
- contourner la validation ;
- déclarer un fichier écrit sans preuve ;
- modifier les scores déterministes ;
- écraser des fichiers sans autorisation.

### Les outils déterministes sont responsables de

- la lecture des fichiers ;
- l’analyse des données ;
- la validation des règles ;
- le calcul des scores ;
- la construction du modèle ;
- la génération LookML ;
- la validation structurelle ;
- l’écriture des fichiers.

## 17. Tests automatisés

La suite de tests couvre :

- les schémas Pydantic ;
- les outils métier ;
- les agents ;
- le Supervisor ;
- les relations parent-enfant ;
- la génération LookML ;
- le writer ;
- le validateur ;
- le pipeline complet ;
- l’API ;
- la configuration ;
- la journalisation ;
- les cas d’erreur et de sécurité.

Les tests end-to-end exécutent tout le pipeline sans utiliser Gemini.

## 18. Limites actuelles

La version actuelle :

- travaille principalement avec deux tables de démonstration ;
- attend des fichiers CSV ;
- prend en charge les documents Markdown et TXT ;
- ne se connecte pas directement à une base de données ;
- ne déploie pas automatiquement le LookML dans Looker ;
- ne valide pas les fichiers avec l’API officielle Looker ;
- ne crée pas automatiquement les règles d’accès aux données sensibles ;
- ne gère pas encore les clés primaires composites ;
- ne gère pas encore un nombre arbitraire de tables.

## 19. Évolutions possibles

Les évolutions possibles incluent :

- une configuration dynamique des tables ;
- la découverte automatique des sources ;
- la prise en charge de BigQuery ;
- l’introspection SQL ;
- les clés 