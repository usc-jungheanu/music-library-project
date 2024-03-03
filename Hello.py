import calendar
from datetime import datetime 
import streamlit as st
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import musicbrainzngs
import mysql.connector
import requests
import hashlib
import base64
import time



# ------ DB Management & Connection -------


# MySQL Connection for DB1 "MusicManager_Intl":
def connect_to_mysql_db1():
    try:
        db1_connection = mysql.connector.connect(
            host="database-1.cj26uo6s41hg.us-west-2.rds.amazonaws.com", 
            user="admin",
            password="RusticRatio60090",
            database="MusicManager_Intl",  # International DB
            port= 3306
        )
        if db1_connection.is_connected():
            # st.write("Successfully connected to MySQL database DB1")
            # You can perform database operations here using db1_connection
            return db1_connection
    except mysql.connector.Error as e:
        # st.write(f"Error connecting to MySQL database DB1: {e}")
        return None
    

# MySQL Connection for DB2 "MusicManager_US":
def connect_to_mysql_db2():
    try:
        db2_connection = mysql.connector.connect(
            host="database-1.cj26uo6s41hg.us-west-2.rds.amazonaws.com", 
            user="admin",
            password="RusticRatio60090",
            database="MusicManager_US",  # US DB
            port= 3306
        )
        if db2_connection.is_connected():
            # st.write("Successfully connected to MySQL database DB2")
            # You can perform database operations here using db1_connection
            return db2_connection
    except mysql.connector.Error as e:
        st.write(f"Error connecting to MySQL database DB2: {e}")
        return None
    
# Ensure to close the MySQL connections when done
def close_mysql_connection(connection):
    if connection is not None and connection.is_connected():
        connection.close()
        # st.write("MySQL connection is closed")


# # Example usage
# db1_connection = connect_to_mysql_db1()
# db2_connection = connect_to_mysql_db2()



# ------ API Connection For Data Retrieval | Backend Engineering ------

# Spotify Credentials (eventually set up as an env. variable)
client_id = 'ee25b9c5e4fb4221a09e60fe877e63a2'
client_secret = '33be200e61ad4caa9fa61b8331c00421'

#reset token if when expired
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

# request spotify's api and query track data
def search_spotify(query, client_id, client_secret):
    access_token = get_spotify_access_token(client_id, client_secret)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    search_url = "https://api.spotify.com/v1/search"
    params = {
        "q": query,
        "type": "track",
        "limit": 20
    }
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['tracks']['items']
    else:
        return None

# request musicbrainz api and extract country code for artists nationality
# def get_musicbrainz_artist_country(artist_name):
#     search_url = f"https://musicbrainz.org/ws/2/artist/"
#     params = {
#         "query": artist_name,
#         "fmt": "json"
#     }
#     headers = {
#         "User-Agent": "musicDBmanager/1.0 ( junghean@usc.edu )" 
#     }
#     response = requests.get(search_url, headers=headers, params=params)
#     if response.status_code == 200:
#         artists = response.json()['artists']
#         if artists:
#             # Assuming the first artist is the correct one
#             return artists[0].get('country', 'N/A')
#     return 'N/A'

def get_musicbrainz_artist_country(artist_name):
    # Set up musicbrainzngs with your application name and version
    musicbrainzngs.set_useragent("musicDBmanager", "1.0", "junghean@usc.edu")

    try:
        # Use search_artists to search for the artist by name
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        artists = result.get('artist-list', [])
        if artists:
            # Assuming the first artist is the correct one
            artist = artists[0]
            return artist.get('country', 'N/A')
    except Exception as e:
        print(f"Error fetching artist country: {e}")
    return 'N/A'




# ------ Frontend Development / UI/UX Design ------


# Setup the layout

st.sidebar.title("TuneSync")
st.sidebar.header("Music Database Manager App")

# Menu sidebar (consider moving to top or leave as-is)
page = st.sidebar.selectbox("Menu", ["Browse Artists in TuneSync", "View Music Library", "Crud Operations With MySQL"])

if page == "Browse Artists in TuneSync":
    st.header("Browse Artists")

    # search engine query to filter results by artist name, album name, song name
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

    # more on this page, we'll want to switch the spotify/musicbrainzngs api sources to the databases, allowing end users to
    # access the data from both databases, search by title (song, artist, album) & country/nationality, sort data, filter, etc
    # any additional functions/features that we can fit in this page for end user engagement/experience          
    # also make sure to adjust the artist section to search artist name and not band name
    # include section to include artists individuals as well like Russell Brand, Kurt Cobain
    # add functionality during the data transformation process to allow for manual entry of country code if missing or set as N/A any Country Code is set to N/A - do the same maybe for other things like song name, albums, etc
                        
