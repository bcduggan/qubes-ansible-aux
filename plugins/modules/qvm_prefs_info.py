#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: qvm_prefs_info

short_description: qvm-prefs
description: qvm-prefs for a qube

options:
  name:
    description: Get prefs for this qube
    required: true
    type: str
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
audiovm:
  description: VM used for Audio
  type: str
  returned: If defined, and if `defaults` is `false` or has default value
  sample: dom0
autostart:
  description: Setting this to True means that VM should be autostarted on dom0 boot.
  type: bool
  returned: If defined, and if `defaults` is `false` or has default value
backup_timestamp:
  description: Time of last backup of the qube, in seconds since unix epoch
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
debug:
  description: Turns on debugging features.
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
default_dispvm:
  description: Default VM to be used as Disposable VM for service calls.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: default-dispvm
default_user:
  description: Default user to start applications as. TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: user
dns:
  description: DNS servers set up for this domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 10.139.1.1 10.139.1.2
gateway:
  description: Gateway for other domains that use this domain as netvm.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
gateway6:
  description: Gateway (IPv6) for other domains that use this domain as netvm.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
guivm:
  description: VM used for Gui
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: dom0
icon:
  description: Icon used for VM in Gui
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: appvm-orange
include_in_backups:
  description: If this domain is to be included in default backup.
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
installed_by_rpm:
  description: If this domain's image was installed from package tracked by package manager.
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
ip:
  description: IP address of this domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 10.137.0.29
ip6:
  description: IPv6 address of this domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
kernel:
  description: Kernel used by this domain. TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 6.12.21-1.fc37
kernelopts:
  description: Kernel command line passed to domain. TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: swiotlb=2048
keyboard_layout:
  description: Keyboard layout for this VM
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: us++
klass:
  description: Domain class name
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: AppVM
label:
  description:
    - Colourful label assigned to VM.
    - This is where the colour of the padlock is set.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  # sample: orange
mac:
  description: MAC address of the NIC emulated inside VM
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 00:16:3e:5f:6b:00
management_dispvm:
  description: Default DVM template for Disposable VM for managing this VM.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: default-mgmt-dvm
maxmem:
  description:
    - Maximum amount of memory available for this VM (for thepurpose of the memory balancer).
    - Set to 0 to disable memory balancing for this qube.
    - TemplateBasedVMs use its template's value by default (unless memory balancing not supported for this qube).
  returned: If defined, and if `defaults` is `false` or has default value
  type: int
  sample: 16000
memory:
  description: Memory currently available for this VM. TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: int
  sample: 1600
name:
  description: User-specified name of the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: workvm
netvm:
  description:
    - VM that provides network connection to this domain.
    - When None, machine is disconnected.
    - When absent, domain uses default NetVM.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: sys-firewall
provides_network:
  description: If this domain can act as network provider (formerly known as NetVM or ProxyVM)
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
qid:
  description:
    - Internal, persistent identificator of particular domain.
    - Note this is different from Xen domid.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 29
qrexec_timeout:
  description:
    - Time in seconds after which qrexec connection attempt is deemed failed.
    - Operating system inside VM should be able to boot in this time.
  returned: If defined, and if `defaults` is `false` or has default value
  type: int
  sample: 60
shutdown_timeout:
  description:
    - Time in seconds for shutdown of the VM, after which VM may be forcefully powered off.
    - Operating system inside VM should be able to fully shutdown in this time.
  returned: If defined, and if `defaults` is `false` or has default value
  type: int
  sample: 60
start_time:
  description: "Tell when machine was started. :rtype: float or None"
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
stubdom_mem:
  description: Memory amount allocated for the stubdom
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
stubdom_xid:
  description: Xen ID of stubdom
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
template:
  description: Template, on which this AppVM is based.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: fedora-41
template_for_dispvms:
  description: Should this VM be allowed to start as Disposable VM
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
updateable:
  description: True if this machine may be updated on its own.
  returned: If defined, and if `defaults` is `false` or has default value
  type: bool
uuid:
  description: UUID from libvirt.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
vcpus:
  description:
    - Number of virtual CPUs for a qube.
    - TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: int
  sample: 2
virt_mode:
  description:
    - 'Virtualisation mode: full virtualisation ("HVM"), or paravirtualisation ("PV"), or hybrid ("PVH").'
    - TemplateBasedVMs use its template's value by default.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: pvh
visible_gateway:
  description: Default gateway of this domain as seen by the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 10.138.11.27
visible_gateway6:
  description: Default (IPv6) gateway of this domain as seen by the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
visible_ip:
  description: IP address of this domain as seen by the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 10.137.0.29
visible_ip6:
  description: IPv6 address of this domain as seen by the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
visible_netmask:
  description: Netmask as seen by the domain.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: 255.255.255.255
xid:
  description: Xen ID. Or not Xen, but ID.
  returned: If defined, and if `defaults` is `false` or has default value
  type: str
  sample: -1
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bcduggan.qubes_ansible_aux.plugins.module_utils.qubes_prefs import QubesPrefs

def main():
  module = AnsibleModule(
    argument_spec=dict(
      defaults=dict(type="bool", required=False, default=False),
      name=dict(type="str", required=True)
    ),
    supports_check_mode=True
  )
  prefs = QubesPrefs(module.params["defaults"], target=module.params["name"])
  return module.exit_json(**prefs.get_properties())


if __name__ == "__main__":
  main()
