import os

from dotenv import load_dotenv

from common import encode_term, calc_md5, write_yaml, dump_json
from webcite_helper import verify

load_dotenv()


def main():
    webcite_api_key = os.environ['WEBCITE_API_KEY']
    aspect = 'Fuel efficiency'
    aspect_feature = 'Fuel consumption'
    superordinate_concept = 'evolute i-space'
    a_concept = encode_term('evolute i-space 4x4')
    b_concept = encode_term('evolute i-space')
    perspective = f'''
## Frame of reference
Unbiased objective comparison
## Observer strategy
Based on car characteristics
## Point of view
Customer selecting car with maximum range per tank
'''
    result = verify(webcite_api_key, a_concept, b_concept, superordinate_concept, aspect, aspect_feature, perspective)
    print('=== Response:\n' + dump_json(result))
    hash = calc_md5(result['other_notes'])
    write_yaml(result, f'temp/webcite3.{hash}.response.yaml')

main()