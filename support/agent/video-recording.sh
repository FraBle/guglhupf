#!/bin/bash
# /usr/local/bin/video-recording
ffmpeg \
-f v4l2 \
-framerate 30 \
-video_size 640x480 \
-i /dev/video1 \
-map 0 \
-segment_time 300 \
-g 30 \
-sc_threshold 0 \
-force_key_frames "expr:gte(t,n_forced*300)" \
-f segment \
-reset_timestamps 1 \
-strftime 1 \
-vf "[in]\
drawtext=\
fontfile=/usr/share/fonts/truetype/SourceCodePro/SourceCodePro-Regular.ttf: \
textfile=/mnt/recordings/gps.txt: \
reload=1: \
x=10: \
y=h-text_h-10: \
fontsize=15: \
fontcolor=black: \
box=1: \
boxcolor=white@0.5: \
boxborderw=5,\
drawtext=\
fontfile=/usr/share/fonts/truetype/SourceCodePro/SourceCodePro-Regular.ttf: \
text='%{localtime}': \
x=w-text_w-10: \
y=h-text_h-10: \
fontsize=15: \
fontcolor=black: \
box=1: \
boxcolor=white@0.5: \
boxborderw=5
[out]" \
-c:v h264_omx \
-pix_fmt yuv420p \
/mnt/recordings/guglhupf/video_front_%Y-%m-%d_%H-%M-%S.mp4
