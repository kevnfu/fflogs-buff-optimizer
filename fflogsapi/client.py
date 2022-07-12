from config import CLIENT_ID, CLIENT_SECRET

CLIENT_API_URL = 'https://www.fflogs.com/api/v2/client'
OAUTH_TOKEN_URL = 'https://www.fflogs.com/oauth/token'

Q_REPORT = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            masterData {{
                title
                actors(subType: "Boss") {{
                    id
                    name
                    subType
                }}
            }}
            startTime
            endTime
            fights {{
                id
                encounterID
                startTime
                endTime
            }}
        }}
    }}
}}
"""

Q_EVENTS = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            events(filterExpression: "inCategory('deaths') = true", startTime: 8984334, endTime: 9448023) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

reportCode = "fj1tvmxZhWa2zKHd"
fightID = "1"

# auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
client = oauth2.BackendApplicationClient(CLIENT_ID)
session = OAuth2Session(client=client)

token = session.fetch_token(
    OAUTH_TOKEN_URL,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

print(token)

access_token = token['access_token']

transport = RequestsHTTPTransport(url=CLIENT_API_URL)
transport.headers = {'Authorization': f'Bearer {access_token}'}

gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

gql_q = gql(Q_REPORT.format(reportCode=reportCode))

res = gql_client.execute(gql_q)

report = res['reportData']['report']


class FFlogsClient(object):
	"""docstring for FFlogsClient"""
	def __init__(self, arg):
		super(FFlogsClient, self).__init__()
		self.arg = arg
		