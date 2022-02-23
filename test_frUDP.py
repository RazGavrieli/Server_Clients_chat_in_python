from unittest import TestCase
import frUDP

class Test(TestCase):
    def test_md5_checksum(self):
        string_data_1 = "test data"
        string_data_2 = "Test data"

        bytes_data_1 = bytes(string_data_1.encode())
        bytes_data_2 = bytes(string_data_2.encode())
        self.assertNotEqual(frUDP.md5_checksum(bytes_data_2), frUDP.md5_checksum(bytes_data_1))
        self.assertNotEqual(frUDP.md5_checksum(string_data_2), frUDP.md5_checksum(string_data_1))
        self.assertEqual(frUDP.md5_checksum(string_data_2.lower()), frUDP.md5_checksum(string_data_1))

    def test_wrap_unwrap(self): # wrap strings
        string_data = "test data"
        id = 35
        wrapped_data = frUDP.wrap(string_data, id)
        _, unwrapped_id, unwrapped_data = frUDP.unwrap(wrapped_data)
        self.assertEqual(id, int(unwrapped_id))
        self.assertEqual(string_data, unwrapped_data)

    def test_wrap_unwrap_payload(self): # wrap bytes data ordered in a dictionary
        bytes_data = {'0': b"test", '1': b"data"}
        wrapped_data = frUDP.wrap_payload(bytes_data)
        _, unwrapped_data = frUDP.unwrap_payload(wrapped_data)
        self.assertEqual(bytes_data, unwrapped_data)
