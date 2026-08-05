"""
==========================================================
Face3D Studio AI

MediaPipe Face Detector

Autore:
Marco Cantù

Versione:
1.0.0
==========================================================
"""

import cv2
import mediapipe as mp

from source.ai.detectors.face_detector import FaceDetector
from source.ai.models.face_detection import FaceDetection


class MediaPipeFaceDetector(FaceDetector):

    def __init__(self):

        self._face_detection = (
            mp.solutions.face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.5,
            )
        )

    # ---------------------------------------------------------

    def detect_faces(
        self,
        image_path: str,
    ) -> list[FaceDetection]:

        image = cv2.imread(image_path)

        if image is None:
            return []

        rgb = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB,
        )

        results = self._face_detection.process(rgb)

        detections = []

        if not results.detections:
            return detections

        image_height, image_width = image.shape[:2]

        for detection in results.detections:

            bbox = detection.location_data.relative_bounding_box

            x = int(bbox.xmin * image_width)
            y = int(bbox.ymin * image_height)
            w = int(bbox.width * image_width)
            h = int(bbox.height * image_height)

            detections.append(

                FaceDetection(
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    score=float(
                        detection.score[0]
                    ),
                )

            )

        return detections