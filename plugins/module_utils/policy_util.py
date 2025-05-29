import pathlib
import functools
from typing import Tuple, List, Dict
from qrexec.policy.admin_client import PolicyClient
import qrexec.tools.qubes_policy_lint as linter
import qrexec.tools.qubes_policy_editor as editor
from ansible_collections.bcduggan.qubes_ansible_aux.plugins.module_utils.tool_context import ToolContext, ToolContextError

class PolicyUtilError(Exception):
  def __nit__(self, message):
    super().__init__(message)

def client_tool(func, *args, **kwargs):
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    try:
      with ToolContext():
        value = func(*args, **kwargs)
    except ToolContextError as exc:
      raise PolicyUtilError(f"Error during client method '{func.__name__}'") from exc
    return value
  return wrapper

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

  def _client_method(self, method_name, *args, **kwargs):
    function_name = (
      "policy_include_"+method_name
      if self.is_include
      else "policy_"+method_name
    )
    method = getattr(self.client, function_name)
    return method(*args, **kwargs)

  @client_tool
  def get(self) -> Tuple[str, str]:
    return self._client_method("get", self.name)

  @client_tool
  def remove(self) -> None:
    return self._client_method("remove", self.name)
  
  @client_tool
  def replace(self, content: str, token: str):
    return self._client_method("replace", self.name, content, token)

  @client_tool
  def list(self) -> List[str]:
    return self._client_method("list")

