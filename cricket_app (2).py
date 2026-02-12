
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Saturday Cricket League", page_icon="🏏", layout="wide")

# Initialize session state
if 'players' not in st.session_state:
    st.session_state.players = []
if 'matches' not in st.session_state:
    st.session_state.matches = []

# Title
st.title("🏏 Saturday Cricket League")
st.markdown("---")

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["Players", "Team Generator", "Match Results", "Leaderboard"])

# ============================================================================
# PAGE 1: PLAYERS (with edit/delete)
# ============================================================================

if page == "Players":
    st.header("👥 Player Management")
    
    col1, col2 = st.columns([1, 1])
    
    # ADD PLAYER
    with col1:
        st.subheader("➕ Add New Player")
        with st.form("add_player_form"):
            new_name = st.text_input("Player Name")
            new_rating = st.slider("Skill Rating (1-10)", 1, 10, 5, help="1 = Beginner, 10 = Expert")
            new_strength = st.selectbox("Player Strength", ["Batsman", "Bowler", "All-rounder", "Wicket Keeper"])
            
            if st.form_submit_button("Add Player"):
                if new_name:
                    # Check if player already exists
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
            player_names = [p['name'] for p in st.session_state.players]
            selected_player = st.selectbox("Select Player", player_names)
            
            # Get player data
            player_data = next(p for p in st.session_state.players if p['name'] == selected_player)
            
            with st.form("edit_player_form"):
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
                    if st.form_submit_button("🗑️ Delete", type="secondary"):
                        st.session_state.players = [p for p in st.session_state.players if p['name'] != selected_player]
                        st.success(f"🗑️ {selected_player} deleted!")
                        st.rerun()
        else:
            st.info("No players to edit. Add players first!")
    
    # DISPLAY ALL PLAYERS
    st.markdown("---")
    st.subheader("📋 All Players")
    if st.session_state.players:
        # Create dataframe with custom order
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
        st.info("No players yet. Add some above!")

# ============================================================================
# PAGE 2: TEAM GENERATOR
# ============================================================================

elif page == "Team Generator":
    st.header("⚖️ Balanced Team Generator")
    
    if len(st.session_state.players) < 2:
        st.warning("⚠️ Add at least 2 players first!")
    else:
        st.write(f"**Total registered players:** {len(st.session_state.players)}")
        
        # Select playing players
        playing_today = st.multiselect(
            "👥 Who's playing today?",
            options=[p['name'] for p in st.session_state.players],
            default=[p['name'] for p in st.session_state.players]
        )
        
        if st.button("🎲 Generate Balanced Teams", type="primary"):
            if len(playing_today) < 2:
                st.error("Need at least 2 players!")
            else:
                # Get selected players with ratings
                selected = [p for p in st.session_state.players if p['name'] in playing_today]
                selected_sorted = sorted(selected, key=lambda x: x['rating'], reverse=True)
                
                # Balance teams (snake draft)
                team_a = []
                team_b = []
                
                for i, player in enumerate(selected_sorted):
                    if i % 2 == 0:
                        team_a.append(player)
                    else:
                        team_b.append(player)
                
                # Calculate strengths
                strength_a = sum(p['rating'] for p in team_a)
                strength_b = sum(p['rating'] for p in team_b)
                
                # Display teams
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🔴 Team A")
                    st.metric("Total Strength", strength_a)
                    for p in team_a:
                        st.write(f"• **{p['name']}** - {p['strength']} (Rating: {p['rating']})")
                
                with col2:
                    st.markdown("### 🔵 Team B")
                    st.metric("Total Strength", strength_b)
                    for p in team_b:
                        st.write(f"• **{p['name']}** - {p['strength']} (Rating: {p['rating']})")
                
                diff = abs(strength_a - strength_b)
                if diff <= 2:
                    st.success(f"⚖️ Perfectly balanced! Difference: {diff} points")
                else:
                    st.info(f"⚖️ Teams difference: {diff} points")

# ============================================================================
# PAGE 3: MATCH RESULTS
# ============================================================================

