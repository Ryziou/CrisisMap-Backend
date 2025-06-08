import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from collections import Counter

def get_reliefweb_stats(query):
    response = requests.post(
        'https://api.reliefweb.int/v1/disasters',
        json=query
    )
    return response.json()

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

@api_view(['GET'])
def reliefweb_stats(request):
    # Total Amount of Disasters
    total_query = { 'limit': 0}
    total_data = get_reliefweb_stats(total_query)
    total_disasters = total_data.get('totalCount', 0)

    # Total Amount of Active Disasters
    active_query = {
        'limit': 0,
        'filter': {
            'field': 'status',
            'value': 'alert'
        }
    }
    active_data = get_reliefweb_stats(active_query)
    active_disasters = active_data.get('totalCount', 0)

    # Most Recent Disaster
    recent_query = {
        'limit': 1,
        'sort': ['date:desc'],
        'fields': {
            'include': [
                'name',
                'status',
                'date',
                'primary_country',
                'primary_type'
            ]
        }
    }
    recent_data = get_reliefweb_stats(recent_query)
    recent_disaster = recent_data['data'][0]['fields']

    # Query for Multiple Filters
    latestdisasters_query = {
        'limit': 500,
        'sort': ['date:desc'],
        'fields': {
            'include': [
                'primary_type',
                'primary_country',
                'status',
                'date'
            ]
        }
    }
    latest_data = get_reliefweb_stats(latestdisasters_query)

    # Combine Latest Disaasters
    # And Count Them
    commontype_types = [
        item['fields']['primary_type']['name']
        for item in latest_data['data']
    ]
    commontype_counter = Counter(commontype_types)
    most_common_type, most_common_count = commontype_counter.most_common(1)[0]

    # Top affected countries
    countries = [
        (
            item['fields']['primary_country']['iso3'],
            item['fields']['primary_country']['name']
        )
        for item in latest_data['data']
    ]

    countries_counter = Counter(countries)
    top_countries = [
        {
            'iso3': iso3.upper(),
            'name': name,
            'disasters': count
        }
        for ((iso3, name), count) in countries_counter.most_common(10)
    ]

    # Amount of Statuses
    status_list = [
        item['fields']['status']
        for item in latest_data['data']
    ]
    status_counter = Counter(status_list)

    # Disasters over time
    monthly_counts = {}

    for item in latest_data['data']:
        if 'date' in item['fields'] and 'created' in item['fields']['date']:
            created_time = item['fields']['date']['created']
            try:
                date_split = created_time.split('T')[0]
                date_parts = date_split.split('-')
                year_month = f'{date_parts[0]}-{date_parts[1].zfill(2)}'
                if year_month in monthly_counts:
                    monthly_counts[year_month] += 1
                else:
                    monthly_counts[year_month] = 1
            except Exception:
                pass

    disasters_overtime = []
    for month in sorted(monthly_counts):
        disasters_overtime.append({
            'month': month,
            'count': monthly_counts[month]
        })

    return JsonResponse({
        'total': total_disasters,
        'active_count': active_disasters,
        'recent_disaster': recent_disaster,
        'common_type': most_common_type,
        'common_count': most_common_count,
        'top_countries': top_countries,
        'status_list': dict(status_counter),
        'disasters_overtime': disasters_overtime,
        'type_list': dict(commontype_counter)
    })

