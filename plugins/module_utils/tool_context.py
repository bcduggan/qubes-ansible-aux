import sys
import io
from subprocess import CalledProcessError

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
    elif exc_type is CalledProcessError:
      raise ToolContextError(exc_value.output.decode().rstrip())
    return False
