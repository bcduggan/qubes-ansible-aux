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
  path:
    description:
      - File containing policy content
      - Mutually exclusive with O(content) option
      - One of O(path) or O(content) required when O(state) is "present"
    required: false
    type: path
  content:
    description:
      - Policy content
      - Mutually exclusive with O(path) option
      - One of O(path) or O(content) required when O(state) is "present"
    required: false
    type: str
  state:
    description: Intended state of the policy
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
    path: policy/30-mgmtvm

- name: Write include policy
  qubes_policy:
    name: include/admin-global-ro
    path: policy/include/admin-global-ro

- name: Write templated policy
  qubes_policy:
    name: 30-split-ssh
    content: "{{ lookup('ansible.builtin.template', './templates/policy/30-split-ssh.j2') }}"

- name: Remove policy
  qubes_policy:
    name: 35-redundant
    state: absent
'''

RETURN = '''
name:
  description: The validated policy name
  type: str
  returned: always
  sample: 30-split-ssh
is_include:
  description: Whether the policy is an include policy
  type: bool
  returned: always
state:
  description: Effective state of the policy
  type: str
  returned: always
  sample: present
new:
  description: Whether the policy replaced an existing policy
  type: bool
  returned: When RV(state) is "present"
content:
  description: Content of the policy
  type: str
  returned: When RV(state) is "present"
  sample: |
    qubes.SSHAgent * @tag:ssh-agent ssh-agent allow
'''

import os
import functools
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
        path=dict(type="path", required=False),
        content=dict(type="str", required=False),
        state=dict(type="str", required=False, default="present")
      ),
      required_if=[('state', 'present', ('path', 'content'), True)],
      mutually_exclusive=[("path", "content")],
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
  def _replace(self, content, token):
    return self.policy_util.replace(content, token)

  def _result(self, changed: bool) -> dict[str, bool | str]:
    return {
      "changed": changed,
      "name": self.policy_util.name,
      "is_include": self.policy_util.is_include,
      "state": self.ansible_module.params["state"]
    }

  def _diff_result(self, header_tag: str, before: str, after: str) -> dict[str, str]:
    return {
      "before": before,
      "before_header": f"{self.policy_util.name} ({header_tag})",
      "after": after,
      "after_header": f"{self.policy_util.name} ({header_tag})"
    }

  def _state_diff_result(self, before: str, after: str) -> dict[str, str]:
    return self._diff_result("state", before, after)

  def _absent_result(self, changed: bool, before_state: str) -> dict[str, bool | str | list[dict[str, str]]]:
    anti_state = (
      "present"
      if before_state == "absent"
      else "absent"
    )

    after_state = (
      anti_state
      if changed
      else before_state
    ) + os.linesep

    return (
      {
        **self._result(changed),
        "diff": [self._state_diff_result(before_state + os.linesep, after_state)]
      }
      if self.ansible_module._diff
      else self._result(changed)
    )
    
  def _present_result(
    self, changed: bool, token: str, before_content: str, after_content: str
  ) -> dict[str, bool | str | list[dict[str, str]]]:

    before_state = (
      "absent"
      if token == "new"
      else "present"
    ) + os.linesep

    after_state = (
      "present"
      if changed
      else before_state
    ) + os.linesep

    present_result = {
      **self._result(changed),
      "new": (token == "new"),
      "content": after_content
    }

    return (
      {
        **present_result,
        "diff": [
          self._state_diff_result(before_state, after_state),
          self._diff_result("content", before_content, after_content)
        ]
      }
      if self.ansible_module._diff
      else present_result
    )

  def _path_content(self) -> str:
    with open(self.ansible_module.params["path"], "r", encoding="utf-8") as path:
      return path.read()

  def present(self) -> None:
    new_content = (
      self._path_content()
      if self.ansible_module.params["path"]
      else self.ansible_module.params["content"]
    )

    self._lint(new_content)

    try:
      current_content, token = self.policy_util.get()
    except PolicyUtilError:
      current_content = ""
      token = "new"

    # Will not create an empty policy file
    if self.ansible_module.check_mode or current_content == new_content:
      changed = False
    else:
      self._replace(new_content, token)
      changed = True

    self.ansible_module.exit_json(
      **self._present_result(changed, token, current_content, new_content),
    )

  def absent(self):
    policies = self.policy_util.list()
    current_state = (
      "present"
      if self.policy_util.name in policies
      else "absent"
    )
    print(policies)

    if self.ansible_module.check_mode:
      changed = False
    else:
      try:
        self.policy_util.remove()
      except PolicyUtilError:
        changed = False
      else:
        changed = True

    self.ansible_module.exit_json(
      **self._absent_result(changed, current_state),
    )

  def run(self):
    if self.ansible_module.params["state"] == "present":
      self.present()
    elif self.ansible_module.params["state"] == "absent":
      self.absent()
  
def main():
  PolicyModule().run()

if __name__ == "__main__":
  main()
