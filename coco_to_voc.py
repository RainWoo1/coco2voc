import os

import numpy as np
from PIL import Image
from pycocotools.coco import COCO

from coco_to_voc_aux import annotations_to_seg

def coco2voc(annotations_file: str, folder: str, n: int = None, apply_border: bool = False):

    annVal = os.path.join(annotations_file, 'annotations', os.path.basename(annotations_file))
    coco_instance = COCO(annVal) # COCO 파일 불러오기
    coco_imgs = coco_instance.imgs # coco image 전체 불러오기 {이미지 id: "images" 하위에 있는 정보 읽어오기}
    # coco_anns = coco_instance.anns # coco anns 전체 불러오기

    if n == None: n = len(coco_imgs)
    else:
        assert type(n) == int, "n must be an integer"
        n = min(n, len(coco_imgs))

    class_target_path = os.path.join(folder, 'class_labels') # class_labels 폴더 image 폴더 하위에 생성

    for i, img in enumerate(coco_imgs):
        img_id = coco_instance.getImgIds(img) # [14]

        # lesion
        category_id = coco_instance.getCatIds(catNms=['lesion']) # 81 # print(coco_anns[9]['image_id'])
       
        annotation_ids = coco_instance.getAnnIds(catIds=category_id, imgIds=img_id) # [1]
        if not annotation_ids:
            continue
        annotations = coco_instance.loadAnns(annotation_ids)
        class_seg, instance_seg, id_seg = annotations_to_seg(annotations, coco_instance, apply_border) # segment에 annotation하는 함수
        Image.fromarray(class_seg).convert("P").save(class_target_path + '/' + coco_imgs[img_id[0]]['file_name'][:-4] + '_EGC.png') # NumPy 배열을 PIL 이미지로 변환
        
        # tool
        category_id = coco_instance.getCatIds(catNms=['tools']) # [82]
        annotation_id1 = coco_instance.getAnnIds(catIds=category_id, imgIds=img_id)
        if not annotation_id1:
            continue
        else:
            annotations1 = coco_instance.loadAnns(annotation_id1)
            class_seg, instance_seg, id_seg = annotations_to_seg(annotations1, coco_instance, apply_border) # segment에 annotation하는 함수
            Image.fromarray(class_seg).convert("P").save(class_target_path + '/' + coco_imgs[img_id[0]]['file_name'][:-4] +  '_EGC_' + str(category_id[0]) +'.png')

    return 0



# annotation_ids = coco_instance.getAnnIds(img) # annotations에 있는 id. [1, 4, 6]
# annotations = coco_instance.loadAnns(annotation_ids) # annotations 부분 id부터 segmentations을 다 보기
# if not annotations:
#     continue