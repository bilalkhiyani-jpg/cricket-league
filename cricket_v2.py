import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="PK Expat Cricket", page_icon="🏏", layout="wide")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'games' not in st.session_state:
    st.session_state.games = []

# Master admin credentials
MASTER_ADMIN_PASSWORD = "cricket2026"

# Regular admin passwords
ADMIN_PASSWORDS = {
    "admin1": "admin123",
    "admin2": "admin456"
}

# Dummy player list (will be dynamic later)
PLAYER_LIST = ["Adnan", "Ahmed", "Ali", "Hassan", "Kamran", "Usman", "Bilal", "Fahad"]

# ============================================================================
# LOGIN PAGE
# ============================================================================

if not st.session_state.authenticated:
    st.title("🏏 PK Expat Cricket League")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔐 Master Admin", "👨‍💼 Admin Login", "👤 Player Access"])
    
    # MASTER ADMIN
    with tab1:
        st.subheader("Master Admin Login")
        master_password = st.text_input("Master Password", type="password", key="master_pwd")
        
        if st.button("Login as Master Admin"):
            if master_password == MASTER_ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.user_role = "master_admin"
                st.session_state.username = "Master Admin"
                st.success("✅ Master Admin access granted!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    # REGULAR ADMIN
    with tab2:
        st.subheader("Admin Login")
        admin_name = st.selectbox("Select Admin", list(ADMIN_PASSWORDS.keys()))
        admin_password = st.text_input("Password", type="password", key="admin_pwd")
        
        if st.button("Login as Admin"):
            if admin_password == ADMIN_PASSWORDS[admin_name]:
                st.session_state.authenticated = True
                st.session_state.user_role = "admin"
                st.session_state.username = admin_name
                st.success(f"✅ Welcome {admin_name}!")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    
    # PLAYER ACCESS
    with tab3:
        st.subheader("Player Access")
        st.info("Select your name if you're a registered player")
        
        player_name = st.selectbox("Select Your Name", ["-- Select --"] + PLAYER_LIST)
        
        if st.button("Continue as Player"):
            if player_name != "-- Select --":
                st.session_state.authenticated = True
                st.session_state.user_role = "player"
                st.session_state.username = player_name
                st.success(f"✅ Welcome {player_name}!")
                st.rerun()
            else:
                st.error("❌ Please select your name")

# ============================================================================
# MAIN APP (after login)
# ============================================================================

else:
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🏏 PK Expat Cricket League")
    with col2:
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role}")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()
    
    st.markdown("---")
    
    # Navigation based on role
    if st.session_state.user_role in ["master_admin", "admin"]:
        page = st.sidebar.radio("Navigate", ["Upcoming Games", "Players", "Team Generator", "Match Results", "Leaderboard"])
    else:  # player
        page = st.sidebar.radio("Navigate", ["Upcoming Games", "Leaderboard"])
    
    # ============================================================================
    # PAGE: UPCOMING GAMES
    # ============================================================================
    
    if page == "Upcoming Games":
        st.header("📅 Upcoming Games")
        
        # ADMIN - Create games
        if st.session_state.user_role in ["master_admin", "admin"]:
            st.subheader("➕ Create New Game")
            
            with st.form("create_game"):
                col1, col2 = st.columns(2)
                
                with col1:
                    game_date = st.date_input("Date")
                    game_time = st.time_input("Time")
                    location = st.text_input("Location", placeholder="e.g., Central Park")
                
                with col2:
                    game_type = st.selectbox("Type", ["Internal", "External"])
                    max_players = st.number_input("Max Players", min_value=10, max_value=50, value=20)
                
                if st.form_submit_button("Create Game"):
                    game = {
                        'id': len(st.session_state.games) + 1,
                        'date': str(game_date),
                        'time': str(game_time),
                        'location': location,
                        'type': game_type,
                        'max_players': max_players,
                        'votes': [],
                        'created_by': st.session_state.username
                    }
                    st.session_state.games.append(game)
                    st.success(f"✅ Game created!")
                    st.rerun()
            
            st.markdown("---")
        
        # ALL USERS - View and vote
        if st.session_state.games:
            st.subheader("🏏 Scheduled Games")
            
            for game in st.session_state.games:
                with st.expander(f"🏏 {game['date']} - {game['location']} ({game['type']})"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**📍 Location:** {game['location']}")
                        st.write(f"**🕐 Time:** {game['time']}")
                        st.write(f"**👥 Capacity:** {len(game['votes'])}/{game['max_players']}")
                    
                    with col2:
                        if game['votes']:
                            st.write("**Players In:**")
                            for player in game['votes']:
                                st.write(f"✅ {player}")
                        else:
                            st.info("No votes yet")
                    
                    with col3:
                        # PLAYER VOTING
                        if st.session_state.user_role == "player":
                            player_name = st.session_state.username
                            
                            if player_name in game['votes']:
                                st.success("✅ You're in!")
                                if st.button("❌ Cancel", key=f"cancel_{game['id']}"):
                                    game['votes'].remove(player_name)
                                    st.rerun()
                            else:
                                if st.button("✅ I'm In!", key=f"join_{game['id']}"):
                                    if len(game['votes']) < game['max_players']:
                                        game['votes'].append(player_name)
                                        st.rerun()
                                    else:
                                        st.error("Game is full!")
                        
                        # ADMIN - Delete game
                        if st.session_state.user_role in ["master_admin", "admin"]:
                            if st.button("🗑️ Delete", key=f"delete_{game['id']}"):
                                st.session_state.games = [g for g in st.session_state.games if g['id'] != game['id']]
                                st.rerun()
        else:
            st.info("No games scheduled yet")
    
    # ============================================================================
    # OTHER PAGES (placeholders)
    # ============================================================================
    
    elif page == "Players":
        st.header("👥 Players")
        st.info("Coming in next step...")
    
    elif page == "Team Generator":
        st.header("⚖️ Team Generator")
        st.info("Coming in next step...")
    
    elif page == "Match Results":
        st.header("📊 Match Results")
        st.info("Coming in next step...")
    
    elif page == "Leaderboard":
        st.header("🏆 Leaderboard")
        st.info("Coming in next step...")
