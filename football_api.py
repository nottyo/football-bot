import requests
import json
from datetime import timezone, datetime


league_competitions = {
    'pl': '2021',
    'ucl': '2001',
    'laliga': '2014',
    'bundesliga': '2002',
    'calcio': '2019'
}

headers = {
    'X-Auth-Token': '1439b063b66a479caf45a00d80d25e22'
}

base_url = 'http://api.football-data.org/v2'


class FootballApi(object):

    def _get_current_matchday(self, league_name):
        url = base_url + '/competitions/' + league_competitions[league_name]
        response = requests.get(url, headers=headers)
        print('matchday_response: {}'.format(json.dumps(response.text)))
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

    def _get_date_from_datetime(self, local_dt):
        date_format = '%A %d %B %Y'
        return datetime.strftime(local_dt, date_format)

    def _get_time_from_datetime(self, local_dt):
        time_format = '%H:%M'
        return datetime.strftime(local_dt, time_format)

    def _normalize_team_name(self, team_name):
        team_name = str(team_name).replace('FC', '')
        team_name = team_name.replace('AFC', '')
        team_name = team_name.replace('Wanderers', '')
        team_name = team_name.replace('& Hove Albion', '')
        team_name = team_name.replace('CF', '')
        team_name = team_name.replace('RCD', '')
        team_name = team_name.replace('RC', '')
        team_name = team_name.replace('SD', '')
        team_name = team_name.replace('de Barcelona', '')
        team_name = team_name.replace('La Coruña', '')
        team_name = team_name.replace('de Fútbol', '')
        return team_name.strip()

    def get_fixtures(self, league_name):
        matchday = self._get_current_matchday(league_name)
        url = base_url + '/competitions/' + league_competitions[league_name] + '/matches'
        params = {
            'matchday': matchday
        }
        response = requests.get(url, params=params, headers=headers)
        print('fixtures response: {}'.format(response.text))
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


