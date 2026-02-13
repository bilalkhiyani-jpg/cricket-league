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
if 'players' not in st.session_state:
    st.session_state.players = []

# Master admin credentials
MASTER_ADMIN_PASSWORD = "cricket2026"

# Regular admin passwords
ADMIN_PASSWORDS = {
    "admin1": "admin123",
    "admin2": "admin456"
}

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
        
        # Get player names from session state
        player_names = [p['name'] for p in st.session_state.get('players', [])]
        if not player_names:
            st.warning("⚠️ No players registered yet. Contact admin.")
            player_names = []
        
        player_name = st.selectbox("Select Your Name", ["-- Select --"] + player_names)
        
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
                    game_time = st.time_input("Reporting Time")
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
                        st.write(f"**🕐 Reporting Time:** {game['time']}")
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
    # PAGE: PLAYERS
    # ============================================================================
    
    elif page == "Players":
        st.header("👥 Player Management")
        
        # ADMIN ONLY
        if st.session_state.user_role in ["master_admin", "admin"]:
            
            col1, col2 = st.columns([1, 1])
            
            # ADD PLAYER
            with col1:
                st.subheader("➕ Add New Player")
                with st.form("add_player"):
                    new_name = st.text_input("Player Name")
                    new_rating = st.slider("Skill Rating (1-10)", 1, 10, 5)
                    new_strength = st.selectbox("Player Strength", ["Batsman", "Bowler", "All-rounder", "Wicket Keeper"])
                    
                    if st.form_submit_button("Add Player"):
                        if new_name:
                            if any(p['name'].lower() == new_name.lower() for p in st.session_state.players):
                                st.error(f"❌ {new_name} already exists!")
                            else:
                                player = {
                                    'name': new_name,
                                    'rating': new_rating,
                                    'strength': new_strength,
                                    'matches_played': 0,
                                    'matches_won': 0,
                                    'points': 0
                                }
                                st.session_state.players.append(player)
                                st.success(f"✅ {new_name} added!")
                                st.rerun()
                        else:
                            st.error("Enter a name!")
            
            # EDIT/DELETE PLAYER
            with col2:
                st.subheader("✏️ Edit/Delete Player")
                if st.session_state.players:
                    player_names_list = [p['name'] for p in st.session_state.players]
                    selected_player = st.selectbox("Select Player", player_names_list)
                    
                    player_data = next(p for p in st.session_state.players if p['name'] == selected_player)
                    
                    with st.form("edit_player"):
                        edit_rating = st.slider("Update Rating", 1, 10, player_data['rating'])
                        edit_strength = st.selectbox(
                            "Update Strength",
                            ["Batsman", "Bowler", "All-rounder", "Wicket Keeper"],
                            index=["Batsman", "Bowler", "All-rounder", "Wicket Keeper"].index(player_data['strength'])
                        )
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.form_submit_button("💾 Update"):
                                player_data['rating'] = edit_rating
                                player_data['strength'] = edit_strength
                                st.success(f"✅ {selected_player} updated!")
                                st.rerun()
                        
                        with col_b:
                            if st.form_submit_button("🗑️ Delete"):
                                st.session_state.players = [p for p in st.session_state.players if p['name'] != selected_player]
                                st.success(f"🗑️ {selected_player} deleted!")
                                st.rerun()
                else:
                    st.info("No players to edit")
            
            # DISPLAY ALL PLAYERS
            st.markdown("---")
            st.subheader("📋 All Players")
            if st.session_state.players:
                df_data = [{
                    'Name': p['name'],
                    'Rating': p['rating'],
                    'Strength': p['strength'],
                    'Matches': p['matches_played'],
                    'Wins': p['matches_won'],
                    'Points': p['points']
                } for p in st.session_state.players]
                
                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No players yet")
        
        else:
            st.warning("⚠️ Admin access required")
    
    # ============================================================================
    # OTHER PAGES
    # ============================================================================
    
