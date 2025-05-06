import torch
from empty_room_gen.recognize_anything.segment_anything import build_sam, SamPredictor
from empty_room_gen.recognize_anything.groundingdino.util.utils import get_phrases_from_posmap

def get_grounding_output(model, image, caption, box_thresh, text_thresh, device="cpu"):
    caption = caption.strip().lower()
    if not caption.endswith("."):
        caption += "."

    with torch.no_grad():
        outputs = model(image[None].to(device), captions=[caption])

    logits = outputs["pred_logits"].sigmoid()[0].cpu()
    boxes = outputs["pred_boxes"][0].cpu()

    mask = logits.max(dim=1)[0] > box_thresh
    logits = logits[mask]
    boxes = boxes[mask]

    tokenized = model.tokenizer(caption)
    phrases = [
        get_phrases_from_posmap(l > text_thresh, tokenized, model.tokenizer) + f"({l.max().item():.2f})"
        for l in logits
    ]
    return boxes, logits.max(dim=1)[0], phrases


def get_sam_masks(predictor: SamPredictor, boxes_px: torch.Tensor, scores: torch.Tensor, iou_threshold: float, image_shape):
    # NMS
    keep = torch.ops.torchvision.nms(boxes_px, scores, iou_threshold)
    boxes_px = boxes_px[keep]
    
    # transform to SAM input format
    transformed = predictor.transform.apply_boxes_torch(boxes_px, image_shape).to(boxes_px.device)
    
    # predict masks
    masks, _, _ = predictor.predict_torch(
        boxes=transformed, point_coords=None, point_labels=None, multimask_output=False
    )
    
    return masks, keep