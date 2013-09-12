#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import json, logging, os, subprocess
from collections import defaultdict
from rdflib import Graph, URIRef
from StringIO import StringIO
from tempfile import NamedTemporaryFile

import sparql, util
from Memoize import Memoize
from timeout import timeout, TimeoutError

# Whitelist of properties, for which it makes sense to resolve URIs of their objects
# and try to retrieve their labels.
RESOLVED_PROPERTIES = [
  "author", "license_id", "maintainer", "tags"
]

# URI to label mappings
MAPPINGS = util.getMappings() 

def arqTransform(transformation, dataset):
  """
    Transform Turtle @dataset using SPARQL CONSTRUCT query in @transformation
    using Jena ARQ's SPARQL processor.
  """
  with NamedTemporaryFile(suffix = ".ttl") as dataFile, \
       NamedTemporaryFile(suffix = ".rq") as queryFile, \
       NamedTemporaryFile(suffix = ".nt") as parsedFile:
    dataPath = dataFile.name
    queryPath = queryFile.name
    util.writeAndRewind(dataFile, dataset)
    util.writeAndRewind(queryFile, transformation)
        
    arqCommand = [
      "bash", os.path.join("bin", "arq"),
      "--data", dataPath,
      "--query", queryPath
    ]
    #with open(os.devnull) as devnull:
    transformedDataset, errors = subprocess.Popen(
        arqCommand,
        stderr = subprocess.PIPE,
        stdout = subprocess.PIPE
      ).communicate()
    if errors:
      logging.warn("Jena ARQ's parser errors: {0}".format(errors))
    return transformedDataset

def convertToDict(graph, resource, visited = None, lang = None):
  """
    Converts RDF @graph (instance of rdflib.graph.Graph) into dict.
    The dict's root is @resource.
  """
  # Mutable default arguments gotcha
  # http://docs.python-guide.org/en/latest/writing/gotchas/#what-you-should-do-instead
  if visited is None:
    visited = []
  resultDict = defaultdict(dict)
  for pred in set(graph.predicates(resource)):
    predicateTransformed = transformNode(pred)
    for obj in set(graph.objects(resource, pred)):
      if list(graph.predicates(obj)) and (obj not in visited):
        # Node with child nodes
        visited.append(obj)
        
        # Special handling of :extras that need to have values in the form of [key, value]
        if predicateTransformed == "extras":
          extraKey = list(graph.predicates(obj))[0]
          extraValue = list(graph.objects(obj, extraKey))[0]
          obj = [transformNode(item) for item in [extraKey, extraValue]]
        # Usual handling of embedded resources
        else: 
          obj = convertToDict(graph, obj, visited)
      else:
        # Leaf node
        if predicateTransformed in RESOLVED_PROPERTIES:
          try:
            obj = resolveResource(obj, lang)
          except TimeoutError:
            pass
        obj = transformNode(obj)
        # Tags must be slugified
        if predicateTransformed == "tags":
          obj = util.slugify(obj)

      if predicateTransformed in resultDict:
        prevObjects = resultDict[predicateTransformed]
        if isinstance(prevObjects, list):
          resultDict[predicateTransformed].append(obj)
        else:
          resultDict[predicateTransformed] = [prevObjects, obj]
      else:
        if predicateTransformed == "extras":
          obj = [obj]
        resultDict[predicateTransformed] = obj
  return resultDict

def getLabel(graph, resourceUri, lang):
  """
    Gets label for @resourceUri from RDF @graph (instance of rdflib.graph.Graph).
  """
  query = sparql.formatQuery("getLabel.tpl", params = {
    "lang" : lang,
    "resourceUri" : resourceUri,
  })
  results = [result[0] for result in graph.query(query)]
  if results:
    return results[0]
  else:
    return False

def getTransformation(datasetURI, lang):
  """
    Reads and format transformation from queries/transform.tpl.
  """
  return sparql.formatQuery("transform.tpl", params = {
    "datasetURI" : datasetURI,
    "lang" : lang,
  })

def initArq(config):
  """
    Initializes Jena ARQ by setting JENA_HOME environment variable if not set already.
  """
  var = "JENA_HOME"
  if not var in os.environ:
    assert var in config, "Value of the {0} attribute must be provided in config.json".format(var)
    os.environ[var] = config[var]

@Memoize
@timeout(10)
def resolveResource(resource, lang):
  """
    Tries to find resource-to-label mapping in etc/mappings.json, then
    resolves @resource's URI to its representation and tries
    to find @resource's label in a given @lang in it.
  """
  resourceStr = str(resource.toPython())
  if resourceStr in MAPPINGS:
    return MAPPINGS[resourceStr]
  if isinstance(resource, URIRef):
    g = Graph()
    resourceString = resource.toPython()
    try:
      g.load(resourceString)
    except:
      return resource
    label = getLabel(g, resourceString, lang)
    if label:
      return label
    else:
      return resource
  else:
    return resource

@Memoize
def transformDataset(datasetURI, dataset, lang):
  """
    Transforms RDF @dataset identified with @datasetURI into dict.
    Literals with @lang are preferred in the output.
  """
  logging.info("Transforming dataset {0}".format(datasetURI))
  transformation = getTransformation(datasetURI, lang)
  #  with open("transformation.rq", "w") as file:
  #    file.write(transformation.encode("UTF-8"))
  #  with open("dataset.ttl", "w") as file:
  #    file.write(dataset.encode("UTF-8"))
  #  raise SystemExit
  transformedDataset = arqTransform(transformation, dataset)
  graph = Graph()
  graph.load(StringIO(transformedDataset), format = "turtle")
  datasetDict = convertToDict(graph, URIRef(datasetURI), lang = lang) # datasetURI is the root
  # print json.dumps(datasetDict, indent = 4, ensure_ascii = False).encode("UTF-8")
  return datasetDict

def transformDatasets(datasets, lang):
  """
    Transforms a list of RDF @datasets into a list of dicts.
    Literals with @lang are preferred in the output.
  """
  transformedDatasets = map(
      lambda (datasetURI, details): transformDataset(datasetURI, details["dataset"], lang),
      datasets.items()
    )
  return transformedDatasets

@Memoize
def transformNode(node):
  """
    Transforms an RDF node (URIRef, Literal) into simplified string representation.
  """
  if not "toPython" in dir(node):
    return node
  ckanNs = "http://ckan.org/ns#"
  tmp = node.toPython()
  if isinstance(tmp, unicode):
    if tmp.startswith(ckanNs):
      return tmp.replace(ckanNs, "")
    else:
      return tmp
  else:
    return str(node)
