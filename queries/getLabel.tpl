# @param string $lang
# @param IRI $resourceUri

PREFIX dc:      <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
PREFIX schema:  <http://schema.org/>

SELECT ?label
WHERE {
  VALUES ?labelProperty {
    dc:title
    dcterms:title
    foaf:name
    rdfs:label
    schema:name
    skos:prefLabel
  }
  <{{resourceUri}}> ?labelProperty ?label .
  BIND (
    IF(lang(?label) = "{{lang}}", 1,
    IF(langMatches(lang(?label), "{{lang}}"), 0.75,
    IF(lang(?label) = "", 0.5, 0))
  ) AS ?score)
}
ORDER BY DESC(?score)
LIMIT 1
