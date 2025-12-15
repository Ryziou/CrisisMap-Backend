import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from collections import Counter

# User-Agent header (best practice)
HEADERS = {
    'User-Agent': 'CallumLiu-CrisisMap-CL96'
}

# Base URL with appname query string explicitly included
BASE_URL = "https://api.reliefweb.int/v2/disasters?appname=CallumLiu-CrisisMap-CL96"


def get_reliefweb_stats(query):
    """
    Makes a POST request to ReliefWeb API with a query JSON.
    Returns a dict with at least 'data' and 'totalCount'.
    """
    try:
        response = requests.post(BASE_URL, json=query, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        # If anything goes wrong, return empty structure
        return {"data": [], "totalCount": 0}


@api_view(['GET'])
def reliefweb_disasters(request):
    """
    Returns the latest disasters with full details.
    """
    query = {
        'fields': {
            'include': [
                'id', 'name', 'status', 'primary_country', 'country',
                'primary_type', 'type', 'url', 'date', 'description'
            ]
        },
        'limit': 100,
        'sort': ['date:desc']
    }

    data = get_reliefweb_stats(query)
    return JsonResponse(data, safe=False)


@api_view(['GET'])
def reliefweb_stats(request):
    """
    Returns aggregated stats for the latest 100 disasters:
    - total count
    - active count
    - most recent disaster
    - most common type
    - top affected countries
    - statuses
    - disasters over time
    """
    # Total disasters
    total_data = get_reliefweb_stats({'limit': 1})
    total_disasters = total_data.get('totalCount', 0)

    # Active disasters
    active_data = get_reliefweb_stats({
        'limit': 1,
        'filter': {'field': 'status', 'value': 'alert'}
    })
    active_disasters = active_data.get('totalCount', 0)

    # Most recent disaster
    recent_data = get_reliefweb_stats({
        'limit': 1,
        'sort': ['date:desc'],
        'fields': {'include': ['name', 'status', 'date', 'primary_country', 'primary_type']}
    })
    recent_disaster = {}
    if recent_data.get('data') and len(recent_data['data']) > 0:
        recent_disaster = recent_data['data'][0].get('fields', {})

    # Latest disasters for stats
    latest_data = get_reliefweb_stats({
        'limit': 100,
        'sort': ['date:desc'],
        'fields': {'include': ['primary_type', 'primary_country', 'status', 'date']}
    })
    latest_items = latest_data.get('data', [])

    # Count disaster types
    commontype_counter = Counter(
        item.get('fields', {}).get('primary_type', {}).get('name', 'Unknown')
        for item in latest_items
    )
    most_common_type, most_common_count = commontype_counter.most_common(1)[0] if commontype_counter else ("N/A", 0)

    # Top affected countries
    countries_counter = Counter()
    for item in latest_items:
        country = item.get('fields', {}).get('primary_country')
        if country:
            iso3 = country.get('iso3', 'N/A').upper()
            name = country.get('name', 'Unknown')
            countries_counter[(iso3, name)] += 1
    top_countries = [
        {'iso3': iso3, 'name': name, 'disasters': count}
        for ((iso3, name), count) in countries_counter.most_common(10)
    ]

    # Status counts
    status_counter = Counter(
        item.get('fields', {}).get('status', 'Unknown')
        for item in latest_items
    )

    # Disasters over time
    monthly_counts = {}
    for item in latest_items:
        created_time = item.get('fields', {}).get('date', {}).get('created')
        if created_time and 'T' in created_time:
            parts = created_time.split('T')[0].split('-')
            if len(parts) >= 2:
                year_month = f"{parts[0]}-{parts[1].zfill(2)}"
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
