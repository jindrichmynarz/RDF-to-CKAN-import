#!/usr/bin/env python 
#-*- coding:utf-8 -*-

import hashlib, json, os, re, unicodedata

from Memoize import Memoize

def formatDate(date):
  """
    Format @date (an instance of datetime.datetime) to YYYY-MM-DD
    (format of xsd:date).
  """
  return date.strftime("%Y-%m-%d")

def getMappings():
  with open(os.path.join(root(), "etc", "mappings.json"), "r") as mappingsFile:
    return json.load(mappingsFile)

@Memoize
def root():
  """
    Return project's root.
  """
  return os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

def sha1(text):
  """
    Compute hexadecimal digest of @text's SHA1 hash. 
  """
  sha1 = hashlib.sha1()
  sha1.update(text)
  return sha1.hexdigest()

def slugify(text):
  """
    Return a slugified version of @text, for example
    "Public Sector" => "public-sector"
  """
   # Normalize accents
  text = "".join(
    (c for c in unicodedata.normalize("NFD", unicode(text)) if unicodedata.category(c) != "Mn")
  )
  # Clean unwanted characters
  return re.sub("[^a-zA-Z0-9]", "-", text.lower())

def writeAndRewind(file, content):
  """
    Write @content to @file and rewind the @file back to its start
    to enable repeated reading.
  """
  file.write(content.encode("UTF-8"))
  file.seek(0)
