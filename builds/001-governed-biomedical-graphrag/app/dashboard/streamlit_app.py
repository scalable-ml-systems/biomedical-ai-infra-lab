import streamlit as st

st.set_page_config(
    page_title="Governed Biomedical GraphRAG",
    page_icon="🧬",
    layout="wide",
)

st.title("Governed Biomedical GraphRAG Pipeline")
st.subheader("Medical RAG Is Broken Without Evidence Contracts")

st.warning(
    "Educational and technical demo only. "
    "This is not medical advice, diagnosis, treatment, or clinical decision support."
)

st.markdown(
    """
This build demonstrates a governed biomedical GraphRAG pipeline with:

- RxNorm drug normalization
- DailyMed drug-label retrieval
- PubMed literature retrieval
- vector search
- graph relationship validation
- evidence contracts
- strict safety checks
- audit logging
"""
)

query = st.text_area(
    "Enter a safe educational drug-label or biomedical evidence question",
    value="What does the official label say about warnings and precautions for warfarin?",
    height=100,
)

submit = st.button("Run governed evidence query")

if submit:
    st.info("Backend integration will be added in a later step.")

    st.markdown("## Placeholder evidence trace")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Normalized drug entities")
        st.code("warfarin")

        st.markdown("### Retrieved DailyMed evidence")
        st.code("Placeholder: warnings and precautions section")

        st.markdown("### Retrieved PubMed evidence")
        st.code("Placeholder: PubMed abstracts")

    with col2:
        st.markdown("### Graph paths")
        st.code("Placeholder: Drug → HAS_WARNING → Warning → SUPPORTED_BY → LabelSection")

        st.markdown("### Validation result")
        st.success("Placeholder: citation validation pending")

        st.markdown("### Safety result")
        st.success("Placeholder: safe educational query")

    st.markdown("### Final answer")
    st.write("Placeholder answer will appear here after backend integration.")

    st.markdown("### Audit trace")
    st.code("Placeholder audit_id: audit_placeholder")
