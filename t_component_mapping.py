warning: in the working copy of 'source/models/landmarks/standard_landmarks.py', CRLF will be replaced by LF the next time Git touches it
[1mdiff --git a/source/models/landmarks/standard_landmarks.py b/source/models/landmarks/standard_landmarks.py[m
[1mindex 883b8df..d1917d2 100644[m
[1m--- a/source/models/landmarks/standard_landmarks.py[m
[1m+++ b/source/models/landmarks/standard_landmarks.py[m
[36m@@ -86,17 +86,17 @@[m [mdef create_standard_landmarks() -> list[LandmarkDefinition]:[m
 [m
         LandmarkDefinition([m
             index=98,[m
[31m-            name="nose_left_base",[m
[32m+[m[32m            name="nose_right_base",[m
             description=([m
[31m-                "Zona laterale sinistra della base del naso."[m
[32m+[m[32m                "Zona laterale destra della base del naso."[m
             ),[m
         ),[m
 [m
         LandmarkDefinition([m
             index=327,[m
[31m-            name="nose_right_base",[m
[32m+[m[32m            name="nose_left_base",[m
             description=([m
[31m-                "Zona laterale destra della base del naso."[m
[32m+[m[32m                "Zona laterale sinistra della base del naso."[m
             ),[m
         ),[m
 [m
[36m@@ -181,17 +181,17 @@[m [mdef create_standard_landmarks() -> list[LandmarkDefinition]:[m
 [m
         LandmarkDefinition([m
             index=61,[m
[31m-            name="mouth_left",[m
[32m+[m[32m            name="mouth_right",[m
             description=([m
[31m-                "Angolo sinistro della bocca."[m
[32m+[m[32m                "Angolo destro della bocca."[m
             ),[m
         ),[m
 [m
         LandmarkDefinition([m
             index=291,[m
[31m-            name="mouth_right",[m
[32m+[m[32m            name="mouth_left",[m
             description=([m
[31m-                "Angolo destro della bocca."[m
[32m+[m[32m                "Angolo sinistro della bocca."[m
             ),[m
         ),[m
 [m
[36m@@ -213,17 +213,17 @@[m [mdef create_standard_landmarks() -> list[LandmarkDefinition]:[m
 [m
         LandmarkDefinition([m
             index=78,[m
[31m-            name="upper_lip_left",[m
[32m+[m[32m            name="upper_lip_right",[m
             description=([m
[31m-                "Zona sinistra del labbro superiore."[m
[32m+[m[32m                "Zona destra del labbro superiore."[m
             ),[m
         ),[m
 [m
         LandmarkDefinition([m
             index=308,[m
[31m-            name="upper_lip_right",[m
[32m+[m[32m            name="upper_lip_left",[m
             description=([m
[31m-                "Zona destra del labbro superiore."[m
[32m+[m[32m                "Zona sinistra del labbro superiore."[m
             ),[m
         ),[m
 [m
[36m@@ -269,4 +269,4 @@[m [mdef create_standard_landmarks() -> list[LandmarkDefinition]:[m
             ),[m
         ),[m
 [m
[31m-    ][m
\ No newline at end of file[m
[32m+[m[32m    ][m
