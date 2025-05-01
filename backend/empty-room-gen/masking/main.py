from masking.run import create_removal_mask 

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    parser.add_argument("--ram_checkpoint", type=str, required=True)
    parser.add_argument("--grounded_checkpoint", type=str, required=True)
    parser.add_argument("--sam_checkpoint", type=str, required=True)
    parser.add_argument("--input_image", type=str, required=True)
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--box_threshold", type=float, default=0.25)
    parser.add_argument("--text_threshold", type=float, default=0.2)
    parser.add_argument("--iou_threshold", type=float, default=0.5)
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    create_removal_mask(args)
