rem py -m venv env
cd env/Scripts
activate

py -m pip install oauthlib
py -m pip install requests
py -m pip install requests-oauthlib
py -m pip install gql[requests]

deactivate
pause