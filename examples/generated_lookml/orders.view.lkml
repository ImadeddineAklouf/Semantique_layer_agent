# Generated from orders.csv
# Validation status: warning
# WARNING: La documentation déclare des informations manquantes.

view: orders {
  sql_table_name: analytics.ORDERS ;;

  dimension: order_id {
    label: "Order ID"
    description: "identifiant technique unique de la commande"
    type: number
    primary_key: yes
    sql: ${TABLE}.ORDER_ID ;;
  }

  dimension: client_id {
    label: "Client ID"
    description: "identifiant du client ayant effectué la commande"
    type: number
    sql: ${TABLE}.CLIENT_ID ;;
  }

  dimension: order_date {
    label: "Order Date"
    description: "date de création de la commande"
    type: date
    datatype: date
    sql: ${TABLE}.ORDER_DATE ;;
  }

  dimension: amount {
    label: "Amount"
    description: "montant total de la commande"
    type: number
    sql: ${TABLE}.AMOUNT ;;
  }

  dimension: status {
    label: "Status"
    description: "statut actuel de la commande"
    type: string
    sql: ${TABLE}.STATUS ;;
  }

  measure: count {
    label: "Count"
    description: "Nombre total d'enregistrements de la vue orders."
    type: count
  }

  # WARNING: Mesure générée automatiquement. La pertinence métier doit être validée.
  measure: total_amount {
    label: "Total Amount"
    description: "Sum de la colonne AMOUNT."
    type: sum
    sql: ${amount} ;;
  }

  # WARNING: Mesure générée automatiquement. La pertinence métier doit être validée.
  measure: average_amount {
    label: "Average Amount"
    description: "Average de la colonne AMOUNT."
    type: average
    sql: ${amount} ;;
  }

  # WARNING: Mesure générée automatiquement. La pertinence métier doit être validée.
  measure: minimum_amount {
    label: "Minimum Amount"
    description: "Min de la colonne AMOUNT."
    type: min
    sql: ${amount} ;;
  }

  # WARNING: Mesure générée automatiquement. La pertinence métier doit être validée.
  measure: maximum_amount {
    label: "Maximum Amount"
    description: "Max de la colonne AMOUNT."
    type: max
    sql: ${amount} ;;
  }
}
