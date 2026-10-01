# Ethics and Responsible AI Note

**Privacy.** Meeting transcripts can contain names, business details, and sensitive discussion. This project uses only synthetic transcripts or publicly available ones (for example, public government meetings), never real private meetings. Real use would require consent from all participants.

**Data handling.** Transcripts sent to the OpenAI API fall under OpenAI's API data policies. Embeddings stored in Pinecone are derived from the same text and carry the same sensitivity. The demo stores only sample data, and a delete-all function removes stored vectors. Outputs from real meetings are gitignored and never committed.

**Accuracy and over-trust.** A wrong decision or invented owner could lead someone to act on false information. Mitigations: every decision includes a source quote verified by code, owners are null when unstated, answers cite their source meeting, and the README states that outputs must be checked against the transcript.

**Bias and fairness.** Extraction quality may vary with informal phrasing, non-standard English, or errors from automatic transcription. The eval set includes varied styles, and known limitations are documented in the final report.

**Transparency.** The app states that outputs are AI-generated and may contain errors.

**Limitations.** Not designed for legal, compliance, or medical meeting records.
