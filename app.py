"""Interactive LLM evaluation scorecard."""

import pandas as pd
import plotly.express as px
import streamlit as st

from evaluation import evaluate, make_demo_judgments, paired_model_differences, slice_scorecard, validate_judgments


st.set_page_config(page_title="LLM Evaluation Lab", page_icon="🧪", layout="wide", initial_sidebar_state="collapsed")
st.title("LLM Evaluation Lab")
st.caption("Quality, reliability, latency, cost, and failure-mode analysis · synthetic model labels and seeded judgments")

uploaded = st.sidebar.file_uploader("Upload labeled judgments", type="csv")
judgments = pd.read_csv(uploaded) if uploaded else make_demo_judgments()
quality = validate_judgments(judgments)
domains = sorted(judgments["domain"].unique())
selected_domains = st.sidebar.multiselect("Domains", domains, default=domains)
filtered = judgments.loc[judgments["domain"].isin(selected_domains)]
summary, errors, agreement = evaluate(filtered)

best = summary.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Best accuracy · {best['model']}", f"{best['accuracy']:.1%}")
c2.metric("Rater agreement", f"κ {agreement['cohen_kappa']:.2f}")
c3.metric("Evaluated items", quality["items"])
c4.metric("Models", quality["models"])

left, right = st.columns(2)
with left:
    st.subheader("Accuracy with 95% bootstrap intervals")
    figure = px.scatter(summary, x="accuracy", y="model", error_x=summary["ci_high"] - summary["accuracy"], error_x_minus=summary["accuracy"] - summary["ci_low"], color="model", range_x=[0, 1])
    figure.update_layout(showlegend=False, xaxis_tickformat=".0%", xaxis_title="Accuracy", yaxis_title=None)
    st.plotly_chart(figure, width="stretch")
with right:
    st.subheader("Quality–cost frontier")
    figure = px.scatter(summary, x="cost_per_correct", y="accuracy", size="median_latency_ms", color="model", text="model", labels={"cost_per_correct": "Cost per correct response ($)", "accuracy": "Accuracy", "median_latency_ms": "Median latency (ms)"})
    figure.update_traces(textposition="top center")
    figure.update_yaxes(tickformat=".0%")
    st.plotly_chart(figure, width="stretch")

st.subheader("Performance by domain and difficulty")
slices = slice_scorecard(filtered)
heatmap = px.density_heatmap(slices, x="difficulty", y="model", z="accuracy", facet_col="domain", histfunc="avg", text_auto=".0%", color_continuous_scale="Blues", range_color=[0, 1])
heatmap.update_layout(coloraxis_colorbar_tickformat=".0%")
st.plotly_chart(heatmap, width="stretch")

left, right = st.columns(2)
with left:
    st.subheader("Error taxonomy")
    st.plotly_chart(px.bar(errors, x="error_type", y="errors", color="model", barmode="group"), width="stretch")
with right:
    st.subheader("Paired model comparisons")
    comparisons = paired_model_differences(filtered)
    st.dataframe(comparisons, hide_index=True, width="stretch")

st.info("Select a model only after defining the use case's primary quality metric, maximum latency/cost, safety constraints, and adjudication process. Aggregate accuracy alone is not a deployment decision.")
st.download_button("Download filtered judgments", filtered.to_csv(index=False), "llm_judgments.csv", "text/csv")
