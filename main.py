import requests
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
import folium
from flask import Flask, render_template, request


def twitter_friends(user_name, token):
    '''
    Getting twitter friends
    '''

    url = "https://api.twitter.com/"

    my_params = {'screen_name': f'@{user_name}'}

    my_headers = {'Authorization': f'Bearer {token}'}

    search_url = f'{url}1.1/friends/list.json'

    response = requests.get(
        search_url, headers=my_headers, params=my_params)

    users = []
    followers_coordinates = []

    followers = response.json()

    for follower in followers['users']:
        users.append((follower['name'], follower['location']))

    for user in users:
        coord = (user[0], get_coordinates(user[1]))
        if isinstance(coord[1], tuple) == True:
            followers_coordinates.append(coord)

    return followers_coordinates


def get_coordinates(address):
    '''
    Returns coordinates of given address
    '''

    geolocator = Nominatim(user_agent="marta")
    location = geolocator.geocode(address)
    if location:

        coords = (location.latitude, location.longitude)
    else:
        return 'No location'

    return coords


def map(followers_coordinates):
    '''
    Creates a map with markers on film places, user's location and the best
    city
    '''

    map = folium.Map(location=[37.77721786139184, -
                               122.4165454598356], zoom_start=2)
    fg_followers = folium.FeatureGroup(name='Friends')
    for point in followers_coordinates:
        coordinates = point[1]
        text = 'Your friend '+point[0]+' is here!'
        fg_followers.add_child(folium.Marker(
            location=[coordinates[0], coordinates[1]], popup=text,
            icon=folium.Icon()))
        map.add_child(fg_followers)

    fg_twitter = folium.FeatureGroup(name='Twitter')
    fg_twitter.add_child(folium.Marker(
        location=[37.77721786139184, -122.4165454598356], popup='Twitter is located here',
        icon=folium.Icon(color='purple')))
    map.add_child(fg_twitter)

    map.add_child(folium.LayerControl())


    return map


app = Flask(__name__)


@app.route("/")
def index():
    '''
    Returns the start page
    '''
    return render_template('index.html')


@app.route("/register", methods=["POST"])
def friends_map():
    '''
    Returns map with friends locations.
    '''
    name = request.form.get("screen_name")
    bearer_token = request.form.get("bearer_token")
    map1 = map(twitter_friends(name, bearer_token))
    if not name or not bearer_token:
        return render_template('failure.html')
    return map1.get_root().render()


if __name__ == '__main__':
    app.run(debug=True, port = 2151)
