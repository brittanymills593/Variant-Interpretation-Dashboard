import requests, sys
from bs4 import BeautifulSoup
from xml.etree import ElementTree


# First API tool


def get_splice_ai_data(variant, hg_version=38, distance=500, mask=1):
    """
    Retrieve SpliceAI data for a given genetic variant.

    Parameters:
    - variant (str): The genetic variant in the format "chromosome-position-reference-alternate" (e.g., "8-140300616-T-G").
    - hg_version (int, optional): The human genome version (default is 38 for GRCh38).
    - distance (int, optional): The maximum allowed distance for splice site predictions (default is 500).
    - mask (int, optional): A masking option (default is 1).

    Returns:
    - dict or None: A dictionary containing SpliceAI data for the specified variant if the request is successful,
      or None if the request fails.

    Example:
    >>> variant = "8-140300616-T-G"
    >>> splice_ai_data = get_splice_ai_data(variant)
    >>> if splice_ai_data is not None:
    >>>     print(splice_ai_data)
    """
    
    # Define the base URL for the SpliceAI API
    base_url = "https://spliceailookup-api.broadinstitute.org/spliceai/"
    
    # Construct the URL with query parameters
    url = f"{base_url}?hg={hg_version}&distance={distance}&mask={mask}&variant={variant}"
    
    try:
        # Send a GET request to the SpliceAI API
        response = requests.get(url, verify=False)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Return the parsed data
            return data
        else:
            # Print an error message if the request fails
            print(f"Request failed with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle exceptions raised during the request
        print(f"Request failed with an error: {e}")
        return None


# Next API tool


def get_clinvar_classification(variant):
    """
    Get clinical information for a given variant using two NCBI ClinVar API calls.

    Parameters:
    - variant (str): The variant to search for.

    Returns:
    - tuple: A tuple containing clinical significance and review status if found, otherwise, None.

    The function performs two steps:
    1. Searches for the given variant in the first API to obtain its unique ID.
    2. Uses the obtained variant ID to search in the second API for clinical significance and review status.

    If the variant is not found in the first API or clinical significance is not found in the second API,
    the function returns None. Otherwise, it returns a tuple with clinical significance and review status.

    Example usage:
    variant = "NM_015450.3(POT1):c.1071dup (p.Gln358fs)"
    result = get_clinical_information(variant)

    if result is not None:
    clinical_significance, review_status = result
    print(f"The clinical significance for {variant} is: {clinical_significance}")
    print(f"Review status is: {review_status}")
    """

    # Step 1: Search in the first API to get the variant ID
    search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term={variant}"
    search_response = requests.get(search_url)
    
    # Parse the XML response to get the variant ID
    root = ElementTree.fromstring(search_response.content)
    id_element = root.find('.//Id')
    
    if id_element is None:
        print("Variant not found in the first API.")
        return None
    
    variant_id = id_element.text

    # Step 2: Use the obtained variant ID to search in the second API
    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id={variant_id}"
    summary_response = requests.get(summary_url)

    # Parse the XML response to get the clinical significance and review status
    root = ElementTree.fromstring(summary_response.content)
    description_element = root.find('.//description')
    review_status_element = root.find('.//review_status')

    if description_element is None:
        print("Clinical significance not found in the second API.")
        return None

    # Extract clinical significance and review status
    clinical_significance = description_element.text
    review_status = review_status_element.text
    link = f"https://www.ncbi.nlm.nih.gov/clinvar/{variant_id}"
    
    return clinical_significance, review_status, link


# Next API tool


def search_pubmed(query):
    """
    Search PubMed for a given query and extract links to relevant papers.

    Args:
        query (str): The search query to be used for searching PubMed.

    Returns:
        list of str: A list of HTML links to the relevant papers found in the search results.
                    Each link is constructed as an anchor tag with the title and URL.
                    If no search results are found, a list with a single "No search results found." message is returned.
                    If an error occurs during the request, None is returned.
    """
    # Define the base URL for PubMed
    base_url = "https://pubmed.ncbi.nlm.nih.gov"
    
    # Replace spaces in the query with '+' for the URL
    search_term = query.replace(" ", "+")
    
    # Construct the URL for the PubMed search
    url = f"{base_url}/?term={search_term}"

    try:
        # Send a GET request to the PubMed search URL
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the response
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all search result links
            search_results = soup.find_all("a", class_="docsum-title")

            if search_results:
                result_links = []
                # Iterate through the search results and construct links for each
                for result in search_results:
                    paper_url = base_url + result["href"]
                    paper_title = result.text
                    result_links.append(f'<a href="{paper_url}" target="_blank">{paper_title}</a>')
                return result_links
            else:
                return ["No search results found."]
        else:
            # Print an error message if the request fails
            print(f"Request failed with status code {response.status_code}")
            return None
    except Exception as e:
        # Handle any exceptions that may occur during the request
        print(f"An error occurred: {e}")
        return None


# Next API tool


def get_varsome_data_url(variant, assembly='hg38', annotation_mode='somatic'):
    """
    Fetches the VarSome data URL for a given variant and prints the result.

    Parameters:
    - variant (str): Variant identifier in the format "gene:positionRef>Alt".
    - assembly (str, optional): Genome assembly version (default is 'hg38').
    - annotation_mode (str, optional): Annotation mode for VarSome (default is 'somatic').

    Returns:
    - str: VarSome URL for the specified variant, or None if there was an error.
    """
    try:
        # Construct the variant identifier
        variant_id = f"{assembly}/{variant}"

        # Construct the API endpoint URL
        api_url = f"https://varsome.com/variant/{variant_id}?annotation-mode={annotation_mode}"

        # Make the GET request
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the result URL as a hyperlink
            print(f"VarSome Query Result: {api_url}")
            return api_url
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        # Print an error message if a request exception occurs
        print(f"Error: {e}")
        return None


# Next API tool


def get_revel_score(input_data_string):
    """
    Retrieves REVEL score data from an online database using two API calls.

    Parameters:
    - input_data_string (str): Input data string of the format 'chr-pos-ref-alt'.

    Returns:
    - dict or None: A dictionary containing the REVEL score data if available, or None if no data is retrieved.

    Example Usage:
    input_data_string = '7-124842898-G-T'
    result = get_revel_score(input_data_string)

    if result:
        print(result)
    else:
        print("No data retrieved.")
    """
    # Parse the input data string
    components = input_data_string.split('-')

    # Check if the input string has the correct number of components
    if len(components) != 4:
        raise ValueError("Invalid input data format. It should be 'chr-pos-ref-alt'.")

    # Create a dictionary with keys for each component
    input_data = {
        'chr': components[0],
        'pos': components[1],
        'ref': components[2],
        'alt': components[3],
        'aaref': '',
        'aaalt': '',
        'Ensembl_transcriptid': ''
    }

    # Define the URLs for the API calls
    url_select = "http://database.liulab.science/aSelect"
    url_query = "http://database.liulab.science/SingleQuery"

    # Define the form data for the first API call
    form_data_select = {
        "range": "hg38",
        "selectBasicInfoA": "chr, pos, ref, alt, aaref, aaalt, rs_dbSNP, hg19_chr, hg19_pos, hg18_chr, hg18_pos, aapos, genename, Ensembl_geneid, Ensembl_transcriptid, Ensembl_proteinid, REVEL_score, REVEL_rankscore"
    }

    # Send a POST request for the first API call
    _ = requests.post(url_select, data=form_data_select)

    # Define the form data for the second API call
    form_data_query = {
        'chr': input_data['chr'],
        'pos': input_data['pos'],
        'ref': input_data['ref'],
        'alt': input_data['alt'],
        'aaref': input_data['aaref'],
        'aaalt': input_data['aaalt'],
        'Ensembl_transcriptid': input_data['Ensembl_transcriptid']
    }

    # Send a POST request for the second API call
    response = requests.post(url_query, data=form_data_query)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")
        return None

    # The HTML content retrieved from the API response
    html_content = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')

    # Find the table in the HTML (assuming there's only one table, adjust if needed)
    table = soup.find('table')

    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th', class_='w3-blue')]

    # Extract table rows
    rows = []
    for row in table.find_all('tr'):
        data = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        rows.append(dict(zip(headers, data)))

    # Remove the first row (header row) as it is already included in the headers
    rows = rows[1:]

    # Return the first row of data if available, otherwise, return None
    return rows[0] if rows else None



# Next API tool


import requests
import sys

def get_gnomad_data(hgvs_variant):
    """
    Get genomic coordinates from Ensembl and GnomAD data for a given HGVS variant.

    Parameters:
    - hgvs_variant (str): HGVS notation for the variant.

    Returns:
    - Tuple containing:
        - formatted_variant (str): Formatted variant for GnomAD search.
        - genome_data (dict): GnomAD genome data.
        - exome_data (dict): GnomAD exome data.

    Example usage:
    hgvs_variant = "NM_000516.7:c.601C>T"
    result = get_gnomad_and_ensembl_data(hgvs_variant)
    if result:
        formatted_variant, genome_data, exome_data = result
    """
    
    # Ensembl API to get genomic coordinates
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/hgvs/{hgvs_variant}?"

    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    decoded = r.json()

    if len(decoded) >= 1 and 'transcript_consequences' in decoded[0]:
        first_transcript_consequence = decoded[0]['transcript_consequences'][0]

        variant_change = hgvs_variant.split(":")[-1]
        variant_change = ''.join(c for c in variant_change if not c.isdigit() and c not in ['.', 'c'])
        variant_change = variant_change.replace(">", "-")

        result = {
            "Chromosome": decoded[0].get('seq_region_name', 'N/A'),
            "Start": decoded[0].get('start', 'N/A'),
            "VariantChange": variant_change,
        }

        # Return the formatted string for GnomAD search
        formatted_variant = f"{result['Chromosome']}-{result['Start']}-{result['VariantChange']}"

        # GnomAD API to get data
        api_url = "https://gnomad.broadinstitute.org/api/"

        query_params = {
            "query": """
                query VariantDetails($datasetId: DatasetId!, $variantId: String!) {
                    variant(dataset: $datasetId, variantId: $variantId) {
                        pos
                        ref
                        alt
                        rsid
                        genome {
                            ac
                            an
                        }
                        exome {
                            ac
                            an
                        }
                    }
                }
            """,
            "variables": {
                "datasetId": "gnomad_r4",
                "variantId": formatted_variant
            }
        }

        response = requests.post(api_url, json=query_params)

        if response.status_code == 200:
            data = response.json()
            genome_data = data["data"]["variant"]["genome"]
            exome_data = data["data"]["variant"]["exome"]

            # Print genomic coordinates
            print("Formatted Variant for GnomAD Search:")
            print(formatted_variant)

            # Print GnomAD data
            print("\nGnomAD Data:")
            print("Genome Data:")
            print(genome_data)

            print("\nExome Data:")
            print(exome_data)

            # Add link to GnomAD
            gnomad_link = f"\nGnomAD Link: https://gnomad.broadinstitute.org/variant/{formatted_variant}"
            print(gnomad_link)

            return formatted_variant, genome_data, exome_data
        else:
            print(f"Error: Unable to retrieve data from GnomAD API.")
            return None


# Ensembl 


def get_ensembl_functional_data(hgvs_variant):
    """
    Query Ensembl REST API for variant information based on HGVS notation.

    Parameters:
    - hgvs_variant (str): HGVS notation for the variant.

    Returns:
    - dict: Dictionary containing information about the variant.

    Example:
    >>> hgvs_variant = "NM_000516.7:c.601C>T"
    >>> get_ensembl_functional_data(hgvs_variant)
    """
    # Define the Ensembl server and endpoint for the Variant Effect Predictor (VEP)
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/hgvs/{hgvs_variant}?"

    # Make a GET request to the Ensembl REST API
    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    # Check if the request was successful
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    # Parse the JSON response
    decoded = r.json()

    # Check if there is at least one item in the response and if 'transcript_consequences' is present
    if len(decoded) >= 1 and 'transcript_consequences' in decoded[0]:
        # Extract information from the first item in the 'transcript_consequences' list
        first_transcript_consequence = decoded[0]['transcript_consequences'][0]

        # Return information about the variant as a dictionary
        result = {
            "SIFT Prediction": first_transcript_consequence.get('sift_prediction', 'N/A'),
            "PolyPhen Prediction": first_transcript_consequence.get('polyphen_prediction', 'N/A')
        }

        # Print the result for demonstration
        print("Ensembl Data:")
        for key, value in result.items():
            print(f"{key}: {value}")

        return result
    else:
        print("Not enough information in the response or structure is not as expected.")
        return None
    


# Next API tool



def get_ensembl_rest_data(hgvs_variant):
    """
    Query Ensembl REST API for variant information based on HGVS notation.

    Parameters:
    - hgvs_variant (str): HGVS notation for the variant.

    Returns:
    - dict: Dictionary containing information about the variant.

    Example:
    >>> hgvs_variant = "NM_000516.7:c.601C>T"
    >>> get_ensembl_rest_data(hgvs_variant)
    """
    # Define the Ensembl server and endpoint for the Variant Effect Predictor (VEP)
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/hgvs/{hgvs_variant}?"

    # Make a GET request to the Ensembl REST API
    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    # Check if the request was successful
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    # Parse the JSON response
    decoded = r.json()

    # Check if there is at least one item in the response and if 'transcript_consequences' is present
    if len(decoded) >= 1 and 'transcript_consequences' in decoded[0]:
        # Extract information from the first item in the 'transcript_consequences' list
        first_transcript_consequence = decoded[0]['transcript_consequences'][0]

        # Extract gene symbol from 'transcript_consequence'
        gene_symbol = first_transcript_consequence.get('gene_symbol', 'N/A')

        # Return information about the variant as a dictionary
        result = {
            "Gene Symbol": gene_symbol,
            "Assembly Name": decoded[0].get('assembly_name', 'N/A'),
            "Chromosome": decoded[0].get('seq_region_name', 'N/A'),
            "Genomic Start": decoded[0].get('start', 'N/A'),
            "Genomic End": decoded[0].get('end', 'N/A'),
            "Most Severe Consequence": decoded[0].get('most_severe_consequence', 'N/A'),
            "Protein Start": first_transcript_consequence.get('protein_start', 'N/A'),
            "Protein End": first_transcript_consequence.get('protein_end', 'N/A'),
            "Amino Acids": first_transcript_consequence.get('amino_acids', 'N/A')
        }

        # Print the result for demonstration
        print("Ensembl Data:")
        for key, value in result.items():
            print(f"{key}: {value}")

        return result
    else:
        print("Not enough information in the response or structure is not as expected.")
        return None



# API



def get_genomic_coordinates(hgvs_variant):
    """
    Query Ensembl REST API for variant information based on HGVS notation.

    Parameters:
    - hgvs_variant (str): HGVS notation for the variant.

    Returns:
    - dict: Dictionary containing information about the variant. Returns None if there is not enough information
      in the response or the structure is not as expected.

    Example:
    >>> hgvs_variant = "NM_000516.7:c.601C>T"
    >>> get_genomic_coordinates(hgvs_variant)

    The function takes an HGVS variant notation as input, makes a request to the Ensembl REST API's Variant Effect
    Predictor (VEP) endpoint, and extracts relevant information about the genomic coordinates of the variant.

    The returned dictionary includes the following information:
    - 'Chromosome': Chromosome name or 'N/A' if not available.
    - 'Start': Genomic start position or 'N/A' if not available.
    - 'VariantChange': Modified variant change, excluding numeric characters, 'c.', and lowercase 'c'.

    If the response from the Ensembl API contains the expected structure, the function prints the genomic coordinates
    in the GRCh38 assembly and returns the dictionary. If the response lacks information or has an unexpected structure,
    the function prints an error message and returns None.

    Note: This function requires the 'requests' module to be installed.

    Example:
    >>> hgvs_variant = "NM_000516.7:c.601C>T"
    >>> get_genomic_coordinates(hgvs_variant)
    GRCh38 Genomic Coordinates: <Chromosome>-<Start>-<VariantChange>
    {'Chromosome': '<Chromosome>', 'Start': '<Start>', 'VariantChange': '<VariantChange>'}
    """

    # Define the Ensembl server and endpoint for the Variant Effect Predictor (VEP)
    server = "https://rest.ensembl.org"
    ext = f"/vep/human/hgvs/{hgvs_variant}?"

    # Make a GET request to the Ensembl REST API
    r = requests.get(server + ext, headers={"Content-Type": "application/json"})

    # Check if the request was successful
    if not r.ok:
        r.raise_for_status()
        sys.exit()

    # Parse the JSON response
    decoded = r.json()

    # Check if there is at least one item in the response and if 'transcript_consequences' is present
    if len(decoded) >= 1 and 'transcript_consequences' in decoded[0]:
        # Extract information from the first item in the 'transcript_consequences' list
        first_transcript_consequence = decoded[0]['transcript_consequences'][0]

        # Extract the C>T part from the HGVS variant
        variant_change = hgvs_variant.split(":")[-1]

        # Remove any numeric characters, "c.", and the lowercase 'c'
        variant_change = ''.join(c for c in variant_change if not c.isdigit() and c not in ['.', 'c'])

        # Replace ">" with "-"
        variant_change = variant_change.replace(">", "-")

        # Return information about the variant as a dictionary
        result = {
            "Chromosome": decoded[0].get('seq_region_name', 'N/A'),
            "Start": decoded[0].get('start', 'N/A'),
            "VariantChange": variant_change,
        }

        # Print the result with a hyphen between Chromosome and Start, and the modified VariantChange
        print(f"GRCh38 Genomic Coordinates: {result['Chromosome']}-{result['Start']}-{result['VariantChange']}")

        return result
    else:
        # If there is not enough information in the response or the structure is not as expected, print a message
        print("Not enough information in the response or structure is not as expected.")
        return None