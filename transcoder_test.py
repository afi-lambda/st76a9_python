import json

from transcoder import Transcoder


def test_transcoder01():
    with open('evaluation.json') as json_file:
        json_data = json.load(json_file)
    for each in json_data:
        source = each['source']
        alto_source = each['alto_source']
        transcoded_source = Transcoder.to_alto("doIt [^[" + source + "]]")
        assert transcoded_source == alto_source