elif page == "Match Results":
    st.header("📊 Record Match Result")
    
    if len(st.session_state.players) < 2:
        st.warning("Add players first!")
    else:
        st.subheader("🏏 Enter Match Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔴 Team A Players:**")
            team_a_players = st.multiselect(
                "Select Team A",
                options=[p['name'] for p in st.session_state.players],
                key="team_a"
            )
        
        with col2:
            st.write("**🔵 Team B Players:**")
            team_b_players = st.multiselect(
                "Select Team B",
                options=[p['name'] for p in st.session_state.players],
                key="team_b"
            )
        
        winner = st.radio("🏆 Who won?", ["Team A", "Team B"])
        
        if st.button("💾 Record Match", type="primary"):
            if not team_a_players or not team_b_players:
                st.error("Both teams need players!")
            elif set(team_a_players) & set(team_b_players):
                st.error("Same player can't be in both teams!")
            else:
                # Record match
                match = {
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'team_a': team_a_players,
                    'team_b': team_b_players,
                    'winner': winner
                }
                st.session_state.matches.append(match)
                
                # Update player stats
                winning_team = team_a_players if winner == "Team A" else team_b_players
                all_players = team_a_players + team_b_players
                
                for player in st.session_state.players:
                    if player['name'] in all_players:
                        player['matches_played'] += 1
                        if player['name'] in winning_team:
                            player['matches_won'] += 1
                            player['points'] += 1
                
                st.success(f"✅ Match recorded! {winner} wins! 🏆")
                st.balloons()
        
        # Show match history
        if st.session_state.matches:
            st.markdown("---")
            st.subheader("📜 Recent Matches")
            for i, match in enumerate(reversed(st.session_state.matches[-5:]), 1):
                with st.expander(f"Match {len(st.session_state.matches) - i + 1} - {match['date']} - Winner: {match['winner']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Team A:**")
                        st.write(", ".join(match['team_a']))
                    with col2:
                        st.write("**Team B:**")
                        st.write(", ".join(match['team_b']))

# ============================================================================
# PAGE 4: LEADERBOARD
# ============================================================================

elif page == "Leaderboard":
    st.header("🏆 Player Leaderboard")
    
    if not st.session_state.players:
        st.info("No players yet!")
    else:
        # Sort by points
        leaderboard = sorted(st.session_state.players, key=lambda x: x['points'], reverse=True)
        
        # Top 3 podium
        if len(leaderboard) > 0:
            st.subheader("🏅 Top 3 Players")
            col1, col2, col3 = st.columns(3)
            
            if len(leaderboard) > 0:
                with col1:
                    st.metric("🥇 1st Place", leaderboard[0]['name'], f"{leaderboard[0]['points']} pts")
            if len(leaderboard) > 1:
                with col2:
                    st.metric("🥈 2nd Place", leaderboard[1]['name'], f"{leaderboard[1]['points']} pts")
            if len(leaderboard) > 2:
                with col3:
                    st.metric("🥉 3rd Place", leaderboard[2]['name'], f"{leaderboard[2]['points']} pts")
        
        # Full leaderboard
        st.markdown("---")
        st.subheader("📊 Complete Rankings")
        
        lb_data = []
        for i, player in enumerate(leaderboard, 1):
            win_rate = (player['matches_won'] / player['matches_played'] * 100) if player['matches_played'] > 0 else 0
            lb_data.append({
                'Rank': f"#{i}",
                'Player': player['name'],
                'Strength': player['strength'],
                'Points': player['points'],
                'Matches': player['matches_played'],
                'Wins': player['matches_won'],
                'Win Rate': f"{win_rate:.1f}%",
                'Rating': player['rating']
            })
        
        df = pd.DataFrame(lb_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# SIDEBAR STATS
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.metric("👥 Total Players", len(st.session_state.players))
st.sidebar.metric("🏏 Matches Played", len(st.session_state.matches))

if st.session_state.players:
    total_points = sum(p['points'] for p in st.session_state.players)
    st.sidebar.metric("🎯 Total Points Awarded", total_points)
