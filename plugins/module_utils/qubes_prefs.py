#!/usr/bin/python

from functools import partial
import qubesadmin

class QubesPrefs():

  def __init__(self, defaults, target=''):
    self.defaults = defaults
    self.app = qubesadmin.Qubes()
    self.app.cache_enabled = True
    self.target = (
      self.app.domains[target]
      if target 
      else self.app
    )
    self.getter = (
      self.target.property_get_default
      if self.defaults
      else partial(getattr, self.target)
    )

  def get_property(self, property):
    try:
      return self.getter(property)
    except AttributeError:
      return None

  def get_all_properties(self):
    return {
      property: self.get_property(property)
      for property in self.target.property_list()
    }

  def get_qube_name(self, obj):
    return (
      obj.name
      if type(obj) in (qubesadmin.vm.QubesVM, qubesadmin.label.Label)
      else obj
    )

  def get_properties(self):
    return {
      property: self.get_qube_name(value)
      for (property, value) in self.get_all_properties().items()
      # qubesadmin can return undefined prefs as None or the type, type
      if value is not None and type(value) is not type
    }

