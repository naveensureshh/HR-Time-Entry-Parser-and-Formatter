import os
import ast
import types
from pathlib import Path

import pandas as pd


def _load_process_timesheet():
    """Load only the `process_timesheet` function from the script without running its main code."""
    src = Path("graph_timesheet_processor.py").read_text()
    tree = ast.parse(src)
    nodes = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "pandas":
                    nodes.append(node)
        if isinstance(node, ast.FunctionDef) and node.name == "process_timesheet":
            nodes.append(node)
            break
    module = types.ModuleType("_processor")
    exec(compile(ast.Module(nodes, []), filename="_processor", mode="exec"), module.__dict__)
    return module.process_timesheet


def test_process_timesheet(tmp_path):
    process_timesheet = _load_process_timesheet()

    ref = pd.DataFrame({"Name": ["Alice"], "StartTime": [pd.Timestamp("2023-01-01 09:00")]})
    ts = pd.DataFrame({"Name": ["Alice"], "ClockIn": [pd.Timestamp("2023-01-01 09:05")]})

    ref_file = tmp_path / "reference.csv"
    ts_file = tmp_path / "timesheet.xlsx"
    ref.to_csv(ref_file, index=False)
    ts.to_excel(ts_file, index=False)

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        process_timesheet(ts_file, ref_file)
    finally:
        os.chdir(cwd)

    result = pd.read_csv(tmp_path / "lateness_report.csv")
    assert result["Late"].iloc[0] is True
