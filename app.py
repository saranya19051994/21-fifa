import streamlit as st
import pickle
import pandas as pd

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# Function to load the models and encoders
def load_pickle(file_name):
    with open(file_name, "rb") as file:
        return pickle.load(file)

# Load the models
model_GK = load_pickle("model_GK.pkl")
model_FW = load_pickle("model_FW.pkl")
model_DEF = load_pickle("model_DEF.pkl")
model_MID = load_pickle("model_MID.pkl")

# Load encoders
body_type_mid = load_pickle("body_type_mid.pkl")
work_rate_mid = load_pickle("work_rate_mid.pkl")
preferred_foot_mid = load_pickle("preferred_foot_mid.pkl")

body_type_gk = load_pickle("body_typegk.pkl")

body_type_fw = load_pickle("body_type.pkl")
work_rate_fw = load_pickle("work_rate.pkl")

body_type_def = load_pickle("body_type_def.pkl")
work_rate_def = load_pickle("work_rate_def.pkl")

# Helper function to predict rating
def predict(model, features):
    df = pd.DataFrame([features])
    return model.predict(df.values)[0]

st.title("Player Position Rating Prediction")

position = st.sidebar.selectbox("Select Player Position", ["Goalkeeper", "Forward", "Defender", "Midfielder"])

if position == "Goalkeeper":
    st.header("Goalkeeper Input")
    league_rank = st.number_input("League Rank", min_value=1.0, step=1.0)
    international_reputation = st.number_input("International Reputation", min_value=1, step=1)
    weak_foot = st.number_input("Weak Foot", min_value=1, step=1)
    body_type = st.selectbox("Body Type", body_type_gk.classes_)
    movement_reactions = st.number_input("Movement Reactions", min_value=1, step=1)
    power_shot_power = st.number_input("Power Shot Power", min_value=1, step=1)
    GK_attribute = st.number_input("GK Attribute", min_value=1, step=1)
    
    if st.button("Predict Rating"):
        features = [league_rank, international_reputation, weak_foot, body_type_gk.transform([body_type])[0], movement_reactions, power_shot_power, GK_attribute]
        rating = predict(model_GK, features)
        st.write(f"Predicted Rating: {rating}")

elif position == "Forward":
    st.header("Forward Input")
    league_rank = st.number_input("League Rank", min_value=1.0, step=1.0)
    international_reputation = st.number_input("International Reputation", min_value=1, step=1)
    weak_foot = st.number_input("Weak Foot", min_value=1, step=1)
    skill_moves = st.number_input("Skill Moves", min_value=1, step=1)
    work_rate = st.selectbox("Work Rate", work_rate_fw.classes_)
    body_type = st.selectbox("Body Type", body_type_fw.classes_)
    attacking_short_passing = st.number_input("Attacking Short Passing", min_value=1, step=1)
    attacking_volleys = st.number_input("Attacking Volleys", min_value=1, step=1)
    skill_ball_control = st.number_input("Skill Ball Control", min_value=1, step=1)
    movement_reactions = st.number_input("Movement Reactions", min_value=1, step=1)
    power_shot_power = st.number_input("Power Shot Power", min_value=1, step=1)
    power_long_shots = st.number_input("Power Long Shots", min_value=1, step=1)
    mentality_positioning = st.number_input("Mentality Positioning", min_value=1, step=1)
    mentality_composure = st.number_input("Mentality Composure", min_value=1, step=1)
    shooting = st.number_input("Shooting", min_value=1.0, step=1.0)
    passing = st.number_input("Passing", min_value=1.0, step=1.0)
    dribbling = st.number_input("Dribbling", min_value=1.0, step=1.0)
    
    if st.button("Predict Rating"):
        features = [league_rank, international_reputation, weak_foot, skill_moves, work_rate_fw.transform([work_rate])[0], body_type_fw.transform([body_type])[0], attacking_short_passing,
                    attacking_volleys, skill_ball_control, movement_reactions, power_shot_power, power_long_shots, mentality_positioning,
                    mentality_composure, shooting, passing, dribbling]
        rating = predict(model_FW, features)
        st.write(f"Predicted Rating: {rating}")

