import streamlit as st
import base64
import pandas as pd
from tabulate import tabulate
from API_Toolkit import get_splice_ai_data, get_clinvar_classification, search_pubmed, get_varsome_data_url, get_revel_score, get_gnomad_data, get_ensembl_rest_data, get_ensembl_functional_data, get_genomic_coordinates

primaryColor="red"
backgroundColor="red"
secondaryBackgroundColor="#0000FF"
textColor="#262730"
font="sans serif"

# Function to render title page
def render_page1():
    st.image('./SVID_image2.png')
    st.title("Somatic Variant Interpretation Dashboard")
    st.write(" ")
  
      # Add a box with descriptive text
    st.markdown("""
        This dashboard enables analysis of somatic variants. 
        It includes summary data, in silico predictions, case/control frequencies, literature search and an area for training cases to practice classification.
        Explore the different pages to access specific features and information.
    """)

    # Add some blank space 
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Add a navy box with descriptive text
    st.markdown("""
        <div style='background-color: #001f3f; padding: 10px; border-radius: 5px;'>
            <p style='color: #ffffff;'>The tools throughout this dashboard can be used along with various guideline to aid interpretation of the pathogenicity of variants.</p>
        </div>
    """, unsafe_allow_html=True)

    # Add some blank space before the columns
    st.markdown("<br><br>", unsafe_allow_html=True)

     # Create a Streamlit row layout
    col1, col2 = st.columns([2, 1])  # Adjust the ratio as needed
    
    # Add a grey box with descriptive text in the left column
    with col1:
         st.markdown("""
        <div style='background-color: #f2f2f2; padding: 10px; border-radius: 5px; color: #000000;'>
            <p>The ACGS provides guidelines for the classification of somatic variants in rare disease and cancer.</p>
        </div>
""", unsafe_allow_html=True)

    with col2:
        # Insert an image below the text
        st.image('./ACGS2.png', width=200)


# Function to render summary data page
def render_page2():
    st.title("Summary Data")
    st.write("")

    # Using HTML entity to represent a colon (&#58;)
    # Common user input for both buttons
    # Input for the search term
    search_term = st.text_input("Enter variant in HGVS nomenclature e.g. NM_000516.7&#58;c.601C>T:")

    # Button to trigger the search
    if st.button("Get summary data"):
        # Check if the search term is not empty
        if search_term:
            # Call the Ensembl function with the search term
            ensembl_data = get_ensembl_rest_data(search_term)
            genomic_coordinates = get_genomic_coordinates(search_term)

            # Call the ClinVar function with the search term
            clinvar_data = get_clinvar_classification(search_term)

            # Call the VarSome function with the search term
            varsome_url = get_varsome_data_url(search_term)

            # Display the results
            st.subheader("Ensembl")
            if ensembl_data:
                for key, value in ensembl_data.items():
                    st.write(f"{key}: {value}")
            else:
                st.warning("Not enough information in the Ensembl response or structure is not as expected.")
            if genomic_coordinates:
                st.write("GRCh38 Genomic Coordinates: " f"{genomic_coordinates.get('Chromosome', 'N/A')}-{genomic_coordinates.get('Start', 'N/A')}-{genomic_coordinates.get('VariantChange', 'N/A')}")
            else:
                st.warning("Not enough information in the genomic coordinates response or structure is not as expected.")


            st.subheader("ClinVar Classification")
            if clinvar_data:
                clinical_significance, review_status, link = clinvar_data
                st.write(f"Clinical Significance: {clinical_significance}")
                st.write(f"Review Status: {review_status}")
                st.write(f"ClinVar Search: {link}")
            else:
                st.warning("Clinical significance not found or variant not found in ClinVar.")

            st.subheader("Varsome")
            if varsome_url:
                st.markdown(f"[Link to Varsome Classification]({varsome_url})")
            else:
                st.warning("Error fetching VarSome data or variant not found.")
        else:
            st.warning("Please enter a search term.")


# Function to render in silico predictions page
def render_page3():
    st.title("In Silico Predictions")
    st.write(" ")

    # Common user input for both functions
    user_input = st.text_input("Example variant format: 8-140300616-T-G", "Enter variant", key="combined_input")

    # Button to trigger both functions
    if st.button("Get SpliceAI and Revel Data"):
        st.write("Processing...")

        # Call the spliceAI function to retrieve the data
        splice_ai_data = get_splice_ai_data(user_input)

        # Display SpliceAI data
        if splice_ai_data is not None:
            splice_ai_scores = {
                "Acceptor Gain": splice_ai_data['scores'][0]['DS_AG'],
                "Acceptor Loss": splice_ai_data['scores'][0]['DS_AL'],
                "Donor Gain": splice_ai_data['scores'][0]['DS_DG'],
                "Donor Loss": splice_ai_data['scores'][0]['DS_DL']
            }
            st.write("SpliceAI Scores:")
            st.table(splice_ai_scores)
        else:
            st.write("Error retrieving SpliceAI data.")

        # Call the Revel function to retrieve the data
        revel_result = get_revel_score(user_input)

        # Display Revel data
        if revel_result:
            display_data = {
                "Ensemble_geneid": [revel_result.get("Ensembl_geneid", "")],
                "Ensemble_transcriptid": [revel_result.get("Ensembl_transcriptid", "")],
                "REVEL_score": [revel_result.get("REVEL_score", "")],
                "REVEL_rankscore": [revel_result.get("REVEL_rankscore", "")]
            }
            st.write("REVEL:")
            st.table(display_data)
        else:
            st.write("No search results found for Revel.")
        
        # Ensembl data
        ensembl_functional_data = get_ensembl_functional_data(user_input)
        st.subheader("Ensembl")
        if ensembl_functional_data:
            for key, value in ensembl_functional_data.items():
                st.write(f"{key}: {value}")
        else:
            st.warning("Not enough information in the Ensembl response or structure is not as expected.")

