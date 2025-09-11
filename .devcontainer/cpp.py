import plotly.express as px

# …inside your if moods: block after df['sentiment'] is computed

# map sentiment to emoji for hover info
def sentiment_to_emoji(s):
    if s < -0.2:
        return "😢"
    elif s < 0.2:
        return "😐"
    else:
        return "😄"

df['emoji'] = df['sentiment'].apply(sentiment_to_emoji)

st.markdown("<div class='glass'><h3>📜 My Mood History</h3>", unsafe_allow_html=True)
for _, row in df[::-1].iterrows():
    st.markdown(f"{row['emoji']} **{row['created_at'].strftime('%Y-%m-%d %H:%M')}** — {row['mood_text']}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='glass'><h3>📊 Mood Trend (Interactive)</h3>", unsafe_allow_html=True)
fig = px.scatter(
    df,
    x='created_at',
    y='sentiment',
    text='emoji',
    color='sentiment',
    color_continuous_scale=['red','orange','yellow','green'],
    labels={'sentiment':'Sentiment Score','created_at':'Date'},
    title='Mood Sentiment Over Time'
)
fig.update_traces(textposition='top center', marker=dict(size=12))
fig.update_layout(yaxis=dict(range=[-1,1]))
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
