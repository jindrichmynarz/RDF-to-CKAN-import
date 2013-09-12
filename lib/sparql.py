#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import os, pickle
from django.template import Context, Template
from django.conf import settings
from SPARQLWrapper import JSON, N3

import util

settings.configure() # Django boilerplate

def construct(sparqlEndpoint, query, returnFormat = N3):
  """
    Execute SPARQL CONSTRUCT @query on @sparqlEndpoint.
  """
  return executeQuery(sparqlEndpoint, query, returnFormat)

def executeQuery(sparqlEndpoint, query, returnFormat = JSON):
  """
    Execute SPARQL @query on @sparqlEndpoint.
    Cache the query results temporarily in the tmp directory.
  """
  path = os.path.join(util.root(), "tmp", util.sha1(sparqlEndpoint.endpoint + query))
  if os.path.exists(path):
    with open(path, "rb") as file:
      return pickle.load(file)
  else:
    sparqlEndpoint.setQuery(unicode(query.decode("UTF-8")))
    sparqlEndpoint.setReturnFormat(returnFormat)
    results = sparqlEndpoint.query().convert()
    with open(path, "wb") as file:
      pickle.dump(results, file)
    return results

def formatQuery(queryTemplateFileName, params):
  """
    Read file at queries/@queryTemplateFileName and format it with @params
    using Django templates.
  """
  return formatQueryFile(os.path.join(util.root(), "queries", queryTemplateFileName), params)

def formatQueryFile(queryTemplatePath, params):
  """
    Read file at @queryTemplatePath and format it with @params using Django templates.
  """
  with open(queryTemplatePath, "r") as queryTemplate:
    return formatQueryString(queryTemplate.read().decode("UTF-8"), params)

def formatQueryString(queryTemplate, params):
  """
    Format SPARQL @queryTemplate with @params using Django templates.
  """
  template = Template(queryTemplate)
  return template.render(Context(params))

def select(sparqlEndpoint, query, returnFormat = JSON):
  """
    Execute SPARQL SELECT @query and return bindings in a dict structure.
  """
  results = executeQuery(sparqlEndpoint, query, returnFormat)
  return results["results"]["bindings"]

def select1binding(sparqlEndpoint, query, returnFormat = JSON):
  """
    Execute SPARQL SELECT @query and return a list for single binding. 
  """
  results = select(sparqlEndpoint, query, returnFormat)
  if results:
    keys = results[0].keys()
    if keys:
      assert len(keys) == 1, "SPARQL results have more than 1 binding"
      binding = keys[0]
      return [result[binding]["value"] for result in results]
    else:
      raise Exception("The following query failed:\n{0}".format(query))
  else:
    return []
