# empty_room_gen/masking/modules/detection_cache.py

# image_id → (boxes_px, masks, scores, labels, (w, h)) 형태 저장
DETECTED_RESULTS = {}