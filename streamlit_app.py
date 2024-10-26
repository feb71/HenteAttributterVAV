import streamlit as st
import pandas as pd
import io

# Sett appen til fullskjerm-bredde
st.set_page_config(layout="wide")

def overskriv_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_overwrite):
    for _, rad in attributter_df.iterrows():
        matching_rows = innmaaling_df[innmaaling_df[koblingsnokkel] == rad[koblingsnokkel]]
        if not matching_rows.empty:
            for attr in attributes_to_overwrite:
                if attr in rad and not pd.isna(rad[attr]):
                    innmaaling_df.loc[matching_rows.index, attr] = rad[attr]
    return innmaaling_df

def legg_til_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_add):
    for _, rad in attributter_df.iterrows():
        matching_rows = innmaaling_df[innmaaling_df[koblingsnokkel] == rad[koblingsnokkel]]
        if not matching_rows.empty:
            for attr in attributes_to_add:
                if attr in rad and not pd.isna(rad[attr]):
                    innmaaling_df.loc[matching_rows.index, attr] = rad[attr]
    return innmaaling_df

def oppdater_informasjon(innmaaling_df):
    linje_start_indexes = innmaaling_df[innmaaling_df['Id'].notna()].index.tolist()
    linje_start_indexes.append(len(innmaaling_df))  # Legg til slutten av DataFrame som en grense

    for i in range(len(linje_start_indexes) - 1):
        start_index = linje_start_indexes[i]
        end_index = linje_start_indexes[i + 1]
        linje_segment = innmaaling_df.iloc[start_index:end_index]

        # Oppdater kun første rad i hver linje-segment
        if not linje_segment.empty:
            siste_rad_index = linje_segment.index[-1]
            siste_profilnr = innmaaling_df.loc[siste_rad_index, 'Profilnr']
            materiale = innmaaling_df.loc[start_index, 'materiale']

            # Formater lengdeverdi med komma som desimalskilletegn
            siste_profilnr_str = f'{siste_profilnr:.2f}'.replace('.', ',')

            # Oppdater kun informasjon for den første raden i segmentet
            ny_informasjon = f'Materiale: {materiale}\\nLengde: {siste_profilnr_str}'
            innmaaling_df.loc[start_index, 'informasjon'] = ny_informasjon

    return innmaaling_df

def format_datafangstdato(df):
    # Formatér datafangstdato til 'åååå-mm-dd' uten klokkeslett
    if 'datafangstdato' in df.columns:
        df['datafangstdato'] = pd.to_datetime(df['datafangstdato'], errors='coerce').dt.strftime('%Y-%m-%d')
    return df

# Del appen i to kolonner for layout
col1, col2 = st.columns([1, 5])

# Venstre kolonne: Filopplasting og valg
with col1:
    st.header("Innstillinger")

    uploaded_innmaaling_file = st.file_uploader("Last opp innmålingsfilen (Excel)", type="xlsx", key="innmaaling_file")
    uploaded_attributter_file = st.file_uploader("Last opp attributtfilen (Excel)", type="xlsx", key="attributter_file")

    if uploaded_innmaaling_file and uploaded_attributter_file:
        innmaaling_df = pd.read_excel(uploaded_innmaaling_file)
        attributter_d
