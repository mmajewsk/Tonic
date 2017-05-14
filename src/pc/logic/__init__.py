from vision import StopDetector
from ai import OpencvAI
__all__ = ['AI','OpencvAI','Action', 'StopDetector']


logic_layers = {
	"stop_sign": StopDetector('cascade_xml/stop_sign.xml'),
	#"ai": OpencvAI('modelpath')
}
