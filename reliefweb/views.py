import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['GET'])
def reliefweb_disasters(request):
    query = {
        'fields': {
            'include': [
                'name',
                'status',
                'primary_country',
                'country',
                'primary_type',
                'type',
                'url',
                'date',
                'description'
            ]
        },
        'limit': 30,
        'sort': ['date:desc']
    }

    response = requests.post(
        'https://api.reliefweb.int/v1/disasters',
        json=query
    )
    return JsonResponse(response.json(), safe=False)