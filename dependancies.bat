rem py -m venv env
cd env/Scripts
activate

py -m pip install oauthlib
py -m pip install requests
py -m pip install requests-oauthlib
py -m pip install gql[requests]

py -m pip install beautifulsoup4
py -m pip install selenium
py -m pip install webdriver-manager
py -m pip install html5lib

deactivate
pause