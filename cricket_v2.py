
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

# Master admin credentials (only you)
MASTER_ADMIN_PASSWORD = "cricket2026"  # Change this to your secret password

# Regular admin passwords (you assign these)
ADMIN_PASSWORDS = {
    "admin1": "admin123",  # Example admin
    "admin2": "admin456"   # Example admin
}

# ============================================================================
# LOGIN PAGE
# ============================================================================

if not st.session_state.authenticated:
    st.title("🏏 PK Expat Cricket League")
    st.markdown("---")
    
    # Login tabs
    tab1, tab2, tab3 = st.tabs(["🔐 Master Admin", "👨‍💼 Admin Login", "👤 Player Access"])
    
    # MASTER ADMIN LOGIN
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
    
    # REGULAR ADMIN LOGIN
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
    
    # PLAYER ACCESS (no password, just name selection)
    with tab3:
        st.subheader("Player Access")
        st.info("Select your name if you're a registered player")
        
        # Dummy player list for now (will come from database later)
        dummy_players = ["Adnan", "Ahmed", "Ali", "Hassan", "Kamran", "Usman"]
        
        player_name = st.selectbox("Select Your Name", ["-- Select --"] + dummy_players)
        
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
        st.write(f"**Logged in as:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role}")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.session_state.username = None
            st.rerun()
    
    st.markdown("---")
    
    # Show different content based on role
    if st.session_state.user_role == "master_admin":
        st.success("🔑 Master Admin Panel")
        st.write("You have full control of the system")
        st.write("Features coming next:")
        st.write("- Manage admins")
        st.write("- Manage players")
        st.write("- Create games")
        st.write("- Generate teams")
        st.write("- Record results")
    
    elif st.session_state.user_role == "admin":
        st.info("👨‍💼 Admin Panel")
        st.write("You can:")
        st.write("- Manage players")
        st.write("- Create games")
        st.write("- Generate teams")
        st.write("- Record results")
    
    elif st.session_state.user_role == "player":
        st.info("👤 Player View")
        st.write("You can:")
        st.write("- View upcoming games")
        st.write("- Vote for games you want to join")
        st.write("- View leaderboard")
