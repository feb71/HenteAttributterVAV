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
    # Oppdater kun kolonnen 'informasjon' basert på Profilnr og materiale
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

            # Formatér siste_profilnr som en streng med komma som desimalskilletegn
            siste_profilnr_str = f'{siste_profilnr:.2f}'.replace('.', ',')

            # Oppdater kun informasjon-kolonnen
            if pd.isna(informasjon) or informasjon.strip() == "":
                ny_informasjon = f'Materiale: {materiale}\\nLengde: {siste_profilnr_str}'
            else:
                informasjon = str(informasjon)
                if 'Lengde: ' in informasjon:
                    ny_informasjon = informasjon.replace(
                        'Lengde: ' + str(informasjon.split('Lengde: ')[1].split()[0]),
                        f'Lengde: {siste_profilnr_str}'
                    )
                else:
                    ny_informasjon = informasjon + f' \\nLengde: {siste_profilnr_str}'

            # Oppdater kun informasjon-kolonnen
            innmaaling_df.loc[start_index, 'informasjon'] = ny_informasjon

    return innmaaling_df

# Del applikasjonen i to kolonner med venstre kolonne 1/4 bredde og høyre kolonne 3/4 bredde
col1, col2 = st.columns([1, 5])

# Venstre kolonne: Dropdowns og valg
with col1:
    st.header("Innstillinger")
    
    # Filopplasting
    uploaded_innmaaling_file = st.file_uploader("Last opp innmålingsfilen (Excel)", type="xlsx", key="innmaaling_file")
    uploaded_attributter_file = st.file_uploader("Last opp attributtfilen (Excel)", type="xlsx", key="attributter_file")

    if uploaded_innmaaling_file and uploaded_attributter_file:
        # Les inn Excel-filen
        innmaaling_df = pd.read_excel(uploaded_innmaaling_file)
        attributter_df = pd.read_excel(uploaded_attributter_file)
        
        koblingsnokkel = st.selectbox("Velg koblingsnøkkel", attributter_df.columns)

        # Fjern uønskede attributter fra valgene
        uønskede_attributter = ["Id", "Lengde", "Lengde 3D", "Lukket", "Areal"]
        tilgjengelige_attributter = [col for col in attributter_df.columns if col not in uønskede_attributter]

        if st.checkbox("Overskriv attributter"):
            attributes_to_overwrite = st.multiselect("Velg attributter som skal overskrives", tilgjengelige_attributter)
            if st.button("Overskriv"):
                innmaaling_df = overskriv_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_overwrite)
                st.success("Attributter har blitt overskrevet.")
        
        if st.checkbox("Legg til attributter"):
            attributes_to_add = st.multiselect("Velg attributter som skal legges til", tilgjengelige_attributter)
            if st.button("Legg til"):
                innmaaling_df = legg_til_attributter(innmaaling_df, attributter_df, koblingsnokkel, attributes_to_add)
                st.success("Attributter har blitt lagt til.")
        
        if st.button("Oppdater lengdeverdi i informasjon"):
            innmaaling_df = oppdater_informasjon(innmaaling_df)
            st.success("Lengdeverdi i informasjon er oppdatert.")

# Høyre kolonne: Visning av data og nedlastingsmulighet
with col2:
    st.header("Oppdatere atteributter VAV")
    
    # Visning av DataFrame
    if uploaded_innmaaling_file and uploaded_attributter_file:
        st.subheader("Visning av DataFrame:")
        st.dataframe(innmaaling_df)

        # Legg til nedlastingsknappen
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            innmaaling_df.to_excel(writer, index=False)
        st.download_button(
            label="Last ned oppdatert Excel-fil",
            data=output.getvalue(),
            file_name="oppdatert_innmaaling.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
