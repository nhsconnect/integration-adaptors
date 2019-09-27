import pathlib
import tempfile
import unittest

from utilities import certs

_TEST_FILE_CONTENTS = 'test-file-contents'


class TestCerts(unittest.TestCase):
    def test_create_certs_files_creates_folders(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            certs.Certs.create_certs_files(temp_dir)
            self.assertTrue((pathlib.Path(temp_dir) / 'data' / 'certs').exists(), msg='data/certs folders not created')

    def test_create_certs_files_creates_private_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            returned_certs = certs.Certs.create_certs_files(temp_dir, private_key=_TEST_FILE_CONTENTS)

            expected_private_key_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'client.key'
            self.assertEqual(str(expected_private_key_filepath), returned_certs.private_key_path)
            self.assertTrue(expected_private_key_filepath.read_text(), _TEST_FILE_CONTENTS)

    def test_create_certs_files_creates_local_cert(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            returned_certs = certs.Certs.create_certs_files(temp_dir, local_cert=_TEST_FILE_CONTENTS)

            expected_local_cert_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'client.pem'
            self.assertEqual(str(expected_local_cert_filepath), returned_certs.local_cert_path)
            self.assertTrue(expected_local_cert_filepath.read_text(), _TEST_FILE_CONTENTS)

    def test_create_certs_files_creates_ca_certs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            returned_certs = certs.Certs.create_certs_files(temp_dir, ca_certs=_TEST_FILE_CONTENTS)

            expected_ca_certs_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'ca_certs.pem'
            self.assertEqual(str(expected_ca_certs_filepath), returned_certs.ca_certs_path)
            self.assertTrue(expected_ca_certs_filepath.read_text(), _TEST_FILE_CONTENTS)

    def test_create_certs_files_creates_multiple_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file_contents_1 = 'test-file-contents1'
            test_file_contents_2 = 'test-file-contents2'
            test_file_contents_3 = 'test-file-contents3'

            returned_certs = certs.Certs.create_certs_files(temp_dir, private_key=test_file_contents_1,
                                                            local_cert=test_file_contents_2,
                                                            ca_certs=test_file_contents_3)

            expected_private_key_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'client.key'
            self.assertEqual(str(expected_private_key_filepath), returned_certs.private_key_path)
            self.assertTrue(expected_private_key_filepath.read_text(), test_file_contents_1)

            expected_local_cert_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'client.pem'
            self.assertEqual(str(expected_local_cert_filepath), returned_certs.local_cert_path)
            self.assertTrue(expected_local_cert_filepath.read_text(), test_file_contents_2)

            expected_ca_certs_filepath = pathlib.Path(temp_dir) / 'data' / 'certs' / 'ca_certs.pem'
            self.assertEqual(str(expected_ca_certs_filepath), returned_certs.ca_certs_path)
            self.assertTrue(expected_ca_certs_filepath.read_text(), test_file_contents_3)
