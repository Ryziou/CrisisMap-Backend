import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from collections import Counter

HEADERS = {
    'User-Agent': 'CallumLiu-CrisisMap-CL96'
}

BASE_URL = "https://api.reliefweb.int/v2/disasters"


def get_reliefweb_stats(params):
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {"data": [], "totalCount": 0}


@api_view(['GET'])
def reliefweb_disasters(request):
    params = {
        'fields[include][]': [
            'id', 'name', 'status', 'primary_country', 'country',
            'primary_type', 'type', 'url', 'date', 'description'
        ],
        'limit': 100,  # reduce limit to prevent timeouts
        'sort[]': 'date:desc'
    }

    data = get_reliefweb_stats(params)
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def reliefweb_stats(request):
    # Total disasters
    total_data = get_reliefweb_stats({'limit': 0})
    total_disasters = total_data.get('totalCount', 0)

    # Active disasters (status = alert)
    active_data = get_reliefweb_stats({'limit': 0, 'filter[field]': 'status', 'filter[value]': 'alert'})
    active_disasters = active_data.get('totalCount', 0)

    # Most recent disaster
    recent_data = get_reliefweb_stats({
        'fields[include][]': ['name', 'status', 'date', 'primary_country', 'primary_type'],
        'limit': 1,
        'sort[]': 'date:desc'
    })
    recent_disaster = recent_data['data'][0]['fields'] if recent_data['data'] else {}

    # Latest disasters for stats
    latest_data = get_reliefweb_stats({
        'fields[include][]': ['primary_type', 'primary_country', 'status', 'date'],
        'limit': 100,
        'sort[]': 'date:desc'
    })

    # Count disaster types
    commontype_counter = Counter(item['fields']['primary_type']['name'] for item in latest_data['data'])
    most_common_type, most_common_count = commontype_counter.most_common(1)[0] if commontype_counter else ("N/A", 0)

    # Top countries
    countries_counter = Counter(
        (item['fields']['primary_country']['iso3'], item['fields']['primary_country']['name'])
        for item in latest_data['data']
    )
    top_countries = [
        {'iso3': iso3.upper(), 'name': name, 'disasters': count}
        for ((iso3, name), count) in countries_counter.most_common(10)
    ]

    # Status counts
    status_counter = Counter(item['fields']['status'] for item in latest_data['data'])

    # Disasters over time
    monthly_counts = {}
    for item in latest_data['data']:
        date_info = item['fields'].get('date', {})
        created_time = date_info.get('created')
        if created_time:
            year_month = "-".join(created_time.split('T')[0].split('-')[:2])
            monthly_counts[year_month] = monthly_counts.get(year_month, 0) + 1

    disasters_overtime = [{'month': m, 'count': c} for m, c in sorted(monthly_counts.items())]

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
