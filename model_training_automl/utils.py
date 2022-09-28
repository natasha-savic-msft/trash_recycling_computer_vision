import jsonlines
import os

### CODE ADAPTED FROM: https://github.com/Azure/medical-imaging/blob/main/notebooks/utils/utils.py

def generate_jsonl_annotations(source, target_path, annotation_file):
    annotations = []
    # delete annotation flie if it exists
    if os.path.exists(annotation_file):
        os.remove(annotation_file)
    # loop through images
    for img_idx, image in enumerate(source['images']):
        id = image['id']
        width = image['width']
        height = image['height']
        file_name = image['file_name']
        extension = file_name.split('.')[-1].lower()
        
        image_dict = {
            "image_url" : target_path + '/' + file_name,
            "image_details" : {
                "format" : extension,
                "width" : width,
                "height" : height },
            "label" : []
        }
        
        # get all annotations for current image
        image_annotations = [annotation for annotation in source['annotations'] if annotation['image_id'] == id]    
        label = {}

        # loop through annotations
        for anno_idx, annotation in enumerate(image_annotations):

            iscrowd = annotation['iscrowd']
            # processing normal cases (iscrowd is 0):
            if iscrowd == 0:
            
                polygons = []
                # loop through list of polygons - will be 1 in most cases
                for segmentation in annotation['segmentation']:
                    
                    polygon = []
                    # loop through vertices:
                    for id, vertex in enumerate(segmentation):
                        if (id % 2) == 0:
                            # x-coordinates (even index)
                            x = vertex / width
                            polygon.append(x)
                
                        else:
                            y = vertex / height
                            polygon.append(y)
                    polygons.append(polygon)
                label_id = [image_annotations[0]["category_id"]]
                #Look up label
                label_ = [d for d in source["categories"] if d['id'] in label_id][0]["supercategory"]
                image_dict['label'].append({
                    "label" : label_,
                    "isCrowd" : iscrowd,
                    "polygon" : polygons
                })
            # TODO: process iscrowd annotations
            if iscrowd != 0:
                pass
                
        # write entry to JSONL file. 
        with jsonlines.open(annotation_file, mode='a') as writer:
                writer.write(image_dict)