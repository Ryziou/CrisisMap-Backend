import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def reliefweb_disasters(request):
    params = request.GET.copy()
    params['appname'] = 'CrisisMap'
    response = requests.get(
        'https://api.reliefweb.int/v1/disasters',
        params=params
    )
    return JsonResponse(response.json(), safe=False)