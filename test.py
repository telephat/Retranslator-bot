import requests, json

api_token = "63b7930922a53469c0a602a8016e9390ab6b455d648abe84c496a806a09b6bb4"
api_url = "http://zabbix.gorvoz.ru/zabbix/api_jsonrpc.php"

def api_request(method, params, token = None):
    headers = {'Content-Type': 'application/json-rpc'}
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params, 
        "id": 1,
        "auth": token
    }

    try:
        response = requests.post(api_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_problem_list(groupid):
    objectid = "0"
    problems_list = []
    problems_dict = {}
    problem_req = {
        "output": "extend",
        "selectAcknowledges": "extend",
        "selectTags": "extend",
        "selectSuppressionData": "extend",
        "groupids": groupid,
        #"recent": True,
        "sortfield": ["eventid"],
        "sortorder": "DESC"
    }
    problem_response = api_request("problem.get", problem_req, api_token)
    return problem_response

for i in [39,38,37,36]:
    print(get_problem_list(i))