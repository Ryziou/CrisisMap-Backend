import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from collections import Counter

HEADERS = {
    'User-Agent': 'CallumLiu-CrisisMap-CL96'
}

BASE_URL = "https://api.reliefweb.int/v2/disasters"

def get_reliefweb_data(params):
    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        # Safe fallback in case of network errors
        return {"data": [], "totalCount": 0}


@api_view(['GET'])
def reliefweb_disasters(request):
    params = {
        'fields[include][]': [
            'id', 'name', 'status', 'primary_country', 'country',
            'primary_type', 'type', 'url', 'date', 'description'
        ],
        'limit': 50,
        'sort[]': 'date:desc'
    }
    data = get_reliefweb_data(params)
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def reliefweb_stats(request):
    # Fetch latest 50 disasters for stats
    latest_data = get_reliefweb_data({
        'fields[include][]': ['name', 'status', 'primary_country', 'primary_type', 'date'],
        'limit': 50,
        'sort[]': 'date:desc'
    })

    data_items = latest_data.get('data', [])

    # Total disasters (from latest 50 only)
    total_disasters = len(data_items)

    # Active disasters
    active_disasters = sum(1 for item in data_items if item.get('fields', {}).get('status') == 'alert')

    # Most recent disaster (safe fallback)
    recent_disaster = {}
    if data_items:
        fields = data_items[0].get('fields', {})
        recent_disaster = {
            'name': fields.get('name', 'N/A'),
            'status': fields.get('status', 'N/A'),
            'date': fields.get('date', {}).get('created', 'N/A'),
            'primary_country': fields.get('primary_country', {}).get('name', 'N/A'),
            'primary_type': fields.get('primary_type', {}).get('name', 'N/A')
        }

    # Count types
    type_counter = Counter()
    for item in data_items:
        primary_type = item.get('fields', {}).get('primary_type', {}).get('name')
        if primary_type:
            type_counter[primary_type] += 1
    most_common_type, most_common_count = type_counter.most_common(1)[0] if type_counter else ("N/A", 0)

    # Top countries
    country_counter = Counter()
    for item in data_items:
        country = item.get('fields', {}).get('primary_country', {})
        if country:
            country_counter[(country.get('iso3', 'N/A'), country.get('name', 'N/A'))] += 1
    top_countries = [
        {'iso3': iso3, 'name': name, 'disasters': count}
        for ((iso3, name), count) in country_counter.most_common(10)
    ]

    # Status counts
    status_counter = Counter()
    for item in data_items:
        status = item.get('fields', {}).get('status')
        if status:
            status_counter[status] += 1

    # Disasters over time
    monthly_counts = {}
    for item in data_items:
        created_time = item.get('fields', {}).get('date', {}).get('created')
        if created_time:
            try:
                year_month = "-".join(created_time.split('T')[0].split('-')[:2])
                monthly_counts[year_month] = monthly_counts.get(year_month, 0) + 1
            except Exception:
                pass
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
        'type_list': dict(type_counter)
    })
