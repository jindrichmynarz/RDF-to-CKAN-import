# @param xsd:date $modifiedSince 

PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX void:    <http://rdfs.org/ns/void#>
PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?dataset
WHERE {
  ?dataset a void:Dataset .
  # Commented out for testing purposes: 
  #  dcterms:publisher <http://opendata.cz> ;
  #  dcterms:modified ?modified .
  #FILTER (?modified > "{{modifiedSince}}"^^xsd:date)
  FILTER (strstarts(str(?dataset), "http://linked.opendata.cz"))
}
