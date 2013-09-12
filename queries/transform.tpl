# @param IRI $datasetURI
# @param string $lang

PREFIX :        <http://ckan.org/ns#>
PREFIX dcat:    <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX qb:      <http://purl.org/linked-data/cube#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX void:    <http://rdfs.org/ns/void#>

CONSTRUCT {
  <{{datasetURI}}> :name ?name ;
    ?datasetTarget ?datasetO ;
    :author ?author ;
    :resources ?distribution, ?dataDump, ?exampleResource, ?sparqlEndpoint ;
    :extras ?extraResource .

  ?extraResource ?extraProperty ?extraO . 
 
  ?distribution ?distributionTarget ?distributionO .
   
  ?dataDump :name ?dataDumpLabel ; 
    :type "file" ;
    :url ?dataDump .

  ?exampleResource :name ?exampleResourceLabel ; 
    :type "file" ;
    :url ?exampleResource .
     
  ?sparqlEndpoint :format "api/sparql" ;
    :name ?sparqlEndpointLabel ; 
    :type "api" ;
    :url ?sparqlEndpoint .
}
WHERE {
  # dcat:Dataset, void:Dataset
  VALUES (?datasetTarget              ?datasetSource) {
         #(:author                     dcterms:creator)
         #(:author_email )
         #(:groups )
         #(:id )
         (:license_id                 dcterms:license)
         (:license_id                 dcterms:rights)
         (:maintainer                 dcterms:publisher)
         #(:maintainer_email )
         (:notes                      dcterms:description)
         (:tags                       dcterms:subject)
         (:tags                       dcat:keyword)
         (:title                      dcterms:title) 
         #(:version )
         #qb:structure
         #void:exampleResource
         #dcterms:identifier
         #dcterms:language
         #dcterms:temporal
         #dcterms:accrualPeriodicity
         #dcat:accessURL
  }
  
  # Extras
  VALUES ?extraProperty {
    dcterms:issued
    dcterms:modified
    dcterms:creator # May have multiple values and :author permits only single value.
  }

  # dcat:Distribution
  VALUES (?distributionTarget ?distributionSource) {
         (:description        dcterms:description)
         (:format             dcterms:format)
         (:last_modified      dcterms:modified)
         (:mimetype           dcat:mediaType)
         (:size               dcat:byteSize)
         (:url                dcat:downloadURL)
  }
  
  # Label translations
  BIND ("{{lang}}" AS ?lang)
  VALUES (?lang ?dataDumpLabel      ?exampleResourceLabel ?sparqlEndpointLabel) {
         ("cs"  "Datový export"@cs  "Příklad zdroje"@cs   "SPARQL rozhraní"@cs)
         ("en"  "Data dump"@en      "Example resource"@en "SPARQL endpoint"@en)
  }

  # Select a single :name to be used as dataset's identifier
  {
    SELECT ?name
    WHERE { 
      # Accepted "title" properties 
      {
        <{{datasetURI}}> dcterms:title ?title .
      } UNION {
        <{{datasetURI}}> rdfs:label ?title .
      }
      
      # Set preferred language forms of title
      BIND (
        IF(lang(?title) = "{{lang}}", 1,
        IF(langMatches(lang(?title), "{{lang}}"), 0.75,
        IF(lang(?title) = "", 0.5, 0))
      ) AS ?score)
      
      # Transform dataset title into URI slug
      BIND (str(?title) AS ?titleStr)
      BIND (
        encode_for_uri(
          lcase(
            # Replace all non-ASCII characters by dash
            replace(
              # Trim to maximum 100 characters
              substr(?titleStr, 1, if((strlen(?titleStr) < 100), strlen(?titleStr), 100)),
              "[^A-Za-z0-9]",
              "-"
            )
          )
        ) AS ?name)
    }
    ORDER BY DESC(?score)
    LIMIT 1
  }

  # Select a single source :url
  OPTIONAL {
    {
      SELECT ?url
      WHERE {
        {
          <{{datasetURI}}> dcat:landingPage ?url .
        } UNION {
          <{{datasetURI}}> dcterms:source ?url .
        }
        # ?url must be a resource or match URL regex
        FILTER (
          isIRI(?url)
          ||
          regex(str(?url), "^(https?|ftp|file)://[-a-zA-Z0-9+&@#/%?=~_|!:,.;]*[-a-zA-Z0-9+&@#/%=~_|]")  
        )
      }
      LIMIT 1
    }
  }

  OPTIONAL {
    {
      SELECT ?author
      WHERE {
        <{{datasetURI}}> dcterms:creator ?author .
      }
      ORDER BY DESC(?author)
      LIMIT 1
    }
  }
  
  <{{datasetURI}}> ?datasetSource ?datasetO ;
    ?extraProperty ?extraO .
  FILTER (
    !isLiteral(?datasetO)
    ||
    (lang(?datasetO) = "")
    ||
    langMatches(lang(?datasetO), "{{lang}}")
  )
  BIND (iri(concat("http://example.com/", sha1(str(?extraO)))) AS ?extraResource)

  OPTIONAL {
    <{{datasetURI}}> dcat:distribution ?distribution .
    ?distribution ?distributionSource ?distributionO .
    FILTER (
      !isLiteral(?distributionO)
      ||
      (lang(?distributionO) = "")
      ||
      langMatches(lang(?distributionO), "{{lang}}")
    )
  }

  OPTIONAL {
    <{{datasetURI}}> void:dataDump ?dataDump .
  }

  OPTIONAL {
    <{{datasetURI}}> void:exampleResource ?exampleResource .
  }

  OPTIONAL {
    <{{datasetURI}}> void:sparqlEndpoint ?sparqlEndpoint .
  }
}
