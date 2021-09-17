import requests
from bs4 import BeautifulSoup
from constant import (
    INSA_URL, PLANNING_URL,
    LOGIN, PASSWORD
)

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

def insa_login():
    """
    Connects to the INSA server with the user's identifiers.

    The server uses the Central Authentication Service (CAS) system,
    it is necessary to send a first GET request to retrieve the
    login ticket and the execution code before sending a POST one
    with the required information.
    """

    response = session.get(INSA_URL)
    content = BeautifulSoup(response.text, 'lxml')

    execution_code = content.find('input', {'name': 'execution'}).get('value')
    login_ticket = content.find('input', {'name': 'lt'}).get('value')

    form = {
        'username': LOGIN,
        'password': PASSWORD,
        'lt': login_ticket,
        'execution': execution_code,
        '_eventId': 'submit'
    }

    session.post(
        INSA_URL,
        data=form
    )


def load_planning() -> str:
    """
    TODO: format calendar content into an .ics file
    """

    response = session.get(PLANNING_URL)

    return response.text


if __name__ == '__main__':
    insa_login()
    planning = load_planning()
