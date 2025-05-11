#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: qubes_prefs_info

short_description: qubes-prefs
description: Global qubes-prefs info

options:
  defaults:
    description: Get default property values, regardless of current values
    required: false
    type: bool
    default: false

author:
  - Brian Duggan <brian@dugga.net>
'''

EXAMPLES = '''
- name: Get qubes-prefs values
  qubes_prefs_info:
  register: qubes_prefs_result

- name: Get default qubes-prefs values
  qubes_prefs_info:
    defaults: true
  register: qubes_prefs_result
'''

RETURN = '''
check_updates_vm:
  description: Check for updates inside qubes
  type: bool
  returned: If defined, and if `defaults` is `false` or has default value
  sample: true
clockvm:
  description: Which VM to use as NTP proxy for updating AdminVM
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: sys-net
default_audiovm:
  description: Default AudioVM for VMs.
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: dom0
default_dispvm:
  description: Default DispVM base for service calls
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: default-dvm
default_guivm:
  description: Default GuiVM for VMs.
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: dom0
default_kernel:
  description: Which kernel to use when not overriden in VM
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: 6.12.21-1.fc37
default_netvm:
  description:
    - Default NetVM for AppVMs
    - Initial state is None, which means that AppVMs are not connected to the Internet.
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: sys-net
default_pool:
  description: Default storage pool
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: vm-pool
default_pool_kernel:
  description: Default storage pool for kernel volumes
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: linux-kernel
default_pool_private:
  description: Default storage pool for private volumes
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: vm-pool
default_pool_root:
  description: Default storage pool for root volumes
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: vm-pool
default_pool_volatile:
  description: Default storage pool for volatile volumes
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: vm-pool
default_qrexec_timeout:
  description: Default time in seconds after which qrexec connection attempt is deemed failed
  type: int
  returned: If defined, and if `defaults` is `false` or has default value
  sample: 60
default_shutdown_timeout:
  description: Default time in seconds for VM shutdown to complete
  type: int
  returned: If defined, and if `defaults` is `false` or has default value
  sample: 60
default_template:
  description: Default template for new AppVMs
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: fedora-41-xfce
management_dispvm:
  description: Default DispVM base for managing VMs
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: default-mgmt-dvm
stats_interval:
  description: Interval in seconds for VM stats reporting (memory, CPU usage)
  type: int
  returned: If defined, and if `defaults` is `false` or has default value
  sample: 3
updatevm:
  description: Which VM to use as yum proxy for updating AdminVM and TemplateVMs
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: sys-firewall
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bcduggan.qubes_ansible_aux.plugins.module_utils.qubes_prefs import QubesPrefs

def main():
  module = AnsibleModule(
    argument_spec=dict(
      defaults=dict(type="bool", required=False, default=False)
    ),
    supports_check_mode=True
  )
  prefs = QubesPrefs(module.params["defaults"])
  return module.exit_json(**prefs.get_properties())


if __name__ == "__main__":
  main()
