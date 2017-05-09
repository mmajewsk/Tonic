import cv2
import numpy as np

stop_cascade = cv2.CascadeClassifier('cascade_xml/stop_sign.xml')

def detect_stop(frame):
	gray = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2GRAY)
	v = 0
	threshold = 150
	cascade_obj = stop_cascade.detectMultiScale(
		gray,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(20, 20),
		flags=0
	)
	for (x_pos, y_pos, width, height) in cascade_obj:
		cv2.rectangle(frame, (x_pos + 5, y_pos + 5), (x_pos + width - 5, y_pos + height - 5), (255, 255, 255), 2)
		v = y_pos + height - 5
		# print(x_pos+5, y_pos+5, x_pos+width-5, y_pos+height-5, width, height)
		cv2.putText(frame, 'STOP', (x_pos, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	return frame

vision_layers = {
	"stop_sign": detect_stop,
}
