"""The PS5 builder's window has a line for every step of the pipeline: ps5/builder/app.py's ABOUT names each of STEPS.

The window shows ABOUT[n] beside the step under way. #47 added step 6 (Listing the game's shaders) to STEPS without an ABOUT
line, so the window's slot raised KeyError at step 6 (under PyQt6 an exception in a slot ends the program). Read from the
source with ast: no Qt needed.

python -I -B tests/test_builder_steps.py
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def constant(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("FAIL: ps5/builder/app.py has no %s" % name)


def main():
    tree = ast.parse((ROOT / "ps5" / "builder" / "app.py").read_text(encoding="utf-8"))
    steps, about = constant(tree, "STEPS"), constant(tree, "ABOUT")
    missing = [n for n in range(1, len(steps) + 1) if n not in about]
    if missing:
        raise SystemExit("FAIL: ps5/builder/app.py ABOUT has no line for step(s) %s (%s)" %
                         (", ".join(map(str, missing)), ", ".join(steps[n - 1] for n in missing)))
    pipeline = (ROOT / "ps5" / "builder" / "pipeline.py").read_text(encoding="utf-8")
    if "STEPS = " in pipeline and constant(ast.parse(pipeline), "STEPS") != steps:
        raise SystemExit("FAIL: ps5/builder/app.py's STEPS are not pipeline.py's")
    print("PASS: the builder's window has a line for each of its %d steps" % len(steps))


if __name__ == "__main__":
    main()
