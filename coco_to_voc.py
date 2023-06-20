import os

import numpy as np
from PIL import Image
from pycocotools.coco import COCO

from coco_to_voc_aux import annotations_to_seg

def coco2voc(annotations_file: str, folder: str, n: int = None, apply_border: bool = False):

    coco_instance = COCO(annotations_file) # COCO 파일 불러오기
    coco_imgs = coco_instance.imgs # coco image {이미지 id: "images" 하위에 있는 정보 읽어오기}

    if n == None: n = len(coco_imgs)
    else:
        assert type(n) == int, "n must be an integer"
        n = min(n, len(coco_imgs))

    class_target_path = os.path.join(folder, 'class_labels') # class_labels 폴더 image 폴더 하위에 생성

    for i, img in enumerate(coco_imgs):
        annotation_ids = coco_instance.getAnnIds(img) # annotations에 있는 id. [1, 4, 6]
        annotations = coco_instance.loadAnns(annotation_ids) # annotations 부분 id부터 segmentations을 다 보기
        if not annotations:
            continue
        
        # segment에 annotation하는 함수
        class_seg, instance_seg, id_seg = annotations_to_seg(annotations, coco_instance, apply_border)
        # print(class_seg)

        # NumPy 배열을 PIL 이미지로 변환
        Image.fromarray(class_seg).convert("P").save(class_target_path + '/' + str(img) + '.png')

    return 0

coco2voc('0000017898.json','./image', 1, False)