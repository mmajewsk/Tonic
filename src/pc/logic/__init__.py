from logic.vision import StopDetector, SignalPainter
from logic.AI import OpencvAI, AI
from logic.action import Action
from clients import SteeringClient

logic_layers = {
	"stop_sign": StopDetector('cascade_xml/stop_sign.xml'),
	#"ai": OpencvAI('modelpath'),
	"signal_painter": SignalPainter(
		video_size=(320, 240),
		draw_border=5,
		letters=SteeringClient.wsad_int,
	)
}

__all__ = ['StopDetector', 'SignalPainter', 'OpencvAI',
		   'AI','Action',  'logic_layers']