# Function to render case data page
def render_page4():
    st.title("Control/Case Frequency")
    st.write(" ")

    # GnomAD
    st.header("GnomAD")
    hgvs_variant = st.text_input("Enter variant in HGVS nomenclature e.g. NM_000516.7&#58;c.601C>T:")

    if st.button("Search GnomAD"):
        if hgvs_variant:
            # Call the combined function
            result = get_gnomad_data(hgvs_variant)

            if result:
                formatted_variant, genome_data, exome_data = result

                # Calculate allele frequency
                genome_data['allele_frequency'] = genome_data['ac'] / genome_data['an'] if genome_data['an'] != 0 else None
                exome_data['allele_frequency'] = exome_data['ac'] / exome_data['an'] if exome_data['an'] != 0 else None

                # Create dataframes
                genome_df = pd.DataFrame([genome_data])
                exome_df = pd.DataFrame([exome_data])

                # Display results with tabulate
                st.subheader("Results:")
                st.write("Formatted Variant for GnomAD Search:", formatted_variant)

                st.subheader("GnomAD Genome Data:")
                st.text(tabulate(genome_df, headers='keys', tablefmt='pretty', showindex=False))

                st.subheader("GnomAD Exome Data:")
                st.text(tabulate(exome_df, headers='keys', tablefmt='pretty', showindex=False))

                # Add GnomAD link
                gnomad_link = f"https://gnomad.broadinstitute.org/variant/{formatted_variant}"
                st.write(f"GnomAD Link: [{formatted_variant}]({gnomad_link})")

# Function to render literature page
def render_page5():
    st.title("Literature Search")
    st.write("This is the content of Page 5.")

    st.header("PubMed")
    third_user_input = st.text_input("Search any variant or disease association in PubMed", "Search")

    if st.button("Search Pubmed"):
        if third_user_input:
            st.write("Searching Pubmed...")
            pubmed_results = search_pubmed(third_user_input)
            if pubmed_results:
                for result in pubmed_results:
                    st.markdown(result, unsafe_allow_html=True)
            else:
                st.write("No search results found.")
        else:
            st.warning("Please enter a different text for Pubmed action.")

# Function to render training cases page
def render_page6():
    st.title("Training cases")
    st.write("Cases to practice somatic variant interpretation following current guidelines.")

    # Read the first image as binary data
    with open('./TNGS_case1.png', 'rb') as f1:
        image_data1 = f1.read()

    # Encode the first image to base64
    image_base64_1 = base64.b64encode(image_data1).decode()

    # Use the encoded first image in the HTML
    st.markdown(f"""
        <div style='background-color: #001f3f; padding: 10px; border-radius: 5px; text-align: center;'>
            <p style='color: #ffffff;'>
                Case 1:<br>
                New diagnosis of acute myeloid leukaemia. Custom NGS panel revealed a variant.
            </p>
            <img src='data:image/png;base64,{image_base64_1}' alt='Image Alt Text' width='70%' style='margin: 0 auto;'/>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Read the second image as binary data
    with open('./TNGS_case2.png', 'rb') as f2:
        image_data2 = f2.read()

    # Encode the second image to base64
    image_base64_2 = base64.b64encode(image_data2).decode()

    # Use the encoded second image in the HTML
    st.markdown(f"""
        <div style='background-color: #001f3f; padding: 10px; border-radius: 5px; text-align: center;'>
            <p style='color: #ffffff;'>
                Case 2:<br>
                Diagnosis of moderately differentiated colorectal adenocarcinoma with suspected liver metastases seen on imaging.
            </p>
            <img src='data:image/png;base64,{image_base64_2}' alt='Image Alt Text' width='70%' style='margin: 0 auto;'/>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Read the third image as binary data
    with open('./TNGS_case3.png', 'rb') as f3:
        image_data3 = f3.read()

    # Encode the third image to base64
    image_base64_3 = base64.b64encode(image_data3).decode()

    # Use the encoded third image in the HTML
    st.markdown(f"""
    <div style='background-color: #001f3f; padding: 10px; border-radius: 5px; text-align: center;'>
        <p style='color: #ffffff;'>
            Case 3:<br>
            Mucinous carcinoma involving both ovaries. Fallopian tube surface involvement present. Metastatic adenocarcinoma to omentum (56mm deposit).
        </p>
        <img src='data:image/png;base64,{image_base64_3}' alt='Image Alt Text' width='70%' style='margin: 0 auto;'/>
    </div>
""", unsafe_allow_html=True)



    # Checkbox to toggle visibility
    show_text = st.checkbox("Show Answers")

    # Hidden text box
    if show_text:
        st.markdown(f"""
            <div style='background-color: #f2f2f2; padding: 10px; border-radius: 5px; color: #000000;'>
                <p>Case 1:<br>
                Answer:<br><br>
                Case 2:<br>
                Answer:<br><br>
                Case 3:<br>
                Answer:</p>
            </div>
        """, unsafe_allow_html=True)


# Create a dictionary mapping page names to corresponding functions
pages = {
    "Somatic Variant Interpretation Dashboard": render_page1,
    "Summary Data": render_page2,
    "In Silico Predictions": render_page3,
    "Case/Control Frequency": render_page4,
    "Literature Search": render_page5,
    "Training cases": render_page6
}

# Create a sidebar with links to different pages
selected_page = st.sidebar.selectbox("Select a page", list(pages.keys()))
st.sidebar.image("SVID_image.png", caption=" ", width=250)


# Render the selected page
pages[selected_page]()



