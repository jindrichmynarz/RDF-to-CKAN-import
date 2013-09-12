# @param IRI $datasetURI

CONSTRUCT {
  <{{datasetURI}}> ?outbound_p ?outbound_o .
  ?dependent_o ?dependent_p2 ?dependent_o2 .
}
WHERE {
  <{{datasetURI}}> ?outbound_p ?outbound_o .
  OPTIONAL {
    {
      SELECT ?dependent_s ?dependent_o
      WHERE {
        ?dependent_s ?dependent_p ?dependent_o .
        FILTER (isBlank(?dependent_o)) 
      }
    } OPTION (TRANSITIVE, t_distinct, t_no_cycles, t_in(?dependent_s), t_out(?dependent_o)) .
    FILTER (?dependent_s = <{{datasetURI}}>)
    ?dependent_o ?dependent_p2 ?dependent_o2 .
  }
}