elif page == "View Music Library":
    st.header("View Music Library")


    # -------------------- SETTINGS -----------------------

    incomes = ["Salary","Blog","Other Income"]
    expenses = ["Rent", "Utilities", "Groceries", "Car", "Other Expenses", "Saving"]
    currency = "USD"
    page_title = "Income and Expense Tracker"
    page_icon = ":money_with_wings:"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
    layout = "centered"

    # -----------------------------------------------------

    # st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
    # st.title(page_title + " " + page_icon)

    # ------ DROP DOWN VALUES FOR SELECTING THE PERIOD ------

    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:])

    # --- DATABASE INTERFACE ---
    def get_all_periods():
        items = db.fetch_all_periods()
        periods = [item["key"] for item in items]
        return periods

    # ------ HIDE STREAMLIT STYLE ------

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # --- NAVIGATION MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Visualization"],
        icons=["pencil-fill", "bar-chart-fill"],  # https://icons.getbootstrap.com/
        orientation="horizontal",
    )

    # ------ INPUT & SAVE PERIODS ------

    st.header(f"Data Entry in {currency}")
    with st.form("entry from", clear_on_submit=True):
        col1, col2 = st.columns(2)
        col1.selectbox("Select Month:", months, key="month")
        col2.selectbox("Select Year:", years, key="year")

        "---"
        with st.expander("Income"):
            for income in incomes:
                st.number_input(f"{income}:", min_value=0, format="%i", step=10, key=income)
        with st.expander("Expenses"):
            for expense in expenses:
                st.number_input(f"{expense}:", min_value=0, format="%i", step=10, key=expense)
        with st.expander("Comment"):
            comment = st.text_area("", placeholder="Enter a comment here ...")
        
        "---"
        submitted = st.form_submit_button("Save Data")
        if submitted:
            period =  str(st.session_state["year"]) + "_" + str(st.session_state["month"])
            incomes = {income: st.session_state[income] for income in incomes}
            expenses = {expenses: st.session_state[expense] for expense in expenses}

            # TODO: Insert values into database
            st.write(f"incomes: {incomes}")
            st.write(f"expenses: {expenses}")
            st.success("Data saved!")


    # ----- PLOT PERIODS ------

    if selected == "Data Visualization":
        st.header("Data Visualization")
        with st.form("saved_periods"):
            # TODO: Get periods from database
            period = st.selectbox("Select Period:", ["2022_March"])
            submitted = st.form_submit_button("Plot Period")
            if submitted:
                # TODO: Get data from database
                comment = "Some Comment"
                incomes = {'Salary': 1500, 'Blog': 50, 'Other Income': 10}
                expenses = {'Rent': 600, 'Utilities': 200, 'Groceries': 300, 
                            'Car': 100, 'Other Expenses': 50, 'Saving': 10}          
                
                # Create metrics
                total_income = sum(incomes.values())
                total_expense = sum(expenses.values())
                remaining_budget = total_income - total_expense
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income", f"{total_income}{currency}")
                col2.metric("Total Expense", f"{total_expense}{currency}")
                col3.metric("Remaining Budget", f"{remaining_budget}{currency}")
                st.text(f"Comment: {comment}")

                # Create sankey chart
                label = list(incomes.keys()) + ["Total Income"] + list(expenses.keys())
                source = list(range(len(incomes))) + [len(incomes)] * len(expenses)
                target = [len(incomes)] * len(incomes) + [label.index(expense) for expense in expenses.keys()]
                value = list(incomes.values()) + list(expenses.values())

                        # Data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # Plot it!
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)



    # enter code for this page
    # expecting to have this page consist of admin/engineer roles with permission to manage the data/etl process, 
    # to ensure the following tasks/maintenance: new data is appended to dbs perodically, delete records, clean up/modify records, etc
     

