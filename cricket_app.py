
import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page config
st.set_page_config(page_title="Saturday Cricket League", page_icon="🏏", layout="wide")

# Initialize session state for data storage
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
# PAGE 1: PLAYERS
# ============================================================================

if page == "Players":
    st.header("👥 Player Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Player")
        name = st.text_input("Player Name")
        rating = st.slider("Skill Rating (1-10)", 1, 10, 5)
        
        if st.button("Add Player"):
            if name:
                player = {
                    'name': name,
                    'rating': rating,
                    'matches_played': 0,
                    'matches_won': 0,
                    'points': 0
                }
                st.session_state.players.append(player)
                st.success(f"✅ {name} added!")
            else:
                st.error("Enter a name")
    
    with col2:
        st.subheader("Current Players")
        if st.session_state.players:
            df = pd.DataFrame(st.session_state.players)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No players yet. Add some!")

# ============================================================================
# PAGE 2: TEAM GENERATOR
# ============================================================================

elif page == "Team Generator":
    st.header("⚖️ Balanced Team Generator")
    
    if len(st.session_state.players) < 2:
        st.warning("Add at least 2 players first!")
    else:
        st.write(f"Total players: {len(st.session_state.players)}")
        
        # Select playing players
        playing_today = st.multiselect(
            "Who's playing today?",
            options=[p['name'] for p in st.session_state.players],
            default=[p['name'] for p in st.session_state.players]
        )
        
        if st.button("Generate Balanced Teams"):
            if len(playing_today) < 2:
                st.error("Need at least 2 players")
            else:
                # Get selected players with ratings
                selected = [p for p in st.session_state.players if p['name'] in playing_today]
                selected_sorted = sorted(selected, key=lambda x: x['rating'], reverse=True)
                
                # Balance teams (snake draft style)
                team_a = []
                team_b = []
                
                for i, player in enumerate(selected_sorted):
                    if i % 2 == 0:
                        team_a.append(player)
                    else:
                        team_b.append(player)
                
                # Calculate team strengths
                strength_a = sum(p['rating'] for p in team_a)
                strength_b = sum(p['rating'] for p in team_b)
                
                # Display teams
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔴 Team A")
                    st.write(f"**Total Strength:** {strength_a}")
                    for p in team_a:
                        st.write(f"• {p['name']} (Rating: {p['rating']})")
                
                with col2:
                    st.subheader("🔵 Team B")
                    st.write(f"**Total Strength:** {strength_b}")
                    for p in team_b:
                        st.write(f"• {p['name']} (Rating: {p['rating']})")
                
                st.info(f"⚖️ Difference: {abs(strength_a - strength_b)} points")

# ============================================================================
# PAGE 3: MATCH RESULTS
# ============================================================================

elif page == "Match Results":
    st.header("📊 Record Match Result")
    
    if len(st.session_state.players) < 2:
        st.warning("Add players first!")
    else:
        st.subheader("Enter Match Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Team A Players:**")
            team_a_players = st.multiselect(
                "Select Team A",
                options=[p['name'] for p in st.session_state.players],
                key="team_a"
            )
        
        with col2:
            st.write("**Team B Players:**")
            team_b_players = st.multiselect(
                "Select Team B",
                options=[p['name'] for p in st.session_state.players],
                key="team_b"
            )
        
        winner = st.radio("Who won?", ["Team A", "Team B"])
        
        if st.button("Record Match"):
            if not team_a_players or not team_b_players:
                st.error("Both teams need players!")
            else:
                # Record match
                match = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
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
                
                st.success(f"✅ Match recorded! {winner} wins!")
        
        # Show match history
        if st.session_state.matches:
            st.subheader("Recent Matches")
            for i, match in enumerate(reversed(st.session_state.matches[-5:]), 1):
                st.write(f"**Match {len(st.session_state.matches) - i + 1}** ({match['date']})")
                st.write(f"Team A: {', '.join(match['team_a'])}")
                st.write(f"Team B: {', '.join(match['team_b'])}")
                st.write(f"🏆 Winner: {match['winner']}")
                st.write("---")

# ============================================================================
# PAGE 4: LEADERBOARD
# ============================================================================

elif page == "Leaderboard":
    st.header("🏆 Player Leaderboard")
    
    if not st.session_state.players:
        st.info("No players yet!")
    else:
        # Create leaderboard
        leaderboard = sorted(st.session_state.players, key=lambda x: x['points'], reverse=True)
        
        # Display as table
        lb_data = []
        for i, player in enumerate(leaderboard, 1):
            win_rate = (player['matches_won'] / player['matches_played'] * 100) if player['matches_played'] > 0 else 0
            lb_data.append({
                'Rank': f"#{i}",
                'Player': player['name'],
                'Points': player['points'],
                'Matches': player['matches_played'],
                'Wins': player['matches_won'],
                'Win Rate': f"{win_rate:.1f}%",
                'Rating': player['rating']
            })
        
        df = pd.DataFrame(lb_data)
        
        # Highlight top 3
        st.subheader("🥇 Top Players")
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
        
        st.markdown("---")
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# FOOTER
# ============================================================================

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Total Players: {len(st.session_state.players)}\n📅 Matches Played: {len(st.session_state.matches)}")
