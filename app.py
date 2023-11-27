import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

# Set up Streamlit page configuration
# st.set_page_config(layout='wide')

# Create the sidebar with project information
st.sidebar.title('🎈 ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. For more information, read the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')

# Define a function to render the molecular structure using stmol and py3Dmol
def render_mol(pdb):
    pdbview = py3Dmol.view()
    pdbview.addModel(pdb, 'pdb')
    pdbview.setStyle({'cartoon': {'color': 'spectrum'}})
    pdbview.setBackgroundColor('white')  # ('0xeeeeee')
    pdbview.zoomTo()
    pdbview.zoom(2, 800)
    pdbview.spin(True)
    showmol(pdbview, height=500, width=800)

# Default protein sequence
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)

# Function to update the prediction and display results
def update(sequence=txt):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    # Make a request to the ESMFold API to get the predicted PDB structure
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    # Save the predicted PDB structure to a file
    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)

    # Load the structure using biotite for additional analysis
    struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    b_value = round(struct.b_factor.mean(), 4)

    # Display the protein structure using stmol and py3Dmol
    st.subheader('Visualization of predicted protein structure')
    render_mol(pdb_string)

    # Display plDDT value, which is stored in the B-factor field
    st.subheader('plDDT')
    st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
    st.info(f'plDDT: {b_value}')

    # Add a download button for the predicted PDB file
    st.download_button(
        label="Download PDB",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain',
    )

# Button to trigger the prediction
predict = st.sidebar.button('Predict', on_click=update)

# Display a warning if the user has not entered a protein sequence
if not predict:
    st.warning('👈 Enter protein sequence data!')