elif page == "Team Generator":
    st.header("⚖️ Team Generator")
    
    # ADMIN ONLY
    if st.session_state.user_role in ["master_admin", "admin"]:
        
        # Check if there are games and players
        if not st.session_state.games:
            st.warning("⚠️ No games created yet. Create a game first.")
        elif not st.session_state.players:
            st.warning("⚠️ No players registered yet. Add players first.")
        else:
            # STEP 1: Select game
            st.subheader("1️⃣ Select Game")
            
            game_options = [f"{g['date']} - {g['location']}" for g in st.session_state.games]
            selected_game_idx = st.selectbox("Choose game", range(len(game_options)), format_func=lambda x: game_options[x])
            selected_game = st.session_state.games[selected_game_idx]
            
            st.info(f"**Players who voted:** {len(selected_game['votes'])} players")
            if selected_game['votes']:
                st.write(", ".join(selected_game['votes']))
            
            st.markdown("---")
            
            # STEP 2: Select number of teams
            st.subheader("2️⃣ Number of Teams")
            num_teams = st.slider("How many teams?", 2, 4, 2)
            
            st.markdown("---")
            
            # STEP 3: Generate teams
            st.subheader("3️⃣ Generate Balanced Teams")
            
            if st.button("🎲 Generate Teams", type="primary"):
                # Get players who voted
                voting_players = [p for p in st.session_state.players if p['name'] in selected_game['votes']]
                
                if len(voting_players) < num_teams:
                    st.error(f"Need at least {num_teams} players! Only {len(voting_players)} voted.")
                else:
                    # Sort by rating (descending)
                    sorted_players = sorted(voting_players, key=lambda x: x['rating'], reverse=True)
                    
                    # Initialize teams
                    teams = [[] for _ in range(num_teams)]
                    team_strengths = [0] * num_teams
                    
                    # Snake draft distribution
                    for i, player in enumerate(sorted_players):
                        # Determine which team gets this player (snake pattern)
                        round_num = i // num_teams
                        if round_num % 2 == 0:
                            team_idx = i % num_teams
                        else:
                            team_idx = num_teams - 1 - (i % num_teams)
                        
                        teams[team_idx].append(player)
                        team_strengths[team_idx] += player['rating']
                    
                    # Store in session state
                    st.session_state.generated_teams = teams
                    st.session_state.team_strengths = team_strengths
                    st.session_state.selected_game_id = selected_game['id']
                    
                    st.success("✅ Teams generated!")
                    st.rerun()
            
            # STEP 4: Display and edit teams
            if 'generated_teams' in st.session_state and st.session_state.get('selected_game_id') == selected_game['id']:
                st.markdown("---")
                st.subheader("4️⃣ Review & Edit Teams")
                
                teams = st.session_state.generated_teams
                
                # Team names and captains
                team_names = []
                team_captains = []
                
                cols = st.columns(num_teams)
                
                for i in range(num_teams):
                    with cols[i]:
                        st.markdown(f"### Team {i+1}")
                        
                        # Team name
                        team_name = st.text_input(f"Team Name", value=f"Team {chr(65+i)}", key=f"team_name_{i}")
                        team_names.append(team_name)
                        
                        # Team strength
                        st.metric("Total Strength", st.session_state.team_strengths[i])
                        
                        # Captain selection
                        if teams[i]:
                            captain = st.selectbox(
                                "Captain",
                                [p['name'] for p in teams[i]],
                                key=f"captain_{i}"
                            )
                            team_captains.append(captain)
                            
                            # Display players
                            st.write("**Players:**")
                            for player in teams[i]:
                                if player['name'] == captain:
                                    st.write(f"⭐ **{player['name']}** (C) - {player['strength']} (Rating: {player['rating']})")
                                else:
                                    st.write(f"• {player['name']} - {player['strength']} (Rating: {player['rating']})")
                        else:
                            st.warning("No players in this team")
                
                # Manual adjustment section
                st.markdown("---")
                st.subheader("5️⃣ Manual Adjustments (Optional)")
                
                with st.expander("🔄 Move Players Between Teams"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Select player to move
                        all_team_players = []
                        for i, team in enumerate(teams):
                            for player in team:
                                all_team_players.append(f"{player['name']} (Team {i+1})")
                        
                        if all_team_players:
                            player_to_move = st.selectbox("Select Player", all_team_players)
                    
                    with col2:
                        # Select destination team
                        dest_team = st.selectbox("Move to Team", [f"Team {i+1}" for i in range(num_teams)])
                    
                    with col3:
                        st.write("")
                        st.write("")
                        if st.button("↔️ Move Player"):
                            # Extract player name and current team
                            player_name = player_to_move.split(" (Team")[0]
                            current_team_idx = int(player_to_move.split("Team ")[1].rstrip(")")) - 1
                            dest_team_idx = int(dest_team.split(" ")[1]) - 1
                            
                            # Find and move player
                            for player in teams[current_team_idx]:
                                if player['name'] == player_name:
                                    teams[current_team_idx].remove(player)
                                    teams[dest_team_idx].append(player)
                                    
                                    # Recalculate strengths
                                    st.session_state.team_strengths[current_team_idx] -= player['rating']
                                    st.session_state.team_strengths[dest_team_idx] += player['rating']
                                    
                                    st.success(f"✅ Moved {player_name}")
                                    st.rerun()
                                    break
                
                # Save teams button
                st.markdown("---")
                if st.button("💾 Finalize Teams", type="primary"):
                    # Store finalized teams with names and captains
                    finalized_teams = []
                    for i in range(num_teams):
                        finalized_teams.append({
                            'name': team_names[i],
                            'captain': team_captains[i] if i < len(team_captains) else None,
                            'players': [p['name'] for p in teams[i]],
                            'strength': st.session_state.team_strengths[i]
                        })
                    
                    # Store for match results
                    st.session_state.finalized_teams = finalized_teams
                    st.session_state.finalized_game_id = selected_game['id']
                    
                    st.success("✅ Teams finalized! Go to Match Results to record the game.")
                    st.balloons()
    
    else:
        st.warning("⚠️ Admin access required")
    
    elif page == "Match Results":
        st.header("📊 Match Results")
        st.info("Coming in next step...")
    
    elif page == "Leaderboard":
        st.header("🏆 Leaderboard")
        st.info("Coming in next step...")
