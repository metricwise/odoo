import platform
import unittest

from odoo.modules.module import get_module_resource
from odoo.tests import BaseCase
from odoo.tools.config import configmanager


class TestConfigManager(BaseCase):
    def test_defaults(self):
        config = configmanager()
        self.assertEqual(config['limit_memory_hard'], 2684354560)
        self.assertEqual(config['limit_memory_soft'], 2147483648)

    def test_limit_memory_old(self):
        config = configmanager(fname=get_module_resource('base', 'tests', 'data', 'limit_memory_old.conf'))
        self.assertEqual(config['limit_memory_hard'], 4294967296)
        self.assertEqual(config['limit_memory_soft'], 1073741824)

    IS_POSIX = platform.system() == 'Linux' and platform.machine() == 'x86_64'
    @unittest.skipIf(not IS_POSIX, 'this test is POSIX only')
    def test_04_parse_size(self):
        config = configmanager(fname=get_module_resource('base', 'tests', 'config', 'limit_memory.conf'))
        self.assertEqual(config['limit_memory_hard'], 3221225472)
        self.assertEqual(config['limit_memory_soft'], 1610612736)

        config._parse_config(['--limit-memory-hard', '4GiB', '--limit-memory-soft', '3GiB'])
        self.assertEqual(config['limit_memory_hard'], 4294967296)
        self.assertEqual(config['limit_memory_soft'], 3221225472)

        config = configmanager()
        self.assertEqual(config._parse_size('1024'), 1024)
        self.assertEqual(config._parse_size('2ki '), 2048)
        self.assertEqual(config._parse_size(' 4MiB'), 4194304)
        self.assertEqual(config._parse_size('1 YiB'), 1208925819614629174706176)

        with self.assertRaises(ValueError) as cm:
            config._parse_size('1.2465')
        self.assertIn("invalid size", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            config._parse_size('B')
        self.assertIn("invalid size", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            config._parse_size('10kB')
        self.assertIn("invalid IEC 80000-13 binary prefix", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            config._parse_size('20fiB')
        self.assertIn("invalid IEC 80000-13 binary prefix", str(cm.exception))
