import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render = load_script('render-config')
label = load_script('rename-refind-label')
LINUX = '11111111-1111-4111-8111-111111111111'
WINDOWS = '22222222-2222-4222-8222-222222222222'


def signer_module():
    module = types.ModuleType('test_signer')
    exec(compile(render.render(LINUX, WINDOWS, 'Test Machine Secure Boot'), '<signer>', 'exec'), module.__dict__)
    return module


class Rendering(unittest.TestCase):
    def test_identifiers_and_injection_rejected(self):
        for linux, cn in [('YOUR_UUID', 'Test'), (LINUX, "Bad'\ncode"), (LINUX, '')]:
            with self.assertRaises(ValueError):
                render.render(linux, WINDOWS, cn)

    def test_render_contains_only_supplied_identity(self):
        source = render.render(LINUX, WINDOWS, 'Test Machine Secure Boot')
        self.assertNotIn('@LINUX_', source)
        self.assertIn(LINUX, source)
        self.assertIn(WINDOWS, source)
        self.assertIn('timeout 20', source)
        self.assertIn('default_selection "Windows"', source)

    def test_label_preserves_other_bytes_and_length(self):
        original = b'MZprefix' + label.OLD + b'\0\0suffix'
        changed = label.patch_image(original)
        self.assertEqual(len(changed), len(original))
        self.assertTrue(changed.startswith(b'MZprefix'))
        self.assertTrue(changed.endswith(b'\0\0suffix'))
        self.assertIn(label.NEW, changed)
        for invalid in [b'MZunknown', original + label.OLD, b'notPE' + label.OLD]:
            with self.assertRaises(ValueError):
                label.patch_image(invalid)

    def test_renderer_wont_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'existing'
            out.write_text('keep me')
            result = subprocess.run(['python3', str(ROOT/'scripts/render-config.py'),
                '--linux-esp-partuuid', LINUX, '--windows-esp-partuuid', WINDOWS,
                '--signer-cn', 'Test', '--output', str(out)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(out.read_text(), 'keep me')


class SignerGuards(unittest.TestCase):
    def test_esp_validation(self):
        s = signer_module()
        def mounts(fs='vfat', options='rw,relatime'):
            return json.dumps({'filesystems': [{'source': '/dev/test', 'fstype': fs, 'options': options}]})
        with patch.object(s.subprocess, 'check_output', side_effect=[mounts(), LINUX]):
            s.validate_esp()
        for listing, part in [(mounts('ext4'), LINUX), (mounts(options='ro'), LINUX),
                              (mounts(), WINDOWS), ('{"filesystems": []}', LINUX)]:
            with patch.object(s.subprocess, 'check_output', side_effect=[listing, part]):
                with self.assertRaises(RuntimeError):
                    s.validate_esp()

    def test_menu_keeps_native_loader_default_timer_and_both_copies(self):
        s = signer_module()
        with tempfile.TemporaryDirectory() as tmp:
            s.STATE = Path(tmp)/'state'; s.STATE.mkdir()
            s.ESP = Path(tmp)/'esp'
            entry = s.ESP/'loader/entries/Pop_OS-current.conf'
            entry.parent.mkdir(parents=True)
            kernel = s.ESP/'EFI/Pop_OS-test/vmlinuz.efi'
            kernel.parent.mkdir(parents=True)
            kernel.write_bytes(b'kernel')
            kernel.with_name('initrd.img').write_bytes(b'initrd')
            entry.write_text('linux /EFI/Pop_OS-test/vmlinuz.efi\ninitrd /EFI/Pop_OS-test/initrd.img\noptions ro quiet\n')
            for directory in ['refind', 'refind-standard']:
                (s.ESP/'EFI'/directory).mkdir()
            s.update_menu()
            config = (s.ESP/'EFI/refind/refind.conf').read_text()
            self.assertEqual(config, (s.ESP/'EFI/refind-standard/refind.conf').read_text())
            self.assertIn('timeout 20\n', config)
            self.assertIn('default_selection "Windows"', config)
            self.assertIn('loader /EFI/systemd/systemd-bootx64.efi', config)
            self.assertIn(LINUX, config)
            self.assertIn(WINDOWS, config)
            self.assertNotIn('log_level', config)
            self.assertNotIn('lockdown=', config)
            self.assertNotIn('resolution', config)

    def test_order_recursion_nochange_and_failure(self):
        s = signer_module()
        with tempfile.TemporaryDirectory() as tmp:
            s.STATE = Path(tmp)/'state'; s.STATE.mkdir()
            s.ESP = Path(tmp)/'esp'
            s.BOOT = Path(tmp)/'boot'; s.BOOT.mkdir()
            version = 'test-kernel'
            (s.BOOT / ('initrd.img-'+version)).write_bytes(b'fixture')
            image = s.ESP/'EFI/Pop_OS-test/vmlinuz.efi'
            image.parent.mkdir(parents=True); image.write_bytes(b'fixture')
            events = []
            def rebuild(args, **kwargs):
                self.assertEqual(args, ['update-initramfs', '-u', '-k', version])
                self.assertEqual(kwargs['env'][s.REBUILD_ENV], '1')
                events.append('rebuild')
                with patch.dict(s.os.environ, {s.REBUILD_ENV: '1'}):
                    s.main()
                events.append('nested-return')
            with patch.object(s.os, 'geteuid', return_value=0), patch.object(s.os, 'sync'), \
                 patch.dict(s.os.environ, {s.REBUILD_ENV: ''}), \
                 patch.object(s, 'validate_esp', side_effect=lambda: events.append('validate')), \
                 patch.object(s, 'sign_modules', return_value=[version]), \
                 patch.object(s, 'sign_efi', side_effect=lambda p: events.append(('sign', str(p)))), \
                 patch.object(s, 'run', side_effect=rebuild) as runner, \
                 patch.object(s, 'update_menu', side_effect=lambda: events.append('menu')) as menu:
                s.main()
                self.assertEqual(events.count('validate'), 1)
                self.assertIn('nested-return', events)
                self.assertLess(events.index('rebuild'), events.index(('sign', str(image))))
                self.assertLess(events.index(('sign', str(image))), events.index('menu'))
                with patch.object(s, 'sign_modules', return_value=[]):
                    runner.reset_mock(); s.main(); runner.assert_not_called()
                runner.side_effect = subprocess.CalledProcessError(1, 'update-initramfs')
                menu.reset_mock()
                with self.assertRaises(subprocess.CalledProcessError):
                    s.main()
                menu.assert_not_called()


if __name__ == '__main__':
    unittest.main()
