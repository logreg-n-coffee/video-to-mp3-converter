import os
import requests


def token(request):
    # validate the jwt the user possess
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing authorization", 401)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},
    )

    if response.status_code == 200:
        return response.text, None
    else:
        return None, (response.text, response.status_code)
