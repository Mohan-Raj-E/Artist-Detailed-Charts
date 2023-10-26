import pandas as pd
import plotly.express as px
import streamlit as st
import os

# Define a function to load and process the data
def load_and_process_data(directory_path):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame()

    # Loop through Excel files in the directory and concatenate them to the combined DataFrame
    for filename in os.listdir(directory_path):
        if filename.endswith(".xlsx"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_excel(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Remove special characters from the 'Artist' column except for commas and colons
    combined_df['Artist'] = combined_df['Artist'].str.replace('[^a-zA-Z0-9, :]', '', regex=True)
    # Remove spaces after commas in the "Artist" column
    combined_df['Artist'] = combined_df['Artist'].str.replace(', ', ',')

    # Group by 'Artist' and 'Channel Name' and sum the columns
    combined_df = combined_df.groupby(['Artist', 'Channel Name']).agg({
        'No of content': 'sum',
        'No of Content Above Million': 'sum'
    }).reset_index()

    result_df_1 = combined_df.groupby('Artist').agg({
        'No of content': 'sum',
        'No of Content Above Million': 'sum',
        'Channel Name': lambda x: dict(zip(x, combined_df.loc[x.index, 'No of content'])),
    })
    result_df_1.reset_index(inplace=True)

    # Rename the 'Channel Name' column to 'Channel Name'
    result_df_1.rename(columns={'Channel Name': 'Channel Content Contribution'}, inplace=True)

    result_df_2 = combined_df.groupby('Artist').agg({
                                            'No of content': 'sum',
                                            'No of Content Above Million': 'sum',
                                            'Channel Name': lambda x: dict(zip(x, combined_df.loc[x.index, 'No of Content Above Million']))
                                            })
    result_df_2.reset_index(inplace=True)

    # Rename the 'Channel Name' column to 'Channel Name'
    result_df_2.rename(columns={'Channel Name': 'Channel Above Million Content Contribution'}, inplace=True)

    # Merge df_1 and df_2 based on the 'Artist' column
    merged_df = result_df_1.merge(result_df_2[['Artist', 'Channel Above Million Content Contribution']], on='Artist', how='left')

    Top_Content_Artist = merged_df.nlargest(10, 'No of content').reset_index(drop=True)
    Top_Content_Artist = Top_Content_Artist[['Artist','Channel Content Contribution']]

    Top_Million_Artist = merged_df.nlargest(10, 'No of Content Above Million').reset_index(drop=True)
    Top_Million_Artist = Top_Million_Artist[['Artist','Channel Above Million Content Contribution']]

    # Create and return the merged DataFrame
    return Top_Content_Artist, Top_Million_Artist

# Streamlit app
st.title("Artist Contribution Analysis")

# Load and process the data
# Input field to ask the user for the directory path
# Input for the directory path
directory_path = st.text_input("Enter the directory path where the data is located")

# Add a button to initiate the process
if st.button("Process"):
    # Check if the directory path is provided
    if directory_path:
        # Process the data located at the provided directory path
        st.write(f"Processing data at directory: {directory_path}")
    else:
        # Display a message if the directory path is not provided
        st.write("Please enter a directory path before processing.")

# Check if a directory path is provided
if directory_path:
    Top_Content_Artist, Top_Million_Artist = load_and_process_data(directory_path)

    # Selectbox to choose between Top_Content_Artist and Top_Million_Artist
    selected_dataframe = st.selectbox("Select a DataFrame:", [None, "Top_Content_Artist", "Top_Million_Artist"])

    if selected_dataframe is not None:
        if selected_dataframe == "Top_Content_Artist":
            selected_df = Top_Content_Artist

            # Select an artist using the selectbox
            # Select an artist using the selectbox
            artist_names = selected_df['Artist'].str.capitalize().unique().tolist()
            artist_names.insert(0, None)
            selected_artist = st.selectbox("Select an artist:", artist_names)


            if selected_artist is not None:
                if selected_artist:
                    selected_artist = selected_artist.lower()

                    artist_data = selected_df[selected_df['Artist'] == selected_artist]

                    if not artist_data.empty:
                        # Extract the contribution data for the selected artist
                        contribution_data = artist_data['Channel Content Contribution'].iloc[0]

                        st.markdown(
                            f"{selected_artist.capitalize()} Produced Total of {sum(list(contribution_data.values()))} Content in 2023")

                        # Create a pie chart using Plotly Express
                        fig = px.pie(
                            names=list(contribution_data.keys()),
                            values=list(contribution_data.values()),
                            title=f'Contribution of {selected_artist.capitalize()} for Producing More Content',
                            labels={'names': 'Channel'}
                        )
                        # Increase the plot size (adjust width and height as needed)
                        fig.update_layout(width=800, height=600)

                        st.plotly_chart(fig)
                    else:
                        st.warning("No data available for the selected artist.")
            else:
                st.write("Please select an artist.")
        else:
            selected_df = Top_Million_Artist

            #selected_artist = None  # Initialize selected_artist as None
            # Select an artist using the selectbox
            artist_names = selected_df['Artist'].str.capitalize().unique().tolist()
            artist_names.insert(0, None)
            selected_artist = st.selectbox("Select an artist:", artist_names)

            if selected_artist is not None:
                if selected_artist:
                    selected_artist = selected_artist.lower()
                    # Filter the DataFrame for the selected artist
                    artist_data = selected_df[selected_df['Artist'] == selected_artist]

                    if not artist_data.empty:
                        # Extract the contribution data for the selected artist
                        contribution_data = artist_data['Channel Above Million Content Contribution'].iloc[0]

                        st.markdown(
                            f"{selected_artist.capitalize()} Produced Total of {sum(contribution_data.values())} Above Million Views Content in 2023")

                        # Create a pie chart using Plotly Express
                        fig = px.pie(
                            names=list(contribution_data.keys()),
                            values=list(contribution_data.values()),
                            title=f'Contribution of {selected_artist.capitalize()} to Above Million Views Content',
                            labels={'names': 'Channel'}
                        )
                        # Increase the plot size (adjust width and height as needed)
                        fig.update_layout(width=800, height=600)
                        st.plotly_chart(fig)
                    else:
                        st.warning("No data available for the selected artist.")
            else:
                st.write("Please select an artist.")
    else:
        st.write("Please select a DataFrame.")