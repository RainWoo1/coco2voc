import cv2 as cv
import numpy as np
from PIL import Image, ImageFilter
from pycocotools import mask as mask_utils

PIXEL = 255
BORDER_THICKNESS = 7

def annotations_to_seg(annotations, coco_instance, apply_border, color):
    # annotations: Sequence[dict] annotations json part
    # coco_instance: COCO
    # apply_border: bool = False

    image_details = coco_instance.loadImgs(annotations[0]['image_id'])[0]

    h = image_details['height']
    w = image_details['width']

    # Create 2D arrays with zeros in three categories: class, instance, and id
    class_seg = np.zeros((h, w))
    instance_seg = np.zeros((h, w))
    id_seg = np.zeros((h, w))

    # Create a mask
    masks, annotations = annotations_to_mask(annotations, h, w)

    for i, mask in enumerate(masks):
        # if i == 1: break
        if apply_border == False:
            class_seg = np.where(class_seg > 0, class_seg, mask * annotations[i]['category_id'])  # 81
            instance_seg = np.where(instance_seg > 0, instance_seg, mask * (i+1))
            id_seg = np.where(id_seg > 0, id_seg, mask * annotations[i]['id'])
            # class_seg = np.stack([class_seg, class_seg, class_seg], axis = -1)
            # class_seg[h, w] = (255, 0, 0)
            selected_region = np.where(mask == 1) # class_seg == i
            class_mask = np.zeros((h, w, 3), np.uint8)

            # 컬러 정하기
            if color == "빨간색":
                class_mask[selected_region] = (255, 0, 0)
            elif color == "파란색":
                class_mask[selected_region] = (0, 0, 255)
            else:
                class_mask[selected_region] = (255, 255, 255)

        # whether to add a void (255) border region around the masks or not
        else:
            border = get_border(mask, color, BORDER_THICKNESS) # get border
            border_mask = np.zeros((h, w, 3), np.uint8)
            selected_region = np.where(border > 0)
            border_mask[selected_region] = (255, 0, 0)
            # for seg in [class_seg, instance_seg, id_seg]:
                # border_mask[border > 0][]
                # seg[border > 0] = (255, 0, 0)

    # three 2D numpy arrays where the value of each pixel is the class id, instance number, and instance id
    if apply_border == False:
        return class_seg, instance_seg, id_seg.astype(np.int64), class_mask
    else:
        return class_seg, instance_seg, id_seg.astype(np.int64), border_mask

def annotation_to_rle(ann, h, w):
    # dict, int, int
    # Convert annotation which can be polygons, uncompressed RLE to RLE.
    segm = ann['segmentation']
    if type(segm) == list:
        # polygon -- a single object might consist of multiple parts
        # we merge all parts into one mask rle code
        rles = mask_utils.frPyObjects(segm, h, w)
        rle = mask_utils.merge(rles)
    elif type(segm['counts']) == list:
        rle = mask_utils.frPyObjects(segm, h, w)  # Encode the RLE
    else:
        rle = ann['segmentation']  # RLE
    
    # binary mask (numpy 2D array)
    return rle

def annotations_to_mask(annotations, h, w):
    # Sequence[dict], int, int
    # Convert annotations which can be polygons, uncompressed RLE, or RLE to binary masks
    masks = []
    # Smaller items first, so they won't be covered by overlapping segmentations
    annotations = sorted(annotations, key=lambda x: x['area'])
    for ann in annotations:
        rle = annotation_to_rle(ann, h, w)
        m = mask_utils.decode(rle)
        masks.append(m)
    
    # A list of binary masks (each a numpy 2D array) of all the annotations in anns
    return masks, annotations


def get_border(mask: np.ndarray, color: str, thickness_factor: int = 7) -> np.ndarray:

    # np.ndarray, int = 7
    pil_mask = Image.fromarray(mask)  # Use PIL to reduce dependencies
    dilated_pil_mask = pil_mask.filter(ImageFilter.MaxFilter(thickness_factor))

    border = np.array(dilated_pil_mask) - mask

    return border