"""Offline contracts for host selection; no test calls a model."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("trigger_eval_under_test", HERE / "trigger_eval.py")
trigger = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(trigger)


def result(text, exit_code=0):
    return {"text": text, "exit": exit_code, "stderr": "", "seconds": 0}


class TriggerEvalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Every test is offline, including accidental calls through either alias.
        self.cli = mock.patch.object(trigger.shutil, "which", return_value="/fake/claude").start()
        self.run = mock.patch.object(trigger, "run_claude", return_value=result("SKILL: none")).start()
        mock.patch.object(trigger._runner.subprocess, "run", side_effect=AssertionError("real CLI forbidden in tests")).start()
        self.addCleanup(mock.patch.stopall)

    def skill(self, text):
        path = self.root / "chosen-SKILL.md"
        path.write_text(text, encoding="utf-8")
        return path

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return trigger.main(list(args))

    def test_parse_exact_first_line(self):
        self.assertEqual(trigger.parse_selection("SKILL: prompt-optimizer\nExplanation"), "invoke")
        self.assertEqual(trigger.parse_selection("SKILL: none\r\nAnswer"), "direct")

    def test_parse_rejects_missing_or_nonfirst_marker(self):
        for text in ("", "\nSKILL: none", "Explanation\nSKILL: none", "```\nSKILL: none\n```",
                     "SKILL: other", "skill: none", "SKILL: none extra", " SKILL: none", "SKILL: none "):
            with self.subTest(text=text):
                self.assertIsNone(trigger.parse_selection(text))

    def test_compare_expected_and_exit(self):
        for expected in ("invoke", "direct"):
            case = {"lang": "en", "expected": expected}
            for text, parsed in (("SKILL: prompt-optimizer", "invoke"), ("SKILL: none", "direct"), ("oops", None)):
                for code in (0, 1, 127, None):
                    with self.subTest(expected=expected, text=text, exit=code):
                        row = trigger.score_result(case, result(text, code), self.root / "raw.txt")
                        self.assertEqual(row["parsed"], parsed)
                        self.assertEqual(row["matches"], parsed == expected and code == 0)
                        self.assertEqual(row["exit"], code)

    def test_summary_keeps_failures_in_denominator(self):
        rows = {}
        for i, (expected, text, code) in enumerate([
            ("invoke", "SKILL: prompt-optimizer", 0), ("invoke", "bad", 0),
            ("direct", "SKILL: none", 0), ("direct", "SKILL: prompt-optimizer", 0),
            ("direct", "SKILL: none", 1),
        ]):
            rows[str(i)] = trigger.score_result({"lang": "en", "expected": expected}, result(text, code), "raw.txt")
        summary = trigger.summarize(rows)
        self.assertEqual(summary["invoke_recall"], {"correct": 1, "total": 2, "rate": 0.5})
        self.assertEqual(summary["direct_accuracy"], {"correct": 1, "total": 3, "rate": 1 / 3})
        self.assertEqual(summary["parse_failures"], 1)
        self.assertEqual(summary["exit_failures"], 1)
        self.assertEqual(summary["passed"], 2)

    def test_empty_summary_is_not_perfect_accuracy(self):
        summary = trigger.summarize({})
        self.assertIsNone(summary["invoke_recall"]["rate"])
        self.assertIsNone(summary["direct_accuracy"]["rate"])
        self.assertEqual(summary["parse_failures"], 0)

    def test_output_allows_absent_and_empty_directory(self):
        out = self.root / "new" / "exam"
        self.assertEqual(trigger.prepare_output(out), out.resolve())
        self.assertEqual(trigger.prepare_output(out), out.resolve())

    def test_output_rejects_existing_content_file_and_symlink(self):
        out = self.root / "occupied"
        out.mkdir()
        sentinel = out / ".existing"
        sentinel.write_text("keep", encoding="utf-8")
        link = self.root / "link"
        link.symlink_to(out, target_is_directory=True)
        broken = self.root / "broken"
        broken.symlink_to(self.root / "absent")
        for path in (out, sentinel, link, broken):
            with self.subTest(path=path), self.assertRaises(ValueError):
                trigger.prepare_output(path)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_description_comes_from_selected_frontmatter(self):
        skill = self.skill("---\nname: prompt-optimizer\ndescription: >\n  Unique routing description.\n  Second line.\nmetadata:\n  version: 'test'\n---\nBODY MUST NOT APPEAR\ndescription: wrong\n")
        description = trigger.read_description(skill)
        self.assertEqual(description, "Unique routing description. Second line.")
        prompt = trigger.host_prompt(description)
        self.assertIn(description, prompt)
        self.assertNotIn("BODY MUST NOT APPEAR", prompt)
        self.assertNotIn("metadata", prompt)
        self.assertIn("fictional-orbit-catalog", prompt)
        self.assertIn("fictional-quilt-index", prompt)

    def test_description_supported_scalar_formats(self):
        for scalar, expected in [
            ("plain description", "plain description"), ('"A quoted description"', "A quoted description"),
            ("'It''s a skill'", "It's a skill"), ("|-\n  First\n  Second", "First\nSecond"),
            (">-\n  First\n  Second", "First Second"),
        ]:
            with self.subTest(scalar=scalar):
                self.assertEqual(trigger.read_description(self.skill("---\ndescription: " + scalar + "\n---\n")), expected)

    def test_description_rejects_missing_empty_or_duplicate(self):
        for text in ("description: outside", "---\ndescription: text", "---\nname: skill\n---\n",
                     "---\ndescription: >\nmetadata: x\n---\n", "---\ndescription: x\ndescription: y\n---\n",
                     "---\ndescription: [x]\n---\n", '---\ndescription: ""\n---\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                trigger.read_description(self.skill(text))

    def test_real_description_and_reused_cli_contract(self):
        self.assertIn("On-demand automatic use:", trigger.read_description(trigger.SKILL))
        self.assertIs(trigger.CLI_FLAGS, trigger._runner.CLI_FLAGS)
        # mock original retained by patch; the wrapper is the actual reused function.
        self.assertEqual(trigger._runner.run_claude.__code__.co_filename, str(HERE / "run_eval.py"))

    def test_dataset_shape_balance_and_no_existing_duplicates(self):
        cases = trigger.select_cases("all", "")
        self.assertEqual(len(cases), 20)
        old_inputs = []
        for path in HERE.glob("cases*.json"):
            for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
                old_inputs.append(case["optimizer_input"])
                if (case.get("effect") or {}).get("task"):
                    old_inputs.append(case["effect"]["task"])
        for lang in ("zh", "en"):
            group = [c for c in cases if c["lang"] == lang]
            self.assertEqual(len(group), 10)
            self.assertEqual(sum(c["expected"] == "invoke" for c in group), 5)
        for case in cases:
            self.assertEqual(set(case), {"id", "lang", "user_message", "expected", "reason"})
            self.assertNotIn(case["user_message"], old_inputs)

    def test_ids_and_language_filter(self):
        self.assertEqual([c["id"] for c in trigger.select_cases("en", " TE02,TE01 ")], ["TE01", "TE02"])
        for lang, ids in (("en", "TZ01"), ("all", "missing"), ("zh", ",")):
            with self.subTest(lang=lang, ids=ids), self.assertRaises(ValueError):
                trigger.select_cases(lang, ids)

    def test_stub_run_writes_raw_results_summary_and_selected_description(self):
        skill = self.skill("---\ndescription: 'CUSTOM DESCRIPTION'\n---\nsecret body\n")
        out = self.root / "results"
        replies = {"TZ01": "SKILL: none\nA direct answer", "TZ08": "SKILL: prompt-optimizer"}
        messages = {c["user_message"]: c["id"] for c in trigger.select_cases("zh", "TZ01,TZ08")}
        def fake(prompt, system_file, model, timeout):
            self.assertEqual(model, "chosen-model")
            self.assertEqual(timeout, 17)
            system = Path(system_file).read_text(encoding="utf-8")
            self.assertIn("CUSTOM DESCRIPTION", system)
            self.assertNotIn("secret body", system)
            return result(replies[messages[prompt]])
        self.run.side_effect = fake
        self.assertEqual(self.invoke("--out", str(out), "--skill", str(skill), "--model", "chosen-model",
                                     "--lang", "zh", "--ids", "TZ01,TZ08", "--workers", "2", "--timeout", "17"), 0)
        manifest = json.loads((out / "trigger_manifest.json").read_text())
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["summary"]["passed"], 2)
        self.assertEqual(self.run.call_count, 2)
        for cid, row in manifest["cases"].items():
            self.assertEqual(Path(row["output_path"]).read_text(), replies[cid])
            self.assertTrue(row["matches"])
            self.assertEqual(row["exit"], 0)

    def test_stub_run_parse_failure_and_bad_exit_never_pass(self):
        for reply in (result("invalid\nSKILL: none"), result("SKILL: none", 1), result("", None)):
            with self.subTest(reply=reply), tempfile.TemporaryDirectory(dir=self.root) as directory:
                self.run.return_value = reply
                self.assertEqual(self.invoke("--out", directory, "--ids", "TE01", "--workers", "1"), 1)
                manifest = json.loads((Path(directory) / "trigger_manifest.json").read_text())
                self.assertFalse(manifest["cases"]["TE01"]["matches"])
                self.assertEqual(manifest["summary"]["direct_accuracy"]["rate"], 0)

    def test_no_cli_errors_before_creating_output_or_calling_model(self):
        self.cli.return_value = None
        out = self.root / "missing-cli"
        with self.assertRaises(SystemExit) as raised:
            self.invoke("--out", str(out))
        self.assertEqual(raised.exception.code, 2)
        self.assertFalse(out.exists())
        self.run.assert_not_called()

    def test_nonempty_output_errors_before_model_call(self):
        sentinel = self.root / "keep.txt"
        sentinel.write_text("keep")
        with self.assertRaises(SystemExit) as raised:
            self.invoke("--out", str(self.root))
        self.assertEqual(raised.exception.code, 2)
        self.run.assert_not_called()
        self.assertEqual(sentinel.read_text(), "keep")

    def test_invalid_parameters_do_not_call_model(self):
        for extra in (("--workers", "0"), ("--timeout", "-1"), ("--lang", "fr"), ("--ids", "unknown")):
            with self.subTest(extra=extra), self.assertRaises(SystemExit):
                self.invoke("--out", str(self.root / "bad"), *extra)
        self.run.assert_not_called()
        self.assertFalse((self.root / "bad").exists())

    def test_defaults(self):
        out = self.root / "defaults"
        self.assertEqual(self.invoke("--out", str(out), "--ids", "TE01"), 0)
        call = self.run.call_args.args
        self.assertEqual(call[2:], ("sonnet", 600))
        manifest = json.loads((out / "trigger_manifest.json").read_text())
        self.assertEqual(manifest["lang"], "all")
        self.assertEqual(manifest["skill"], str(trigger.SKILL))


if __name__ == "__main__":
    unittest.main()
