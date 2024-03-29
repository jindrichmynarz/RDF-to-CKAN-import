#!/usr/bin/env python 
#-*- coding:utf-8 -*-

class Memoize (object):
  """
    Memoization decorator stolen from http://dzone.com/snippets/memoization-decorator
  """
  def __init__(self, f):
    self.f = f
    self.mem = {}

  def __call__(self, *args, **kwargs):
    if (args, str(kwargs)) in self.mem:
      return self.mem[args, str(kwargs)]
    else:
      tmp = self.f(*args, **kwargs)
      self.mem[args, str(kwargs)] = tmp
      return tmp
