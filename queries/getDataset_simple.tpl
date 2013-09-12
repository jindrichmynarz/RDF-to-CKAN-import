# @param IRI $datasetURI

CONSTRUCT {
  <{{datasetURI}}> ?outbound_p ?outbound_o .
  ?outbound_o ?p2 ?o2 .
  ?o2 ?p3 ?o3 .
}
WHERE {
  <{{datasetURI}}> ?outbound_p ?outbound_o .
  OPTIONAL {
    ?outbound_o ?p2 ?o2 .
    FILTER (isBlank(?outbound_o))
    
    OPTIONAL {
      ?o2 ?p3 ?o3 .
      FILTER (isBlank(?o2))
    }
  }
}
