from resumer.model import Combined
from zrcl.markdown import create_yaml_properties 
from zrcl.app_pandoc import pandoc_generate_file_from_data

def get_batches_model(*datas):
    base = None
    for data in datas:
        model = Combined.fromDict(data, base)
        if base is None:
            base = model

    return base

