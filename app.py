import streamlit as st
import mysql.connector
import requests
import base64
import time

# Spotify Credentials 'We should 
client_id = 'ee25b9c5e4fb4221a09e60fe877e63a2'
client_secret = '33be200e61ad4caa9fa61b8331c00421'

def get_spotify_access_token(client_id, client_secret):
    if 'spotify_token_expiry' not in st.session_state or time.time() > st.session_state.spotify_token_expiry:
        token_url = "https://accounts.spotify.com/api/token"
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
        token_headers = {
            "Authorization": f"Basic {client_creds_b64}"
        }
        token_data = {
            "grant_type": "client_credentials"
        }
        token_response = requests.post(token_url, headers=token_headers, data=token_data)
        if token_response.status_code in range(200, 299):
            token_response_data = token_response.json()
            now = time.time()
            access_token = token_response_data['access_token']
            expires_in = token_response_data['expires_in']
            st.session_state.spotify_token_expiry = now + expires_in
            st.session_state.spotify_access_token = access_token
        else:
            raise Exception("Could not obtain token from Spotify")
    return st.session_state.spotify_access_token

def search_spotify(query, client_id, client_secret):
    access_token = get_spotify_access_token(client_id, client_secret)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    search_url = "https://api.spotify.com/v1/search"
    params = {
        "q": query,
        "type": "track",
        "limit": 10
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tracks']['items']
    else:
        return None

def get_musicbrainz_artist_country(artist_name):
    search_url = f"https://musicbrainz.org/ws/2/artist/"
    params = {
        "query": artist_name,
        "fmt": "json"
    }
    headers = {
        "User-Agent": "musicDBmanager/1.0 ( junghean@usc.edu )" 
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        artists = response.json()['artists']
        if artists:
            # Assuming the first artist is the correct one
            return artists[0].get('country', 'N/A')
    return 'N/A'

st.title('Spotify Music Database')

with st.form("search_form"):
    search_query = st.text_input("Enter search query")
    submitted = st.form_submit_button("Search")
    if submitted and search_query:
        search_results = search_spotify(search_query, client_id, client_secret)
        if search_results:
            for track in search_results:
                artist_name = track['artists'][0]['name']
                country = get_musicbrainz_artist_country(artist_name)
                st.write(f"**{track['name']}** by {artist_name} ({country})")
                st.write(f"Album: {track['album']['name']}, Release Date: {track['album']['release_date']}")
                st.image(track['album']['images'][0]['url'], width=100)
        else:
            st.write("No results found.")
