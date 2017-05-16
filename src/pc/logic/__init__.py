from logic.vision import StopDetector
from logic.AI import OpencvAI, AI
from logic.action import Action

__all__ = ['AI','OpencvAI','Action', 'StopDetector']


logic_layers = {
	"stop_sign": StopDetector('cascade_xml/stop_sign.xml'),
	#"ai": OpencvAI('modelpath')
}
