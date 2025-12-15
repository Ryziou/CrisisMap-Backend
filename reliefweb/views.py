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
        # Safe fallback if API fails
        return {"data": [], "totalCount": 0}

@api_view(['GET'])
def reliefweb_stats(request):
    # Total disasters
    total_data = get_reliefweb_stats({'limit': 1})  # limit=1 to get totalCount
    total_disasters = total_data.get('totalCount', 0)

    # Active disasters
    active_data = get_reliefweb_stats({
        'limit': 1,
        'filter[field]': 'status',
        'filter[value]': 'alert'
    })
    active_disasters = active_data.get('totalCount', 0)

    # Most recent disaster (safe)
    recent_data = get_reliefweb_stats({
        'fields[include][]': ['name', 'status', 'date', 'primary_country', 'primary_type'],
        'limit': 1,
        'sort[]': 'date:desc'
    })
    recent_disaster = {
        'name': 'N/A',
        'status': 'N/A',
        'date': None,
        'primary_country': {},
        'primary_type': {}
    }
    if recent_data.get('data'):
        fields = recent_data['data'][0].get('fields', {})
        recent_disaster['name'] = fields.get('name', 'N/A')
        recent_disaster['status'] = fields.get('status', 'N/A')
        recent_disaster['date'] = fields.get('date', {}).get('created')
        recent_disaster['primary_country'] = fields.get('primary_country', {})
        recent_disaster['primary_type'] = fields.get('primary_type', {})

    # Latest disasters for stats
    latest_data = get_reliefweb_stats({
        'fields[include][]': ['primary_type', 'primary_country', 'status', 'date'],
        'limit': 100,
        'sort[]': 'date:desc'
    })

    data_items = latest_data.get('data', [])

    # Count disaster types
    commontype_counter = Counter(
        item['fields']['primary_type']['name']
        for item in data_items
        if item.get('fields') and item['fields'].get('primary_type')
    )
    most_common_type, most_common_count = commontype_counter.most_common(1)[0] if commontype_counter else ("N/A", 0)

    # Top countries
    countries_counter = Counter(
        (item['fields']['primary_country'].get('iso3', ''), item['fields']['primary_country'].get('name', ''))
        for item in data_items
        if item.get('fields') and item['fields'].get('primary_country')
    )
    top_countries = [
        {'iso3': iso3.upper(), 'name': name, 'disasters': count}
        for ((iso3, name), count) in countries_counter.most_common(10)
        if iso3 and name
    ]

    # Status counts
    status_counter = Counter(
        item['fields'].get('status', 'Unknown')
        for item in data_items
        if item.get('fields')
    )

    # Disasters over time
    monthly_counts = {}
    for item in data_items:
        fields = item.get('fields', {})
        created_time = fields.get('date', {}).get('created')
        if created_time:
            # Safe split
            try:
                parts = created_time.split('T')[0].split('-')
                if len(parts) >= 2:
                    year_month = f"{parts[0]}-{parts[1].zfill(2)}"
                    monthly_counts[year_month] = monthly_counts.get(year_month, 0) + 1
            except Exception:
                continue

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
