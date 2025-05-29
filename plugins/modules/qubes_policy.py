#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: qubes_policy

short_description: qubes-policy
description: Create, replace, and delete Qubes OS policy

options:
  name:
    description: Create, replace, or remove this policy
    required: true
    type: str
  source:
    description:
      - File containing policy content
      - Mutually exclusive with O(content) option
      - One of O(source) or O(content) required
    required: false
    type: path
  content:
    description:
      - Policy content
      - Mutually exclusive with O(source) option
      - One of O(source) or O(content) required
    required: false
    type: str
  state:
    description: 
    required: false
    choices:
      - present
      - absent
    default: present

author:
  - Brian Duggan <brian@dugga.net>
'''

EXAMPLES = '''
- name: Write policy
  qubes_policy:
    name: 30-mgmtvm
    source: policy/30-mgmtvm

- name: Write include policy
  qubes_policy:
    name: include/admin-global-ro
    source: policy/include/admin-global-ro

- name: Remove policy
  qubes_policy:
    name: 35-redundant
    state: absent
'''

RETURN = '''
# check_updates_vm:
#   description: Check for updates inside qubes
#   type: bool
#   returned: If defined, and if `defaults` is `false` or has default value
#   sample: true
'''

import functools
from typing import Tuple, List, Dict
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bcduggan.qubes_ansible_aux.plugins.module_utils.policy_util import PolicyUtil, PolicyUtilError

def policy_util(func, *args, **kwargs):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    self = args[0]
    try:
      value = func(*args, **kwargs)
    except PolicyUtilError as exc:
      message = f"{str(exc)}: {str(exc.__cause__)}"
    else:
      message = ""
    finally:
      if message:
        self.ansible_module.fail_json(message)
    return value
  return wrapper

class PolicyModule():
  def __init__(self):
    self.ansible_module = AnsibleModule(
      argument_spec=dict(
        name=dict(type="str", required=True),
        source=dict(type="path", required=False),
        content=dict(type="str", required=False),
        state=dict(type="str", required=False, default="present")
      ),
      mutually_exclusive=([["source", "content"]]),
      # required_one_of=([["source", "content"]]),
      supports_check_mode=True
    )
    self.policy_util = self._PolicyUtil(self.ansible_module.params["name"])

  @policy_util
  def _PolicyUtil(self, name):
    return PolicyUtil(name)

  @policy_util
  def _lint(self, content):
    return self.policy_util.lint(content)

  @policy_util
  def _remove(self):
    return self.policy_util.remove()

  @policy_util
  def _replace(self, content, token):
    return self.policy_util.replace(content, token)

  def _result(self, changed: bool, before: str, after: str) -> Dict:
    common_result = {
      "changed": changed,
      "name": str(self.policy_util.name),
      "is_include": self.policy_util.is_include
    }
    diff_result = {
      **common_result,
      "diff": {
        "before": before,
        "after": after
      }
    }
    return (
      diff_result
      if self.ansible_module._diff
      else common_result
    )

  def _source_content(self) -> str:
    with open(self.ansible_module.params["source"], "r", encoding="utf-8") as source:
      return source.read()

  def present(self):
    new_content = (
      self._source_content()
      if self.ansible_module.params["source"]
      else self.ansible_module.params["content"]
    )

    self._lint(new_content)

    try:
      current_content, token = self.policy_util.get()
    except PolicyUtilError:
      # No test for how RPC execution failed:
      # qrexec.tools.qubes_policy_editor:manage_policy
      current_content = ""
      token = "new"

    # Will not create an empty policy file
    if self.ansible_module.check_mode or current_content == new_content:
      changed = False
    else:
      self._replace(new_content, token)
      changed = True

    self.ansible_module.exit_json(
      **self._result(changed, current_content, new_content),
      state="present",
      new=(token == "new"),
      content=new_content
    )
      
  def absent(self):
    if self.ansible_module.check_mode:
      changed = False
    else:
      self._remove()
      changed = True

    self.ansible_module.exit_json(
      **self._result(changed, self.policy_util.name, ""),
      state="absent"
    )

  def run(self):
    if self.ansible_module.params["state"] == "present":
      self.present()
    elif self.ansible_module.params["state"] == "absent":
      self.absent()
  
def main():
  policy_module = PolicyModule()
  policy_module.run()

if __name__ == "__main__":
  main()
