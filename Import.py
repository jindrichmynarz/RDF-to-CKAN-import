#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import datetime, json, logging, os, shelve 
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper

from lib import ckan, Memoize, sparql, transform, util

def filterDatasets(datasets, shelf):
  """
    Narrow down @datasets by checking if they were modified since the previous
    run of the script.
  """
  filteredDatasets = dict(filter(
      lambda (datasetURI, details): isModified(datasetURI, details["hash"], shelf),
      datasets.items()
    ))
  return filteredDatasets

def getConfig():
  """
    Reads JSON configuration from etc/config.json
  """
  with open(os.path.join(util.root(), "etc", "config.json"), "r") as configFile:
    return json.loads(configFile.read())

def getDatasetMetadata(sparqlEndpoint, datasetURI):
  """
    Retrieves description of dataset identified by @datasetURI from the @sparqlEndpoint.
    The return value corresponds to concise-bounded description.
    Note that non-Virtuoso SPARQL endpoints need to use queries/getDataset_simple.tpl instead.
  """
  query = sparql.formatQuery("getDataset.tpl", params = {
    "datasetURI" : datasetURI,
  })
  return sparql.construct(sparqlEndpoint, query)

def getDatasets(sparqlEndpoint, modifiedSince):
  """
    Returns a dict of datasets fetched from @sparqlEndpoint along with the datasets'
    hashes. The dataset are narrowed down to those that were modified since @modifiedSince.
  """
  datasetURIs = getDatasetURIs(sparqlEndpoint, modifiedSince)
  datasets = {}
  for datasetURI in datasetURIs:
    datasets[datasetURI] = {
      "dataset" : getDatasetMetadata(sparqlEndpoint, datasetURI),
    }
    datasets[datasetURI]["hash"] = util.sha1(datasets[datasetURI]["dataset"])
  return datasets

def getDatasetURIs(sparqlEndpoint, modifiedSince):
  """
    Retrieve URIs of relevant datasets from @sparqlEndpoint based on SPARQL
    SELECT query configured in the queries/getDatasetURIs.tpl file.
  """
  query = sparql.formatQuery("getDatasetURIs.tpl", params = {
    "modifiedSince" : modifiedSince,  
  })
  return sparql.select1binding(sparqlEndpoint, query)

def getShelf():
  """
    Return an instance of shelve.Shelf, in which we store hashes
    of the previously processed datasets.
  """
  path = os.path.join(util.root(), "db", "shelf")
  return shelve.open(path)

def isModified(datasetURI, datasetHash, shelf):
  """
    Test if @datasetHash associated with @datasetURI matches the hash
    stored in @shelf under the same @datasetURI. 
  """
  if ("datasets" in shelf) and (datasetURI in shelf["datasets"]):
    oldHash = shelf["datasets"][datasetURI]
    return not(oldHash == datasetHash)
  else:
    True

def updateShelfHashes(filteredDatasets, shelf):
  """
    Update datasets' SHA1 hashes based on their last received contents,
    so that the script can skip them at the next run, if datasets' hashes
    remain the same.
  """ 
  for datasetURI, details in filteredDatasets.items():
    if "datasets" in shelf:
      shelf["datasets"][datasetURI] = details["hash"]
    else:
      shelf["datasets"] = {
        datasetURI : details["hash"],    
      }
  return shelf

def main():
  logging.basicConfig(
    filename = os.path.join("log", "import.log"),
    format = "%(asctime)s %(levelname)s:%(message)s",
    level = logging.INFO
  )
  config = getConfig()
  shelf = getShelf()
  transform.initArq(config["JENA_HOME"])

  sparqlEndpoint = SPARQLWrapper(config["sparql"]["endpoint"])
  modifiedSince = shelf.get("lastRun", util.formatDate(datetime.fromtimestamp(0)))
  shelf["lastRun"] = util.formatDate(datetime.now())

  datasets = getDatasets(sparqlEndpoint, modifiedSince)
  filteredDatasets = filterDatasets(datasets, shelf)
  ckan.updateCkanInstances(config["ckanInstances"], filteredDatasets)
  
  shelf = updateShelfHashes(filteredDatasets, shelf)
  shelf.close()

if __name__ == "__main__":
  main()
