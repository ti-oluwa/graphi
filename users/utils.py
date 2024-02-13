import re
from django.http import HttpRequest
from typing import Any, Dict



def parse_query_params_from_request(request: HttpRequest) -> Dict[str, str]:
    """Parses the query parameters from a request. Returns a dictionary of the query parameters."""
    if request.method != "POST":
        return request.GET.dict()
    
    query_param_pattern = r"&?(?P<param_name>[a-zA-Z0-9-_\s]+)=(?P<param_value>[a-zA-Z0-9-_/\?=\\\s]+)"
    request_path: str = request.META.get("HTTP_REFERER", "")
    try:
        _, query_params_part = request_path.split("?", maxsplit=1)
        results = re.findall(query_param_pattern, query_params_part)
        if not results:
            return {}
    except ValueError:
        return {}
    return {param_name: param_value for param_name, param_value in results}


def underscore_dict_keys(_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Replaces all hyphens in the dictionary keys with underscores"""
    return {key.replace('-', "_"): value for key, value in _dict.items()}
