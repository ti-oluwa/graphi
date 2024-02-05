import re
from django.http import HttpRequest
from typing import Any, Dict



def parse_query_params_from_request(request: HttpRequest) -> Dict[str, str]:
    """Parses the query parameters from a request. Returns a dictionary of the query parameters."""
    if request.method != "POST":
        return request.GET.dict()
    
    query_param_pattern = r"[\?&]+(?P<param_name>[a-zA-Z0-9-_\s]+)=(?P<param_value>[a-zA-Z0-9-_/\\\s]+)"
    request_path = request.META.get("HTTP_REFERER", "")
    results = re.findall(query_param_pattern, request_path)
    if not results:
        return {}
    return {param_name: param_value for param_name, param_value in results}


def underscore_dict_keys(_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Replaces all hyphens in the dictionary keys with underscores"""
    return {key.replace('-', "_"): value for key, value in _dict.items()}
