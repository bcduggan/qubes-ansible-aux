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

import sys
import io
import pathlib
import subprocess
import functools
from typing import Tuple, List, Dict
from ansible.module_utils.basic import AnsibleModule
# from qrexec.exc import PolicySyntaxError
from qrexec.policy.admin_client import PolicyClient
import qrexec.tools.qubes_policy_lint as linter
import qrexec.tools.qubes_policy_lint as linter
import qrexec.tools.qubes_policy_editor as editor

class ToolContextError(Exception):
  """Generic qrexec/qubesadmin tool error"""
  def __nit__(self, message):
    super().__init__(message)

class ToolContext():
  def __init__(self, input: str = ""):
    self.input = io.StringIO()
    self.input.write(input)
    self.input.seek(0)
    self.output = io.StringIO()
    super().__init__()

  def __enter__(self):
    self.stdin = sys.stdin
    self.stdout = sys.stdout
    sys.stdin = self.input
    sys.stdout = self.output

  def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
    sys.stdin = self.stdin
    sys.stdout = self.stdout
    if exc_type is SystemExit and exc_value.code == 1:
      raise ToolContextError(self.output.getvalue())
    return False

class PolicyUtilError(Exception):
  def __nit__(self, message):
    super().__init__(message)

class PolicyUtil:
  def __init__(self, name: str):
    try:
      with ToolContext():
        valid_name = editor.validate_name(name)
    except ToolContextError as exc:
      raise PolicyUtilError("Name validation failed") from exc
    self.name = pathlib.PurePosixPath(valid_name)
    self.is_include = self.name.parent == "include"
    self.client = PolicyClient()

  def lint(self, content: str) -> None:
    try:
      with ToolContext(content):
        linter.parse_file("-", show=True, include_service=self.is_include)
    except ToolContextError as exc:
      raise PolicyUtilError("Lint failed") from exc

  def _do(self, method, *args, **kwargs) -> Tuple[str, str] | List[str] | None:
    method_name = (
      "policy_include_"+method
      if self.is_include
      else "policy_"+method
    )
    client_method = getattr(self.client, method_name)
    try:
      value = client_method(*args, **kwargs)
    except subprocess.CalledProcessError as exc:
      raise PolicyUtilError(f"Error while running method {method}") from exc
    return value

  def get(self) -> Tuple[str, str]:
    return self._do("get", self.name)

  def remove(self) -> None:
    self._do("remove", self.name)

  def replace(self, content: str, token: str):
    self._do("replace", self.name, content, token)
    
#   def list(self) -> List[str]:
#     return self._do("list")

def policy_util(func, *args, **kwargs):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      value = func(*args, **kwargs)
    except PolicyUtilError as exc:
      message = f"{str(exc)}: {str(exc.__cause__)}"
    else:
      message = ""
    finally:
      if message:
        # args[0] == self
        args[0].ansible_module.fail_json(message)
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

  def _result(self, before: str, after: str, changed: bool = False) -> Dict:
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

    if self.ansible_module.check_mode or current_content == new_content:
      self.ansible_module.exit_json(
        **self._result(current_content, new_content),
        state="present",
        new=(token == "new"),
        content=new_content
      )
    else:
      self._replace(new_content, token)
      self.ansible_module.exit_json(
        **self._result(current_content, new_content, changed=True),
        state="present",
        new=(token == "new"),
        content=new_content
      )
      
  def absent(self):
    if self.ansible_module.check_mode:
      self.ansible_module.exit_json(
        **self._result(self.name, ""),
        state="absent"
      )
    else:
      self._remove()
      self.ansible_module.exit_json(
        **self._result(self.name, "", changed=True),
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
