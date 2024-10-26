import streamlit as st
import pandas as pd
import io

# Sett appen til fullskjerm-bredde
st.set_page_config(layout="wide")

def oppdater_informasjon(innmaaling_df):
    # Iterér gjennom hver rad og oppdater kun lengdetallet i informasjon
    for idx, row in innmaaling_df.iterrows():
        siste_profilnr = row['Profilnr']
        
        # Formater lengdetallet
        siste_profilnr_str = f'{siste_profilnr:.2f}'.replace('.', ',')

        # Hvis informasjon inneholder "Lengde: ", bytt kun ut lengdetallet etter "Lengde: "
        if pd.notna(row['informasjon']) and "Lengde: " in row['informasjon']:
            start = row['informasjon'].split('Lengde: ')[0] + 'Lengde: '
            ny_informasjon = start + siste_profilnr_str
            innmaaling_df.at[idx, 'informasjon'] = ny_informasjon
        # Hvis informasjon mangler eller ikke har "Lengde: ", legg til lengdeinformasjonen
        elif pd.notna(row['informasjon']):
            innmaaling_df.at[idx, 'informasjon'] = row['informasjon'] + f' \\nLengde: {siste_profilnr_str}'
        else:
            innmaaling_df.at[idx, 'informasjon'] = f'Lengde: {siste_profilnr_str}'

    return innmaaling_df

# Trinn 1: Last opp og vis data, og gi mulighet til å laste ned filen som Excel
st.header("Last opp innmålingsdata")
uploaded_file = st.file_uploader("Last opp innmålingsfilen (Excel)", type="xlsx", key="initial_upload")

if uploaded_file:
    innmaaling_df = pd.read_excel(uploaded_file)
    st.subheader("Original DataFrame")
    st.dataframe(innmaaling_df)

    # Gi brukeren mulighet til å laste ned filen som Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        innmaaling_df.to_excel(writer, index=False)
    st.download_button(
        label="Last ned Excel-fil",
        data=output.getvalue(),
        file_name="innmaaling_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Trinn 2: Last opp filen igjen og oppdater lengdeverdiene
st.header("Last opp filen på nytt for å oppdatere lengdeverdien")
updated_file = st.file_uploader("Last opp filen på nytt for lengdeoppdatering", type="xlsx", key="update_upload")

if updated_file:
    updated_df = pd.read_excel(updated_file)
    updated_df = oppdater_informasjon(updated_df)
    
    st.subheader("Oppdatert DataFrame med lengdeverdi i informasjon")
    st.dataframe(updated_df)

    # Gi mulighet til å laste ned den oppdaterte filen som Excel
    output_updated = io.BytesIO()
    with pd.ExcelWriter(output_updated, engine='openpyxl') as writer:
        updated_df.to_excel(writer, index=False)
    st.download_button(
        label="Last ned oppdatert Excel-fil",
        data=output_updated.getvalue(),
        file_name="oppdatert_innmaaling_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
