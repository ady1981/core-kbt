import requests

from kbt_core.common import log_str, dump_json


def better_verify(webcite_api_key, a_concept, b_concept, superordinate_concept, aspect, aspect_feature, perspective):
    perspective2 = f'''## Details of the perspective
{perspective}
''' if perspective else ''
    claim = f'''# Claim context
aspect: {aspect}
aspect_feature: {aspect_feature}
superordinate_concept: {superordinate_concept}
{perspective2}
# Claim
{a_concept} is strictly better (not equal) than {b_concept} in this aspect_feature  
'''.strip()
    response = requests.post(
        'https://api.webcite.co/api/v1/verify',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': webcite_api_key
        },
        json={
            'claim': claim,
            'include_stance': True,
            'include_verdict': True,
            # 'useEnhancedAnalysis': False,
            'useClaimDecomposition': False
        }
    )
    try:
        json_response = response.json()
        if json_response.get('claim_groups', []):
            verdict = json_response['claim_groups'][0]['verdict']
            result = {
                'result': verdict['result'], ## "contradicted", "supported", "unverifiable", "partially_verified" (+ "error")
                'confidence_likelihood': verdict.get('confidence', 0) / 100.0 if verdict.get('confidence') else 0.0,
                'stance_breakdown': verdict.get('stance_breakdown'),
                'other_notes': verdict.get('summary'),
                'raw': json_response
            }
            return result
        else:
            log_str('cannot verify: response=' + dump_json(json_response))
            result = {
                'result': 'error',
                'raw': json_response
            }
            return result
    except Exception as e:
        log_str('unknown_error, raw_response=' + response.text)
        raise e
