import requests
import json
from dateutil.relativedelta import relativedelta
from datetime import timezone, datetime, timedelta


league_competitions = {
    'pl': '2021',
    'ucl': '2001',
    'laliga': '2014',
    'bundesliga': '2002',
    'calcio': '2019'
}

match_status = {
    'FINISHED': "FT",
    'IN_PLAY': 'LIVE',
    'LIVE': 'LIVE'
}

headers = {
    'X-Auth-Token': '1439b063b66a479caf45a00d80d25e22'
}

base_url = 'http://api.football-data.org/v2'
date_format = '%Y-%m-%dT%H:%M:%SZ'

with open('emoji_flags.json') as f:
    emoji_flags = json.load(f)


class FootballApi(object):

    def _get_current_matchday(self, league_name):
        url = base_url + '/competitions/' + league_competitions[league_name]
        response = requests.get(url, headers=headers)
        json_resp = response.json()
        current_matchday = json_resp['currentSeason']['currentMatchday']
        if current_matchday is None:
            return 1
        else:
            return current_matchday

    def _convert_datetime_timezone_to_local(self, utc_dt_str):
        dt_format = '%Y-%m-%dT%H:%M:%SZ'
        utc_dt = datetime.strptime(utc_dt_str, dt_format)
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def _get_date_from_datetime(self, local_dt, date_format='%A %d %B %Y'):
        return datetime.strftime(local_dt, date_format)

    def _get_time_from_datetime(self, local_dt, time_format='%H:%M'):
        return datetime.strftime(local_dt, time_format)

    def _normalize_team_name(self, team_name):
        team_name = str(team_name).replace('AFC', '')
        team_name = team_name.replace('FC', '')
        return team_name.strip()

    def get_fixtures(self, league_name):
        matchday = self._get_current_matchday(league_name)
        url = base_url + '/competitions/' + league_competitions[league_name] + '/matches'
        params = {
            'matchday': matchday
        }
        response = requests.get(url, params=params, headers=headers)
        resp_json = response.json()
        data = dict()
        data['match_day'] = matchday
        data['competition_name'] = resp_json['competition']['name']
        for match in resp_json['matches']:
            localt_dt = self._convert_datetime_timezone_to_local(match['utcDate'])
            date_str = self._get_date_from_datetime(localt_dt)
            home_team = match['homeTeam']
            home_team['name'] = self._normalize_team_name(home_team['name'])
            away_team = match['awayTeam']
            away_team['name'] = self._normalize_team_name(away_team['name'])
            if date_str not in data:
                data[date_str] = [
                    {
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'match_time': self._get_time_from_datetime(localt_dt),
                        'match_id': match['id']
                    }
                ]
            else:
                data[date_str].append(
                    {
                        'homeTeam': match['homeTeam'],
                        'awayTeam': match['awayTeam'],
                        'match_time': self._get_time_from_datetime(localt_dt),
                        'match_id': match['id']
                    }
                )

        return data

    def _get_age(self, dob_str):
        if dob_str is not None:
            current_date = datetime.now()
            dob_date = datetime.strptime(dob_str, date_format)
            return relativedelta(current_date, dob_date).years
        return 'N/A'

    def _get_emoji_flag(self, country):
        for flag in emoji_flags:
            if country.lower() in flag['name'].lower():
                return flag['emoji']
        return ''

    def get_team(self, team_id):
        url = base_url + '/teams/{0}'.format(team_id)
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        data = dict()
        data['team_name'] = resp_json['name']
        data['team_website'] = resp_json['website']
        data['players'] = []
        for player in resp_json['squad']:
            if player['role'] == 'PLAYER':
                data['players'].append(
                    {
                        'name': '{0} {1}'.format(player['name'], self._get_emoji_flag(player['nationality'])),
                        'position': player['position'],
                        'age': self._get_age(player['dateOfBirth'])
                    }
                )
            if player['role'] == 'COACH':
                data['head_coach'] = '{0} {1}'.format(player['name'], self._get_emoji_flag(player['nationality']))
        data['players'] = sorted(data['players'], key=lambda k: k['position'])
        return data

    def get_matches_by_team(self, team_id, limit):
        url = base_url + '/teams/{0}/matches'.format(team_id)
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        data = dict()
        data['matches'] = []
        for match in resp_json['matches']:
            if len(data['matches']) == limit:
                break
            if match['status'] == 'SCHEDULED':
                local_dt = self._convert_datetime_timezone_to_local(match['utcDate'])
                local_date = self._get_date_from_datetime(local_dt, date_format='%a, %b %d').upper()
                local_time = self._get_time_from_datetime(local_dt)
                if int(team_id) == match['homeTeam']['id']:
                    data['team_name'] = match['homeTeam']['name']
                    data['matches'].append(
                        {
                            'dt': '{0} {1}'.format(local_date, local_time),
                            'opponent_team_name': '{0} (H)'.format(match['awayTeam']['name']),
                            'opponent_team_id': match['awayTeam']['id']
                        }
                    )
                else:
                    data['matches'].append(
                        {
                            'dt': '{0} {1}'.format(local_date, local_time),
                            'opponent_team_name': '{0} (A)'.format(match['homeTeam']['name']),
                            'opponent_team_id': match['homeTeam']['id']
                        }
                    )
        return data
    
    def get_results(self, league_name, day_offset):
        current_matchday = self._get_current_matchday(league_name)
        params = {
            'matchday': current_matchday,
            'status': 'FINISHED,LIVE,IN_PLAY'
        }
        url = base_url + '/competitions/' + league_competitions[league_name] + '/matches'
        response = requests.get(url, headers=headers, params=params)
        resp_json = response.json()
        data = dict()
        data['competition_name'] = resp_json['competition']['name']
        for match in resp_json['matches']:
            localt_dt = self._convert_datetime_timezone_to_local(match['utcDate'])
            date_str = self._get_date_from_datetime(localt_dt)
            home_team = match['homeTeam']
            home_team['name'] = self._normalize_team_name(home_team['name'])
            away_team = match['awayTeam']
            away_team['name'] = self._normalize_team_name(away_team['name'])
            if date_str not in data:
                data[date_str] = [
                    {
                        'homeTeam': home_team,
                        'awayTeam': away_team,
                        'match_id': match['id'],
                        'status': match_status[match['status']],
                        'score': '{0} - {1}'.format(match['score']['fullTime']['homeTeam'], 
                                        match['score']['fullTime']['awayTeam'])
                    }
                ]
            else:
                data[date_str].append(
                    {
                        'homeTeam': match['homeTeam'],
                        'awayTeam': match['awayTeam'],
                        'match_id': match['id'],
                        'status': match_status[match['status']],
                        'score': '{0} - {1}'.format(match['score']['fullTime']['homeTeam'], 
                                        match['score']['fullTime']['awayTeam'])
                    }
                )

        return data

    def get_standings(self, league_name):
        url = base_url + '/competitions/' + league_competitions[league_name] + '/standings'
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        data = dict()
        data['competition_name'] = resp_json['competition']['name']
        data['teams'] = []
        for standing in resp_json['standings']:
            if standing['type'] == 'TOTAL':
                for table in standing['table']: 
                    data['teams'].append(
                        {
                            'position': str(table['position']),
                            'team_name': self._normalize_team_name(table['team']['name']),
                            'team_id': table['team']['id'],
                            'played': str(table['playedGames']),
                            'won': str(table['won']),
                            'draw': str(table['draw']),
                            'lost': str(table['lost']),
                            'gd': str(table['goalDifference']),
                            'pts': str(table['points'])
                        }
                    )
        return data

if __name__ == '__main__':
    football_api = FootballApi()
    data = football_api.get_standings('pl')
    print(json.dumps(data))


