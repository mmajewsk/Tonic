from logic.vision import StopDetector, SignalPainter
from logic.AI import OpencvAI, AI
from logic.action import Action
from clients import QTSteeringClient
from logic.imu_processing import ImuKeeper, Imu

import os
from logic.mapper import Mapper

logic_layers = {
	#"stop_sign": StopDetector('cascade_xml/stop_sign.xml'),
	#"ai": OpencvAI(r"C:\Users\hawker\Dropbox\Public\data_intake\ann.xml"),
	"signal_painter": SignalPainter(
		video_size=(640, 480),
		draw_border=5,
		letters=QTSteeringClient.wsad_int,
	)
}

__all__ = ['StopDetector', 'SignalPainter', 'OpencvAI',
		   'AI','Action',  'logic_layers','ImuKeeper','Imu',
		   'ahrs', 'Mapper']

