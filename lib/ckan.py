#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import json, logging
from ckanclient import CkanClient

import transform, util

def updateCkanInstance(ckanInstance, datasets):
  """
    Updates @ckanInstance with @datasets.
  """
  ckan = CkanClient(base_location = ckanInstance["api"],
                    api_key = ckanInstance["key"])
  transformedDatasets = transform.transformDatasets(datasets, ckanInstance["lang"])

  for dataset in transformedDatasets:
    updateDataset(ckan, dataset)
  
  if "group" in ckanInstance:
    updateGroup(ckan, [dataset["name"] for dataset in transformedDatasets], ckanInstance["group"])

def updateCkanInstances(ckanInstances, datasets):
  """
    Updates a list of @ckanInstances with @datasets.
  """
  for ckanInstance in ckanInstances:
    updateCkanInstance(ckanInstance, datasets)

def updateDataset(ckanInstance, dataset):
  """
    Updates @ckanInstance with @dataset, either creating it or updating
    existing one.
  """
  logging.info("Updating dataset {0}".format(dataset["name"]))
  if ckanInstance.package_search("name:{0}".format(dataset["name"]))["count"] == 1:
    # Dataset with given :name already exists.
    # Update an existing dataset.
    ckanInstance.package_entity_put(dataset)
  else:
    # Dataset doesn't yet exist
    # Create a new dataset.
    ckanInstance.package_register_post(dataset)

def updateGroup(ckanInstance, datasetNames, group):
  """
    Associates list of @datasetNames with an existing @group in a @ckanInstance.
  """
  logging.info("Updating group {0}".format(group))
  groupData = ckanInstance.group_entity_get(group)
  if "packages" in groupData:
    groupData["packages"] += datasetNames
    groupData["packages"] = list(set(groupData["packages"]))
  else:
    groupData["packages"] = datasetNames
  ckanInstance.group_entity_put(groupData)
