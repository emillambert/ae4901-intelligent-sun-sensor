import sys
import json
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/'runtime'/'pc'
sys.path.insert(0,str(P))
from host import SunSensor, make_packet,parse_packet,synthetic_demo

CFG=json.loads((P/'calibration_PLACEHOLDER.json').read_text())

class RuntimeTests(unittest.TestCase):
    def test_checksum_roundtrip(self):
        p=parse_packet(make_packet(0,[100,200,300,400,500,600]))
        self.assertEqual(p['adc'][0],100)
    def test_checksum_rejects_corruption(self):
        p=make_packet(0,[100,200,300,400,500,600]).replace('100,','101,',1)
        self.assertIsNone(parse_packet(p))
    def test_bad_channel_range(self):
        self.assertIsNone(parse_packet(make_packet(0,[1024,200,300,400,500,600])))
    def test_missing_boards(self):
        self.assertEqual(SunSensor(CFG).estimate()['status'],'INSUFFICIENT_DATA')
    def test_demo_is_not_falsely_control_valid(self):
        d=synthetic_demo(CFG)
        self.assertIsNotNone(d['estimated']['vector'])
        self.assertFalse(d['estimated']['valid_for_control'])
    def test_demo_direction(self):
        import numpy as np
        d=synthetic_demo(CFG)
        a=np.array(d['true_sun']);b=np.array(d['estimated']['vector'])
        angle=np.degrees(np.arccos(np.clip(a@b, -1,1)))
        self.assertLess(angle,8.0)
    def test_one_board_stale(self):
        p=parse_packet(make_packet(0,[500,300,400,600,500,320]))
        m=SunSensor(CFG);m.ingest(p)
        self.assertEqual(m.estimate()['boards_online'],[0])
    def test_sequence_reject_duplicate(self):
        p=parse_packet(make_packet(0,[500,300,400,600,500,320],seq=3))
        m=SunSensor(CFG);self.assertTrue(m.ingest(p))
        self.assertFalse(m.ingest(p))

if __name__=='__main__':unittest.main()
