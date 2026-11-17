"""Read-only SQL execution worker, matching official sql_server._execute_sql_direct output strings.

Usage: python -m info_seeking.sql_worker <database_path>   (query on stdin)
       python -m info_seeking.sql_worker --verify <external_root> <database_path> <submission_file> <ground_truth_file>
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def execute_direct(database_path: str, query: str, max_rows: int = 200) -> str:
    import pandas as pd
    try:
        with sqlite3.connect(f'file:{database_path}?mode=ro', uri=True) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                if cursor.description is not None:
                    columns = [description[0] for description in cursor.description]
                    data = cursor.fetchall()
                    df = pd.DataFrame(data, columns=columns)
                    if df.empty:
                        return 'Query executed successfully. No results returned.'
                    if len(df) > max_rows:
                        df = df.head(max_rows)
                        return (f'Query executed successfully. Result truncated to the first {max_rows} rows:\n'
                                f'{df.to_csv(index=False)}')
                    return f'Query executed successfully:\n{df.to_csv(index=False)}'
                return 'Error: non-SELECT query'
            except sqlite3.OperationalError as e:
                if 'attempt to write a readonly database' in str(e).lower():
                    return 'Error: non-SELECT query'
                return f'Error: {e}'
            except Exception as e:
                return f'Error: {e}'
    except Exception as e:
        return f'Error executing query: {e}'


def verify(external_root: str, database_path: str, submission: str, ground_truth: str) -> dict:
    """Official test_verify semantics: run both queries read-only, compare with compare_pandas_outputs."""
    from info_seeking.official import OfficialFiles
    official = OfficialFiles(external_root).verifier
    if not submission.strip():
        return {'solve': 0, 'submission_error': 'Error: empty query', 'ground_truth_error': None}
    sub_err, sub_df = official.execute_sql(database_path, submission)
    gt_err, gt_df = official.execute_sql(database_path, ground_truth)
    solve = 0 if sub_df is None or gt_df is None else int(official.compare_pandas_outputs(gt_df, sub_df))
    return {'solve': solve, 'submission_error': sub_err, 'ground_truth_error': gt_err}


if __name__ == '__main__':
    if len(sys.argv) == 6 and sys.argv[1] == '--verify':
        _, _, root, db, sub_file, gt_file = sys.argv
        print(json.dumps(verify(root, db, Path(sub_file).read_text(), Path(gt_file).read_text())))
    elif len(sys.argv) == 2:
        print(execute_direct(sys.argv[1], sys.stdin.read()), end='')
    else:
        raise SystemExit(__doc__)
