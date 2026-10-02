# Exemples d’utilisation de l’API

## 1. Démarrer le serveur

Depuis la racine du projet :

```powershell
python -m uvicorn app.api.main:app `
    --host 127.0.0.1 `
    --port 8001
```

Documentation Swagger :

```text
http://127.0.0.1:8001/docs
```

## 2. Vérifier la santé du service

```powershell
Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8001/health"
```

Réponse attendue :

```json
{
  "status": "healthy",
  "service": "semantic-layer-builder",
  "version": "0.1.0"
}
```

## 3. Analyser les métadonnées d’un CSV

```powershell
$body = @{
    file_path = "data/inputs/clients.csv"
} | ConvertTo-Json
```

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/metadata/analyze" `
    -ContentType "application/json" `
    -Body $body
```

## 4. Analyser une documentation métier

```powershell
$body = @{
    file_path = "data/documentation/clients_documentation.md"
} | ConvertTo-Json
```

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/documentation/analyze" `
    -ContentType "application/json" `
    -Body $body
```

## 5. Comparer un CSV et sa documentation

```powershell
$body = @{
    csv_file_path = "data/inputs/clients.csv"
    documentation_file_path = "data/documentation/clients_documentation.md"
} | ConvertTo-Json
```

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/consistency/analyze" `
    -ContentType "application/json" `
    -Body $body
```

## 6. Analyser une relation entre deux tables

```powershell
$body = @{
    source_file_path = "data/inputs/orders.csv"
    source_column = "CLIENT_ID"
    target_file_path = "data/inputs/clients.csv"
    target_column = "CLIENT_ID"
    documented_cardinality = "many-to-one"
} | ConvertTo-Json
```

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/relationships/analyze" `
    -ContentType "application/json" `
    -Body $body
```

## 7. Construire un brouillon de modèle sémantique

```powershell
$body = @{
    model_name = "sales"
    project_name = "semantic_layer_builder"
    clients_csv_path = "data/inputs/clients.csv"
    clients_documentation_path = "data/documentation/clients_documentation.md"
    orders_csv_path = "data/inputs/orders.csv"
    orders_documentation_path = "data/documentation/orders_documentation.md"
    relationship_source_column = "CLIENT_ID"
    relationship_target_column = "CLIENT_ID"
    documented_cardinality = "many-to-one"
} | ConvertTo-Json
```

```powershell
Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/semantic-model/build" `
    -ContentType "application/json" `
    -Body $body
```

Sans connexion ni schéma physique, le résultat doit indiquer :

```json
{
  "generation_ready": false
}
```

## 8. Construire un modèle sémantique prêt

Ajoute :

```powershell
$body = @{
    model_name = "sales"
    project_name = "semantic_layer_builder"
    clients_csv_path = "data/inputs/clients.csv"
    clients_documentation_path = "data/documentation/clients_documentation.md"
    orders_csv_path = "data/inputs/orders.csv"
    orders_documentation_path = "data/documentation/orders_documentation.md"
    relationship_source_column = "CLIENT_ID"
    relationship_target_column = "CLIENT_ID"
    documented_cardinality = "many-to-one"
    connection_name = "bigquery_connection"
    default_schema = "analytics"
} | ConvertTo-Json
```

## 9. Prévisualiser le LookML

```powershell
$result = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/lookml/preview" `
    -ContentType "application/json" `
    -Body $body
```

Résumé :

```powershell
$result.status
$result.pipeline_stage
$result.validation_report.valid
$result.written_files
```

Résultat attendu :

```text
success
lookml_validation
True
[]
```

## 10. Afficher les artefacts prévisualisés

```powershell
$result.generation_result.files |
    Select-Object file_name, file_type, source_name
```

Afficher le contenu d’un fichier :

```powershell
(
    $result.generation_result.files |
    Where-Object {
        $_.file_name -eq "sales.model.lkml"
    }
).content
```

## 11. Générer et écrire les fichiers

```powershell
$generationBody = @{
    model_name = "sales"
    project_name = "semantic_layer_builder"
    clients_csv_path = "data/inputs/clients.csv"
    clients_documentation_path = "data/documentation/clients_documentation.md"
    orders_csv_path = "data/inputs/orders.csv"
    orders_documentation_path = "data/documentation/orders_documentation.md"
    relationship_source_column = "CLIENT_ID"
    relationship_target_column = "CLIENT_ID"
    documented_cardinality = "many-to-one"
    connection_name = "bigquery_connection"
    default_schema = "analytics"
    output_directory = "data/outputs/lookml"
    overwrite = $false
} | ConvertTo-Json
```

```powershell
$result = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8001/api/v1/lookml/generate" `
    -ContentType "application/json" `
    -Body $generationBody
```

Afficher les fichiers écrits :

```powershell
$result.written_files
```

## 12. Autoriser explicitement l’écrasement

```powershell
$generationBody = @{
    model_name = "sales"
    project_name = "semantic_layer_builder"
    clients_csv_path = "data/inputs/clients.csv"
    clients_documentation_path = "data/documentation/clients_documentation.md"
    orders_csv_path = "data/inputs/orders.csv"
    orders_documentation_path = "data/documentation/orders_documentation.md"
    relationship_source_column = "CLIENT_ID"
    relationship_target_column = "CLIENT_ID"
    documented_cardinality = "many-to-one"
    connection_name = "bigquery_connection"
    default_schema = "analytics"
    output_directory = "data/outputs/lookml"
    overwrite = $true
} | ConvertTo-Json
```

L’écrasement ne doit être activé que sur demande explicite.

## 13. Codes HTTP importants

```text
200 : requête traitée avec succès
400 : entrée ou chemin invalide
404 : fichier source introuvable
409 : fichier existant et overwrite=false
422 : requête Pydantic invalide ou génération bloquée
500 : erreur interne inattendue
```

## 14. Identifiant de requête

Chaque réponse contient l’en-tête :

```text
X-Request-ID
```

Exemple :

```powershell
$response = Invoke-WebRequest `
    -Method Get `
    -Uri "http://127.0.0.1:8001/health" `
    -UseBasicParsing

$response.Headers["X-Request-ID"]
```

Cet identifiant permet de retrouver une requête dans les journaux applicatifs.