elif page == "Crud Operations With MySQL":

    # Create function to hash the country value before insertion
    def hash_country(country):
        """Hash the country using SHA-256."""
        hasher = hashlib.sha256()
        hasher.update(country.encode('utf-8'))  # Encode the country to bytes
        return hasher.hexdigest()

    # Create function that decides which database connection to use absed on the country's value. 
    def get_connection_based_on_country(country):
        """Decide which DB connection to use based on the country."""
        if country == "US":
            return connect_to_mysql_db2()  # this connects to the MusicManager_US database
        else:
            return connect_to_mysql_db1()  # this connects to the MusicManager_Intl database

    st.header("MySQL Data Entry")

    option = st.sidebar.selectbox("Select an Operation", ("Create", "Read", "Update", "Delete"))

    if option == "Create":
        st.subheader("Create a Record")
        Artist = st.text_input("Enter Artist")
        Album = st.text_input("Enter Album")
        Song = st.text_input("Enter Song")
        Genre = st.text_input("Enter Genre")
        Country = st.text_input("Enter Country of Origin")

        if st.button("Create"):
           
            # Decide which DB to use based on the original (unhashed) country value
            mydb = get_connection_based_on_country(Country)
            
            if mydb is not None:
                mycursor = mydb.cursor()
                sql = "INSERT INTO artist_listing (Artist, Album, Song, Genre, Country) VALUES (%s, %s, %s, %s, %s)"
                val = (Artist, Album, Song, Genre, Country)
                mycursor.execute(sql, val)
                mydb.commit()
                mycursor.close()  # Close cursor after operation
                st.success("Record Created Successfully!")
            else:
                st.error("Failed to connect to the database.")



    elif option == "Read":
        st.subheader("Read Records")

        # Let the user choose the database
        db_choice = st.selectbox("Choose the database", ("MusicManager_Intl", "MusicManager_US"))

        # Decide which database to use based on the user's choice
        if db_choice == "MusicManager_Intl":
            mydb = connect_to_mysql_db1()
        else:
            mydb = connect_to_mysql_db2()

        if mydb is not None:
            mycursor = mydb.cursor()
            try:
                sql = "SELECT * FROM artist_listing"
                mycursor.execute(sql)
                records = mycursor.fetchall()
                
                if records:
                    # Display each record in a nice format
                    for record in records:
                        st.text(f"ID: {record[0]}, Artist: {record[1]}, Album: {record[2]}, Song: {record[3]}, Genre: {record[4]}, Country: {record[5]}")
                else:
                    st.info("No records found.")
            except Exception as e:
                st.error(f"Failed to read records: {e}")
            finally:
                mycursor.close()
        else:
            st.error("Failed to connect to the selected database.")




    elif option == "Update":
        st.subheader("Update a Record")
        record_id = st.number_input("Enter ID", min_value=1, format="%d")
        Artist = st.text_input("Enter New Name")
        Album = st.text_input("Enter New Album")
        Song = st.text_input("Enter New Song")
        Genre = st.text_input("Enter New Genre")
        Country = st.text_input("Enter Country of Origin")

        if st.button("Update"):
            # Initialize update clause components
            update_clauses = []
            values = []

            # For each field, check if a value has been provided and add it to the update statement
            if Artist: 
                update_clauses.append("Artist = %s")
                values.append(Artist)
            if Album: 
                update_clauses.append("Album = %s")
                values.append(Album)
            if Song: 
                update_clauses.append("Song = %s")
                values.append(Song)
            if Genre: 
                update_clauses.append("Genre = %s")
                values.append(Genre)
            if Country: 
                update_clauses.append("Country = %s")
                values.append(Country)

            # Only proceed if there's at least one field to update
            if update_clauses:
                sql = "UPDATE artist_listing SET " + ", ".join(update_clauses) + " WHERE id = %s"
                values.append(record_id)  # Append the record ID to the list of values for the WHERE clause

                # Decide which database to connect based on the Country field if provided, or default logic
                mydb = get_connection_based_on_country(Country) if Country else connect_to_mysql_db1() # Adjust default logic as needed

                if mydb is not None:
                    mycursor = mydb.cursor()
                    mycursor.execute(sql, tuple(values))
                    mydb.commit()
                    mycursor.close()
                    st.success("Record Updated Successfully!")
                else:
                    st.error("Failed to connect to the database.")
            else:
                st.warning("No fields were updated. Please fill in at least one field.")



    elif option == "Delete":
        st.subheader("Delete a Record")

        # Let the user choose the database
        db_choice = st.selectbox("Choose the database", ("MusicManager_Intl", "MusicManager_US"))

        record_id = st.number_input("Enter ID", min_value=1, format="%d")

        if st.button("Delete Record"):
            # Decide which database to use based on the user's choice
            if db_choice == "MusicManager_Intl":
                mydb = connect_to_mysql_db1()
            else:
                mydb = connect_to_mysql_db2()

            if mydb is not None:
                mycursor = mydb.cursor()
                try:
                    sql = "DELETE FROM artist_listing WHERE id = %s"
                    val = (record_id,)  # Ensure the ID is passed as a tuple
                    mycursor.execute(sql, val)
                    mydb.commit()
                    if mycursor.rowcount > 0:
                        st.success("Record Deleted Successfully!")
                    else:
                        st.warning("No record found with the provided ID.")
                except Exception as e:
                    st.error(f"Failed to delete the record: {e}")
                finally:
                    mycursor.close()
            else:
                st.error("Failed to connect to the selected database.")




# ----- Settings Page ------
            
    # add basic controls for user roles and permissions to access/view app content (we may not need this page)
