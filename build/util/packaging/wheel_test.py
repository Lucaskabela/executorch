import sys
import os
import argparse
import subprocess

_PYTHON_PATH = os.getenv("PYTHONPATH")
if _PYTHON_PATH is None:
  print("PYTHONPATH is not set")
  exit(1)

# Since the .ci folder starts with a period, it is not possible to import it
# directly, so we must use the importlib module to load it.
sys.path.append(os.path.join(_PYTHON_PATH, ".ci"))
from scripts import gather_test_models


def _create_arg_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser()

  parser.add_argument(
      "--target-os",
      type=str,
      required=True,
      choices=gather_test_models.DEFAULT_RUNNERS.keys(),
      help="the target OS",
  )

  return parser

def _run_test(model_name: str, build_tool: str, backend: str) -> None:
  subprocess.run(
      [
        os.path.join(_PYTHON_PATH, ".ci/scripts/test_model.sh"), 
        model_name, 
        build_tool, 
        backend,
      ],
      check=True,
  )

if __name__ == "__main__":
  args = _create_arg_parser().parse_args()
  models = gather_test_models.export_models_for_ci(
    target_os = args.target_os,
    # Event refers to the type of models that will be downloaded. "pull_request"
    # uses higher priority and fast models.
    event="pull_request",
  ).get("include", [])

  if len(models) == 0:
    print("No models found")
    exit(1)

  for model in models:
    _run_test(
      model_name=model["model"],
      build_tool=model["build-tool"],
      backend=model["backend"],
    )
