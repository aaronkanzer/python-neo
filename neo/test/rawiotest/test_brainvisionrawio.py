""" """

import tempfile
import unittest
from pathlib import Path

import numpy as np

from neo.rawio.brainvisionrawio import BrainVisionRawIO

from neo.test.rawiotest.common_rawio_test import BaseTestRawIO


class TestBrainVisionRawIO(
    BaseTestRawIO,
    unittest.TestCase,
):
    rawioclass = BrainVisionRawIO
    entities_to_test = [
        "brainvision/File_brainvision_1.vhdr",
        "brainvision/File_brainvision_2.vhdr",
        "brainvision/File_brainvision_3_float32.vhdr",
        "brainvision/File_brainvision_3_int16.vhdr",
        "brainvision/File_brainvision_3_int32.vhdr",
        "brainvision/File_brainvision_4_float32.vhdr",
    ]

    entities_to_download = ["brainvision"]

    def test_marker_positions_are_one_based(self):
        # SegmentDataPoints=294 in the .vhdr and a "New Segment" marker on the first sample of each of the 34 segments
        reader = BrainVisionRawIO(self.get_local_path("brainvision/File_brainvision_3_int16.vhdr"))
        reader.parse_header()
        event_names = list(reader.header["event_channels"]["name"])
        timestamps, _, _ = reader.get_event_timestamps(event_channel_index=event_names.index("New Segment"))
        np.testing.assert_array_equal(timestamps, np.arange(34) * 294)


class TestBrainVisionRawIOChannelInfos(unittest.TestCase):
    def test_omitted_resolution_and_unit_use_defaults(self):
        vhdr = (
            "Brain Vision Data Exchange Header File Version 1.0\n"
            "[Common Infos]\n"
            "Codepage=UTF-8\n"
            "DataFile=test.eeg\n"
            "MarkerFile=test.vmrk\n"
            "DataFormat=BINARY\n"
            "DataOrientation=MULTIPLEXED\n"
            "NumberOfChannels=4\n"
            "SamplingInterval=1000\n"
            "[Binary Infos]\n"
            "BinaryFormat=INT_16\n"
            "[Channel Infos]\n"
            # no unit field
            "Ch1=A,,0.5\n"
            # empty resolution field
            "Ch2=B,,,µV\n"
            # empty unit field
            "Ch3=C,,0.1,\n"
            # extra fields after the unit
            "Ch4=D,,2,mV,extra\n"
        )
        vmrk = "Brain Vision Data Exchange Marker File, Version 1.0\n[Marker Infos]\nMk1=New Segment,,1,1,0\n"
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            (tmp_dir / "test.vhdr").write_text(vhdr, encoding="utf8")
            (tmp_dir / "test.vmrk").write_text(vmrk, encoding="utf8")
            np.arange(40, dtype="int16").tofile(tmp_dir / "test.eeg")

            reader = BrainVisionRawIO(filename=tmp_dir / "test.vhdr")
            reader.parse_header()
            channels = reader.header["signal_channels"]
            np.testing.assert_array_equal(channels["units"], ["uV", "uV", "uV", "mV"])
            np.testing.assert_allclose(channels["gain"], [0.5, 1.0, 0.1, 2.0])


if __name__ == "__main__":
    unittest.main()
