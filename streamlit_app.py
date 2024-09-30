import pandas as pd
import streamlit as st

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
    linje_start_indexes.append(len(innmaaling_df))

    for i in range(len(linje_start_indexes) - 1):
        start_index = linje_start_indexes[i]
        end_index = linje_start_indexes[i + 1]
        linje_segment = innmaaling_df.iloc[start_index:end_index]

        if not linje_segment.empty:
            siste_rad_index = linje_segment.index[-1]
            siste_profilnr = innmaaling_df.loc[siste_rad_index, 'Profilnr']
            informasjon = innmaaling_df.loc[start_index, 'informasjon']
            materiale = innmaaling_df.loc[start_index, 'materiale']

            siste_profilnr_str = f'{siste_profilnr:.2f}'.replace('.', ',')

            if pd.isna(informasjon) or informasjon.strip() == "":
                ny_informasjon = f'Materiale: {materiale}\nLengde: {siste_profilnr_str}'
            else:
                informasjon = str(informasjon)
                if 'Lengde: ' in informasjon:
                    ny_informasjon = informasjon.replace(
                        'Lengde: ' + str(informasjon.split('Lengde: ')[1].split()[0]),
                        f'Lengde: {siste_profilnr_str}'
                    )
                else:
                    ny_informasjon = informasjon + f' \nLengde: {siste_profilnr_str}'

            innmaaling_df.loc[start_index, 'informasjon'] = ny_informasjon

    return innmaaling_df

st.title("Oppdater Attributter")

uploaded_innmaaling_file = st.file_uploader("Last opp innmålingsfilen (Excel)", type="xlsx")
uploaded_attributter_file = st.file_uploader("Last opp attributtfilen (Excel)", type="xlsx")

if uploaded_innmaaling_file and uploaded_attributter_file:
    innmaaling_df = pd.read_excel(uploaded_innmaaling_file)
    attributter_df = pd.read_excel(uploaded_attributter_file)
    
    koblingsnokkel = st.selectbox("Velg koblingsnøkkel", attributter_df.columns)

    if st.checkbox("Overskriv attributter"):
        attributes_to_overwrite = st.multiselect("Velg attributter som skal overskrives", attributter_df.columns)
        if st.button("Overskriv"):
            innmaaling_df = overskriv_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_overwrite)
            st.success("Attributter har blitt overskrevet.")
    
    if st.checkbox("Legg til attributter"):
        attributes_to_add = st.multiselect("Velg attributter som skal legges til", attributter_df.columns)
        if st.button("Legg til"):
            innmaaling_df = legg_til_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_add)
            st.success("Attributter har blitt lagt til.")
    
    if st.button("Oppdater lengdeverdi i informasjon"):
        innmaaling_df = oppdater_informasjon(innmaaling_df)
        st.success("Lengdeverdi i informasjon er oppdatert.")
    
    st.write("Oppdatert DataFrame:")
    st.dataframe(innmaaling_df)

    output_filename = st.text_input("Skriv inn filnavn for å lagre", "oppdatert_innmaaling.xlsx")
    if st.button("Lagre til Excel"):
        innmaaling_df.to_excel(output_filename, index=False)
        st.success(f"Innmaaling er lagret som '{output_filename}'")
