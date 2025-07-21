import streamlit as st
import pandas as pd

st.set_page_config(page_title="DeFi Transaction Identifier", layout="wide")

st.title("🔍 DeFi Transaction Identifier")
st.write("Upload your transaction export CSV file below. This tool will match your transactions to known DeFi protocol addresses and identify related protocols and chains.")

uploaded_file = st.file_uploader("Upload Transaction CSV", type=["csv"])

@st.cache_data
def load_defi_data():
    return pd.read_csv("data/defi_protocols.csv")

defi_df = load_defi_data()
defi_df['contract_address'] = defi_df['contract_address'].str.lower()

if uploaded_file:
    txn_df = pd.read_csv(uploaded_file)
    txn_df['from'] = txn_df['from'].str.lower()
    txn_df['to'] = txn_df['to'].str.lower()

    from_matches = txn_df.merge(defi_df, left_on='from', right_on='contract_address', how='inner')
    from_matches['matched_field'] = 'from'

    to_matches = txn_df.merge(defi_df, left_on='to', right_on='contract_address', how='inner')
    to_matches['matched_field'] = 'to'

    defi_txns = pd.concat([from_matches, to_matches], ignore_index=True)
    defi_txns = defi_txns.drop_duplicates(subset=['id', 'matched_field'])

    result_cols = [
        'id', 'dateTime', 'operation', 'from', 'to', 'amount', 'asset',
        'walletName', 'chain', 'protocol', 'matched_field', 'explorerLink'
    ]
    defi_txns_display = defi_txns[result_cols]

    st.success(f"Found {len(defi_txns_display)} DeFi-related transactions.")
    st.dataframe(defi_txns_display, use_container_width=True)

    csv = defi_txns_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv,
        file_name='defi_related_transactions.csv',
        mime='text/csv'
    )
else:
    st.info("Awaiting transaction CSV upload.")