elif position == "Defender":
    st.header("Defender Input")
    league_rank = st.number_input("League Rank", min_value=1.0, step=1.0)
    international_reputation = st.number_input("International Reputation", min_value=1, step=1)
    weak_foot = st.number_input("Weak Foot", min_value=1, step=1)
    work_rate = st.selectbox("Work Rate", work_rate_def.classes_)
    body_type = st.selectbox("Body Type", body_type_def.classes_)
    attacking_heading_accuracy = st.number_input("Attacking Heading Accuracy", min_value=1, step=1)
    attacking_short_passing = st.number_input("Attacking Short Passing", min_value=1, step=1)
    skill_ball_control = st.number_input("Skill Ball Control", min_value=1, step=1)
    movement_reactions = st.number_input("Movement Reactions", min_value=1, step=1)
    mentality_interceptions = st.number_input("Mentality Interceptions", min_value=1, step=1)
    mentality_composure = st.number_input("Mentality Composure", min_value=1, step=1)
    defending_sliding_tackle = st.number_input("Defending Sliding Tackle", min_value=1, step=1)
    passing = st.number_input("Passing", min_value=1.0, step=1.0)
    defending = st.number_input("Defending", min_value=1.0, step=1.0)
    physic = st.number_input("Physic", min_value=1.0, step=1.0)
    dribbling = st.number_input("Dribbling", min_value=1.0, step=1.0)
    
    if st.button("Predict Rating"):
        features = [league_rank, international_reputation, weak_foot, work_rate_def.transform([work_rate])[0], body_type_def.transform([body_type])[0], attacking_heading_accuracy, attacking_short_passing,
                    skill_ball_control, movement_reactions, mentality_interceptions, mentality_composure, defending_sliding_tackle, passing, defending, physic, dribbling]
        rating = predict(model_DEF, features)
        st.write(f"Predicted Rating: {rating}")

elif position == "Midfielder":
    st.header("Midfielder Input")
    league_rank = st.number_input("League Rank", min_value=1.0, step=1.0)
    international_reputation = st.number_input("International Reputation", min_value=1, step=1)
    weak_foot = st.number_input("Weak Foot", min_value=1, step=1)
    skill_moves = st.number_input("Skill Moves", min_value=1, step=1)
    work_rate = st.selectbox("Work Rate", work_rate_mid.classes_)
    body_type = st.selectbox("Body Type", body_type_mid.classes_)
    preferred_foot = st.selectbox("Preferred Foot", preferred_foot_mid.classes_)
    attacking_short_passing = st.number_input("Attacking Short Passing", min_value=1, step=1)
    skill_dribbling = st.number_input("Skill Dribbling", min_value=1, step=1)
    skill_long_passing = st.number_input("Skill Long Passing", min_value=1, step=1)
    skill_ball_control = st.number_input("Skill Ball Control", min_value=1, step=1)
    movement_reactions = st.number_input("Movement Reactions", min_value=1, step=1)
    power_long_shots = st.number_input("Power Long Shots", min_value=1, step=1)
    mentality_composure = st.number_input("Mentality Composure", min_value=1, step=1)
    shooting = st.number_input("Shooting", min_value=1.0, step=1.0)
    passing = st.number_input("Passing", min_value=1.0, step=1.0)
    dribbling = st.number_input("Dribbling", min_value=1.0, step=1.0)
    
    if st.button("Predict Rating"):
        features = [league_rank, international_reputation, weak_foot, skill_moves, work_rate_mid.transform([work_rate])[0], body_type_mid.transform([body_type])[0], preferred_foot_mid.transform([preferred_foot])[0], attacking_short_passing, skill_dribbling,
                    skill_long_passing, skill_ball_control, movement_reactions, power_long_shots, mentality_composure, shooting, passing, dribbling]
        rating = predict(model_MID, features)
        st.write(f"Predicted Rating: {rating}")
