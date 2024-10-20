"""
A simple AI Action template showcasing some more advanced configuration features

Please check out the base guidance on AI Actions in our main repository readme:
https://github.com/sema4ai/actions/blob/master/README.md

https://github.com/Zmalski/NHL-API-Reference?tab=readme-ov-file#get-team-roster-as-of-now

NOTES:
- static data like team name and abbreviation should be stored in a database or a file
- use caching for frequently requested data like standings
"""

from sema4ai.actions import action, Response, ActionError

import json
import requests
from pathlib import Path
from support import write_data_to_json

BASE_URL = "https://api-web.nhle.com/v1"


@action
def get_teams() -> Response[str]:
    """Get teams from current standings as saves them as JSON file.

    Returns:
        list of teams with their name and abbreviation
    """
    url = f"{BASE_URL}/standings/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    standings = data.get("standings", [])
    teams = []
    # Perform case-insensitive search for full or partial match by abbreviation or name
    for standing in standings:
        teams.append(
            {
                "team_name": standing.get("teamName")["default"],
                "team_abbreviation": standing.get("teamAbbrev")["default"],
            }
        )
    write_data_to_json(teams, "teams")
    return teams


def get_team_abbreviation(query: str) -> str:
    """Get team abbreviation by query.

    Args:
        query: team name or abbreviation

    Returns:
        team abbreviation
    """
    Path("data/teams.json").exists() or get_teams()
    with open("data/teams.json", "r", encoding="utf-8") as f:
        teams = json.load(f)
    for team in teams:
        if (
            query.lower() in team["team_name"].lower()
            or query.lower() in team["team_abbreviation"].lower()
        ):
            return team["team_abbreviation"]
    raise ValueError("Team not found")


@action
def get_team_roster(
    team_name_or_abbreviation: str, refresh: bool = False
) -> Response[str]:
    """Get team roster by abbreviation.

    Args:
        team_name_or_abbreviation: team abbreviation
        refresh: whether to refresh the roster
    Returns:
        list of players in the team
    """
    abbreviation = get_team_abbreviation(team_name_or_abbreviation)
    url = f"{BASE_URL}/roster/{abbreviation}/current"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    remove_headshot(data)
    if not data:
        raise ActionError(f"Team {abbreviation} not found")
    write_data_to_json(data, f"team_{abbreviation}_roster")
    # for player_id in team_players:
    #     player_url = f"{BASE_URL}/people/{player_id}"
    #     player_response = requests.get(player_url)
    #     player_info = player_response.json()
    #     write_data_to_json(player_info, f"player_{player_id}")
    return data


@action
def get_player_by_id(player_id: int) -> Response[str]:
    """Get player by ID.

    Args:
        player_id: player ID

    Returns:
        player information
    """
    url = f"{BASE_URL}/player/{player_id}"
    response = requests.get(url)
    response.raise_for_status()
    player = response.json()
    return player


def remove_headshot(data):
    if isinstance(data, dict):
        if "headshot" in data:
            del data["headshot"]
        for key, value in data.items():
            remove_headshot(value)
    elif isinstance(data, list):
        for item in data:
            remove_headshot(item)


def remove_teamlogo(data):
    if isinstance(data, dict):
        if "teamLogo" in data:
            del data["teamLogo"]
        for key, value in data.items():
            remove_teamlogo(value)
    elif isinstance(data, list):
        for item in data:
            remove_teamlogo(item)


@action
def get_team_scoreboard(team_name_or_abbreviation: str) -> Response[str]:
    """Get team scoreboard

    Args:
        team_name_or_abbreviation: team abbreviation
    Returns:
        scoreboard of the team
    """
    abbreviation = get_team_abbreviation(team_name_or_abbreviation)
    url = f"{BASE_URL}/scoreboard/{abbreviation}/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ActionError(f"Team {abbreviation} not found")
    return data


@action
def get_standings_now() -> Response[str]:
    """Get standings now


    Returns:
        standings
    """
    url = f"{BASE_URL}/standings/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    # TODO. lot of data returned and needs to be filtered and formatted as a table
    return data


@action
def get_goalie_stat_leaders() -> Response[str]:
    """Get goalie stat leaders

    Returns:
        goalier stats
    """
    url = f"{BASE_URL}/goalie-stats-leaders/current"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    remove_headshot(data)
    remove_teamlogo(data)
    return data


@action
def get_skater_stat_leaders() -> Response[str]:
    """Get skater stat leaders

    Returns:
        skater stats
    """
    url = f"{BASE_URL}/skater-stats-leaders/current"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    remove_headshot(data)
    remove_teamlogo(data)
    return data


@action
def get_team_stats(team_name_or_abbreviation: str) -> Response[str]:
    """Get team stats

    Args:
        team_name_or_abbreviation: team abbreviation
    Returns:
        stats of the team
    """
    abbreviation = get_team_abbreviation(team_name_or_abbreviation)
    url = f"{BASE_URL}/club-stats/{abbreviation}/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    remove_headshot(data)
    remove_teamlogo(data)
    if not data:
        raise ActionError(f"Team {abbreviation} not found")
    return data


@action
def get_team_schedule(team_name_or_abbreviation: str) -> Response[str]:
    """Get team schedule

    Args:
        team_name_or_abbreviation: team abbreviation
    Returns:
        schedule of the team
    """
    abbreviation = get_team_abbreviation(team_name_or_abbreviation)
    url = f"{BASE_URL}/club-schedule-season/{abbreviation}/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ActionError(f"Team {abbreviation} not found")
    return data


@action
def get_daily_scores() -> Response[str]:
    """Get daily scores

    Returns:
        daily scores
    """
    url = f"{BASE_URL}/score/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data


@action
def get_scoreboard() -> Response[str]:
    """Get scoreboard

    Returns:
        scoreboard
    """
    url = f"{BASE_URL}/scoreboard/now"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data
