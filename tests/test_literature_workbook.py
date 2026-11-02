"""Reading-workbook migration and user-edit preservation."""
import importlib.util
import shutil
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('literature_export', ROOT / 'scripts/export_literature_workbook.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class WorkbookSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.previous_docs = module.DOCS
        module.DOCS = self.directory / 'papers'
        module.DOCS.mkdir()
        for name in ('citation_screening_shortlist.csv', 'literature_reading.csv'):
            shutil.copy2(self.previous_docs / name, module.DOCS / name)
        shutil.copytree(self.previous_docs / 'citation_screening_sources', module.DOCS / 'citation_screening_sources')
        self.output = self.directory / 'reading.xlsx'
        module.export(self.output)

    def tearDown(self):
        module.DOCS = self.previous_docs
        self.temp.cleanup()

    def test_sorted_user_notes_and_blank_edits_round_trip(self):
        book = load_workbook(BytesIO(self.output.read_bytes()))
        sheet = book['Papers']
        rows = list(sheet.iter_rows(min_row=2, values_only=True))
        sheet.delete_rows(2, 32)
        for row in reversed(rows):
            sheet.append(row)
        for row in sheet:
            if row[0].value == 3:
                row[7].value = '用户原文\n方法与想法'
                row[6].value = None
                row[12].value = '已读'
        book.save(self.output)
        module.import_workbook(self.output)
        module.export(self.output)
        records = {v['ID']: v for _, v in module.records()}
        self.assertEqual(records[3]['Additional think'], '用户原文\n方法与想法')
        self.assertEqual(records[3]['Limitation'], '')
        book = load_workbook(BytesIO(self.output.read_bytes()))
        row = next(r for r in book['Papers'].iter_rows(values_only=True) if r[0] == 3)
        self.assertEqual(row[12], '已读')
        self.assertTrue(self.output.with_name('reading.backup.xlsx').exists())

    def test_only_latest_preupdate_backup_is_retained(self):
        legacy = self.directory / 'reading.backup-20260101.xlsx'
        legacy.write_bytes(self.output.read_bytes())
        for text in ('first manual edit', 'second manual edit'):
            book = load_workbook(BytesIO(self.output.read_bytes()))
            book['Papers'].cell(2, 8, text)
            book.save(self.output)
            before = self.output.read_bytes()
            module.export(self.output)
            backup = self.directory / 'reading.backup.xlsx'
            self.assertEqual(backup.read_bytes(), before)
            self.assertEqual(list(self.directory.glob('reading.backup*.xlsx')), [backup])

    def test_old_schema_adds_future_work_without_losing_notes(self):
        book = load_workbook(BytesIO(self.output.read_bytes()))
        sheet = book['Papers']
        sheet.delete_cols(15)
        sheet.cell(4, 8, '手改笔记必须保留')
        book.save(self.output)
        module.export(self.output)
        book = load_workbook(BytesIO(self.output.read_bytes()))
        self.assertEqual(book['Papers'].cell(1, 15).value, 'Future work')
        self.assertEqual(book['Papers'].cell(4, 8).value, '手改笔记必须保留')
        self.assertEqual(len(book['Papers'].tables['LiteratureTable'].tableColumns), 15)

    def test_lock_and_unknown_id_stop_before_csv_changes(self):
        before = (module.DOCS / 'literature_reading.csv').read_bytes()
        lock = self.output.with_name('~$' + self.output.name)
        lock.touch()
        with self.assertRaises(SystemExit):
            module.import_workbook(self.output)
        with self.assertRaises(SystemExit):
            module.export(self.output)
        lock.unlink()
        book = load_workbook(BytesIO(self.output.read_bytes()))
        book['Papers'].cell(2, 1, 999)
        book.save(self.output)
        with self.assertRaises(SystemExit):
            module.import_workbook(self.output)
        self.assertEqual((module.DOCS / 'literature_reading.csv').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
