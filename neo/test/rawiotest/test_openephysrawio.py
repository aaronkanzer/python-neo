import unittest

from neo.rawio.openephysrawio import OpenEphysRawIO
from neo.test.rawiotest.common_rawio_test import BaseTestRawIO


class TestOpenEphysRawIO(
    BaseTestRawIO,
    unittest.TestCase,
):
    rawioclass = OpenEphysRawIO
    entities_to_download = ["openephys"]
    entities_to_test = [
        "openephys/OpenEphys_SampleData_1",
        # this file has gaps and this is now handle corretly
        "openephys/OpenEphys_SampleData_2_(multiple_starts)",
        # 'openephys/OpenEphys_SampleData_3',
        # two nodes with the new naming convention for openephys
        "openephys/openephys_rhythmdata_test_nodes/Record Node 120",
        "openephys/openephys_rhythmdata_test_nodes/Record Node 121",
    ]

    def test_raise_error_if_strange_timestamps(self):
        # In this dataset CH32 have strange timestamps
        reader = OpenEphysRawIO(dirname=self.get_local_path("openephys/OpenEphys_SampleData_3"))
        with self.assertRaises(Exception):
            reader.parse_header()

    def test_channel_order(self):
        reader = OpenEphysRawIO(dirname=self.get_local_path("openephys/OpenEphys_SampleData_1"))
        reader.parse_header()
        reader.header["signal_channels"]["name"][0].startswith("CH")

    def test_spike_count(self):
        # STp106.0n0.spikes holds 454 spikes, all with sorted_id 0
        reader = OpenEphysRawIO(dirname=self.get_local_path("openephys/OpenEphys_SampleData_1"))
        reader.parse_header()
        assert reader.spike_count(block_index=0, seg_index=0, spike_channel_index=0) == 454
        spike_timestamps = reader.get_spike_timestamps(block_index=0, seg_index=0, spike_channel_index=0)
        assert spike_timestamps.size == 454
        assert spike_timestamps[0] == 52218


if __name__ == "__main__":
    unittest.main()
