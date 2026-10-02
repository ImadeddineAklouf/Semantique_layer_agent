# Generated from clients.csv
# Validation status: warning
# WARNING: La documentation déclare des informations manquantes.

view: clients {
  sql_table_name: analytics.CLIENTS ;;

  dimension: client_id {
    label: "Client ID"
    description: "identifiant technique unique du client"
    type: number
    primary_key: yes
    sql: ${TABLE}.CLIENT_ID ;;
  }

  # WARNING: Cette dimension contient une donnée sensible.
  dimension: client_name {
    label: "Client Name"
    description: "nom complet du client"
    type: string
    # Sensitive field: access controls should be reviewed.
    sql: ${TABLE}.CLIENT_NAME ;;
  }

  dimension: country {
    label: "Country"
    description: "pays de résidence principal du client"
    type: string
    sql: ${TABLE}.COUNTRY ;;
  }

  dimension: creation_date {
    label: "Creation Date"
    description: "date d'enregistrement du client dans le système"
    type: date
    datatype: date
    sql: ${TABLE}.CREATION_DATE ;;
  }

  dimension: is_active {
    label: "Is Active"
    description: "indique si le client est actuellement actif"
    type: yesno
    sql: ${TABLE}.IS_ACTIVE ;;
  }

  measure: count {
    label: "Count"
    description: "Nombre total d'enregistrements de la vue clients."
    type: count
  }
}
