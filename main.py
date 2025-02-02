import json
import requests
from geopy import distance
import folium
from decouple import config

API_KEY = config("API_KEY")


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_user_position(address):
    your_coordinates = fetch_coordinates(API_KEY, address)
    return (your_coordinates[1], your_coordinates[0])


def load_coffee_shops():
    with open("coffee .json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()
    list_coffee = json.loads(file_contents)
    return list_coffee


def get_nearest_coffee_shops(list_coffee, user_coordinates):
    coffee_shop_for_distance = []
    for coffee_shop in list_coffee:
        coffee_shop_coordinates = (coffee_shop["Latitude_WGS84"], coffee_shop["Longitude_WGS84"])
        dist = distance.distance(coffee_shop_coordinates, user_coordinates).km
        coffee_shop_for_distance.append(
            {'title': coffee_shop["Name"],
            'distance': dist,
            'latitude': float(coffee_shop["Latitude_WGS84"]),
            'longitude': float(coffee_shop["Longitude_WGS84"])})
    sorted_coffee_shop_for_distance = sorted(coffee_shop_for_distance, key=lambda x: x['distance'])
    closest_coffee = sorted_coffee_shop_for_distance[:5]
    return closest_coffee


def create_map(user_coordinates, closest_coffee):
    map = folium.Map(location=[user_coordinates[0], user_coordinates[1]],)
    mark_group = folium.FeatureGroup("5 coffee shop").add_to(map)
    for coffee in closest_coffee:
        folium.Marker((coffee['latitude'], coffee['longitude']),icon=folium.Icon(color='red')).add_to(mark_group)
    map.save("index.html")


def main():
    coffee_shops = load_coffee_shops()
    user_coordinates = input("Где Вы находитесь?\n")
    user_coordinates = get_user_position(user_coordinates)
    closest_coffee = get_nearest_coffee_shops(coffee_shops, user_coordinates)
    create_map(user_coordinates, closest_coffee)


if __name__ == "__main__":
    main()