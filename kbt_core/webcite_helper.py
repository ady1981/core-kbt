import requests

from common import log_str


def verify(webcite_api_key, a_concept, b_concept, superordinate_concept, aspect, aspect_feature, perspective):
    claim = f'''# Claim context
superordinate_concept: {superordinate_concept}
aspect: {aspect}
aspect_feature: {aspect_feature}
## Perspective details
{perspective}

# Claim
{a_concept} is strictly better (not equal) than {b_concept} in this aspect_feature  
'''
    response = requests.post(
        'https://api.webcite.co/api/v1/verify',
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': webcite_api_key
        },
        json = {
            'claim': claim,
            'include_stance': True,
            'include_verdict': True,
            # 'useEnhancedAnalysis': False,
            'useClaimDecomposition': False
        }
    )
    try:
        json_response = response.json()
        verdict = json_response['claim_groups'][0]['verdict']
        result = {
            'result': verdict['result'], ## "contradicted", "supported", "unverifiable"
            'confidence': verdict.get('confidence') / 100.0 if verdict.get('confidence') else 0.0,
            'stance_breakdown': verdict.get('stance_breakdown'),
            'other_notes': verdict.get('summary'),
            'raw': json_response
        }
        return result
    except Exception as e:
        log_str('unknown_error, raw_response=' + response.text)
        raise e