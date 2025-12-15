import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from collections import Counter

HEADERS = {
    'User-Agent': 'CallumLiu-CrisisMap-CL96'
}

def get_reliefweb_stats(post_body):
    """
    Sends a POST request to ReliefWeb API with the given query.
    """
    url = "https://api.reliefweb.int/v2/disasters"
    try:
        response = requests.post(
            url,
            json=post_body,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("ReliefWeb POST request failed:", e)
        if hasattr(e, 'response') and e.response is not None:
            print("Response content:", e.response.text)
        return {"error": str(e)}

@api_view(['GET'])
def reliefweb_stats(request):
    # -----------------------------
    # 1. Total disasters
    # -----------------------------
    total_query = {"limit": 0}
    total_data = get_reliefweb_stats(total_query)
    total_disasters = total_data.get('totalCount', 0)

    # -----------------------------
    # 2. Active disasters (status=alert)
    # -----------------------------
    active_query = {
        "query": {
            "operator": "AND",
            "conditions": [
                {"field": "status", "value": "alert"}
            ]
        },
        "limit": 0
    }
    active_data = get_reliefweb_stats(active_query)
    active_disasters = active_data.get('totalCount', 0)

    # -----------------------------
    # 3. Most recent disaster
    # -----------------------------
    recent_query = {
        "limit": 1,
        "sort": ["date:desc"],
        "fields": {
            "include": ["name", "status", "date", "primary_country", "primary_type"]
        }
    }
    recent_data = get_reliefweb_stats(recent_query)
    if 'data' in recent_data and len(recent_data['data']) > 0:
        recent_disaster = recent_data['data'][0]['fields']
    else:
        recent_disaster = {}

    # -----------------------------
    # 4. Latest 500 disasters (for stats & counts)
    # -----------------------------
    latest_query = {
        "limit": 150,
        "sort": ["date:desc"],
        "fields": {
            "include": ["primary_type", "primary_country", "status", "date"]
        }
    }
    latest_data = get_reliefweb_stats(latest_query)
    latest_items = latest_data.get('data', [])

    # Most common disaster type
    commontype_types = [
        item['fields']['primary_type']['name']
        for item in latest_items
        if 'primary_type' in item['fields'] and 'name' in item['fields']['primary_type']
    ]
    commontype_counter = Counter(commontype_types)
    most_common_type, most_common_count = commontype_counter.most_common(1)[0] if commontype_counter else ("N/A", 0)

    # Top affected countries
    countries = [
        (item['fields']['primary_country']['iso3'], item['fields']['primary_country']['name'])
        for item in latest_items
        if 'primary_country' in item['fields'] and item['fields']['primary_country']
    ]
    countries_counter = Counter(countries)
    top_countries = [
        {"iso3": iso3.upper(), "name": name, "disasters": count}
        for ((iso3, name), count) in countries_counter.most_common(10)
    ]

    # Disaster status counts
    status_list = [
        item['fields']['status']
        for item in latest_items
        if 'status' in item['fields']
    ]
    status_counter = Counter(status_list)

    # Disasters over time
    monthly_counts = {}
    for item in latest_items:
        date_field = item['fields'].get('date', {})
        created_time = date_field.get('created')
        if created_time:
            try:
                year_month = "-".join(created_time.split("T")[0].split("-")[:2])
                monthly_counts[year_month] = monthly_counts.get(year_month, 0) + 1
            except Exception:
                pass
    disasters_overtime = [{"month": month, "count": count} for month, count in sorted(monthly_counts.items())]

    # -----------------------------
    # Return final stats
    # -----------------------------
    return JsonResponse({
        "total": total_disasters,
        "active_count": active_disasters,
        "recent_disaster": recent_disaster,
        "common_type": most_common_type,
        "common_count": most_common_count,
        "top_countries": top_countries,
        "status_list": dict(status_counter),
        "disasters_overtime": disasters_overtime,
        "type_list": dict(commontype_counter)
    })
