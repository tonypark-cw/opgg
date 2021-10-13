#  ________  ________  ________  ________                              
# |\   __  \|\   __  \|\   ____\|\   ____\                             
# \ \  \|\  \ \  \|\  \ \  \___|\ \  \___|                             
#  \ \  \\\  \ \   ____\ \  \  __\ \  \  ___                           
#   \ \  \\\  \ \  \___|\ \  \|\  \ \  \|\  \                          
#    \ \_______\ \__\    \ \_______\ \_______\                         
#     \|_______|\|__|     \|_______|\|_______|                         
#  ________ ________      ___    ___ ________  ________  ________      
# |\  _____\\   __  \    |\  \  /  /|\   __  \|\   __  \|\   ___  \    
# \ \  \__/\ \  \|\  \   \ \  \/  / | \  \|\  \ \  \|\  \ \  \\ \  \   
#  \ \   __\\ \   _  _\   \ \    / / \ \   ____\ \   __  \ \  \\ \  \  
#   \ \  \_| \ \  \\  \|   \/  /  /   \ \  \___|\ \  \ \  \ \  \\ \  \ 
#    \ \__\   \ \__\\ _\ __/  / /      \ \__\    \ \__\ \__\ \__\\ \__\
#     \|__|    \|__|\|__|\___/ /        \|__|     \|__|\|__|\|__| \|__|
#                       \|___|/                                                                           
#
# LAST UPDATE: 2021.07.27 /@heezeo
 

import requests
import pandas as pd
import datetime
import numpy as np
import os
import json
import time

class PUBG_esports:
    def __init__(self, api_key = None):
        # -> self.api_key
        print('_____PUBG_esports_class_____')     
        self.api_key = api_key
    def tournament(self, tournament_id):
        # -> 원하는 tournament_id를 입력하면 PUBG_esports의 api_key가 자동으로 입력된 tournament 객체 출력
        return_object = tournament(api_key = self.api_key,tournament_id = tournament_id)
        return return_object
    def matches(self, match_id):
        # -> 원하는 match_id를 입력하면 PUBG_esports의 api_key가 자동으로 입력된 matches 객체 출력
        return_object = matches(api_key = self.api_key ,match_id = match_id)
        return return_object
    def telemetry(self, telemetry_or_match_id):
        # -> 원하는 match_id나 telemetry_link를 입력하면 PUBG_esports의 api_key가 자동으로 입력된 telemetry 객체 출력
        return_object = telemetry(api_key = self.api_key, telemetry_or_match_id = telemetry_or_match_id)
        return return_object

class tournament:
    def __init__(self, api_key, tournament_id = None): 
        # -> self.api_key, self.tournament_id, self.match_id
        print('_____tournament_class_____')      
        self.api_key = api_key
        # tournament_id를 list나 character 형태로 모두 받을 수 있음
        if type(tournament_id) == list:
            self.tournament_id = tournament_id
        else:
            self.tournament_id = [tournament_id]
        # match id는 match_info_list 함수에서 matches 클래스를 경유하여 도출되기 때문에 duration이 1200초가 넘는 유효 매치의 match id임
        self.match_id = [i['match_id'] for i in tournament.match_info_list(self)]
        print('_match_id_count: ', len(self.match_id))
    def match_info_list(self):
        # -> createdAt, match_id를 key로 하는 dictionary의 집합 출력
        return_information = []
        for id in self.tournament_id:
            url = "https://api.pubg.com/tournaments/" + id
            header = {
                "Authorization": self.api_key, 
                "Accept": "application/vnd.api+json"
                }
            tour_json = requests.get(url, headers=header).json()
            raw_match_id = [i['id'] for i in tour_json['included']]
            #matches 클래스를 경유하여 duration이 1200초가 넘는 유효 매치의 match id만 획득
            matches_ = matches(api_key = self.api_key, match_id = raw_match_id)
            return_list = [{'createdAt': i['data']['attributes']['createdAt'], 'match_id': i['data']['id']} for i in matches_.match_json]
            return_information += return_list
        return return_information
    def matches(self):
        # -> tournament 클래스의 match_id를 입력하여 matches 클래스 획득
        return_matches = matches(api_key = self.api_key, match_id = self.match_id)
        return return_matches

class matches:
    def __init__(self, api_key = None, match_id = None):
        # -> self.api_key, self.match_json, self.telemetry_link, self.match_id
        print('_____matches_class_____')
        self.api_key = api_key
        match_url = "https://api.pubg.com/shards/tournament/matches/"
        match_header = {
                "Authorization": self.api_key ,
                "Accept": "application/vnd.api+json"
                }
        if type(match_id) == list:
            match_id_list = []
            match_json_list = []
            telemetry_link_list = []
            for id in match_id:
                match_json = requests.get(match_url + id, headers=match_header).json()
                # duration이 1200초 이상인 매치만 선별
                if match_json['data']['attributes']['duration'] > 1200 :
                    telemetry_link = [i['attributes']['URL'] for i in match_json['included'] if i['type'] == 'asset'][0]
                    match_json_list.append(match_json)
                    telemetry_link_list += telemetry_link
                    match_id_list.append(id)
                else: 
                    pass
            self.match_json = match_json_list
            self.telemetry_link = telemetry_link_list    
            self.match_id = match_id_list
        else:
            match_json = requests.get(match_url + match_id, headers= match_header).json()
            # duration이 1200초 이상인 매치만 선별
            if match_json['data']['attributes']['duration'] > 1200 :
                self.telemetry_link = [i['attributes']['URL'] for i in match_json['included'] if i['type'] == 'asset'][0]    
                match_json_list = []
                match_json_list.append(match_json)
                self.match_json = match_json_list
                self.match_id = [match_id]
            else:
                pass
        print('_match_id_count: ', len(self.match_id))
    def raw_stats_df(self):
        # -> PUBG API matches 단에서 획득할 수 있는 stat의 Dataframe 출력       
        match_id_list = []
        for json in self.match_json:
            match_included = json['included']
            rosters_stats = [item['attributes']['stats'] for item in match_included if item['type'] == 'roster']
            rosters = [item['relationships']['participants']['data'] for item in match_included if item['type'] == 'roster']
            roster_id = [item['id'] for item in match_included if item['type'] == 'roster']

            for a in range(len(rosters)):
                r = rosters[a]
                players = []
                for b in range(len(r)):
                    players.append(r[b]['id'])
                rosters_stats[a]['players'] = players

            players = []
            rank = []
            team_no = []
            team_id = []
            
            for a in range(len(rosters_stats)):
                r = rosters_stats[a]
                players += r['players']
                for b in range(len(r['players'])):
                    rank.append(r['rank'])
                    team_no.append(r['teamId'])
                    team_id.append(roster_id[a])
            rosters_df = pd.DataFrame({'player_id': players, 'rank': rank, 'team_no': team_no, 'team_id': team_id})
            players_stats = [item['attributes']['stats'] for item in match_included if item['type'] == 'participant']
            players_id = [item['id'] for item in match_included if item['type'] == 'participant']
            players_df = pd.DataFrame(players_stats)
            players_df['playerId'] = players_id
            stats = pd.merge(rosters_df, players_df, how = 'inner', left_on = 'player_id', right_on = 'playerId')
            match_id = json['data']['id'] 
            stats['match_id'] = [match_id for i in range(len(stats))]
            match_id_list.append(match_id)
            globals()[match_id] = stats
            
        return_df = pd.concat([globals()[id] for id in match_id_list])
        return_df = return_df.loc[:, ['match_id','player_id', 'rank', 'team_no', 'team_id',
                                        'DBNOs', 'assists', 'boosts','damageDealt', 'deathType',
                                        'headshotKills', 'heals', 'killPlace','killStreaks', 'kills',
                                        'longestKill', 'name', 'playerId', 'revives','rideDistance',
                                        'roadKills', 'swimDistance', 'teamKills','timeSurvived', 'vehicleDestroys',
                                        'walkDistance', 'weaponsAcquired','winPlace' ]]
        return return_df
    def participant_df(self):
        # -> matches 클래스의 match_id에 해당하는 매치에 참여한 선수들의 정보 Dataframe 출력
        # '_'를 기준으로 선수명, 팀명을 분리하기 때문에 '팀명_선수명'의 형식을 갖추지 않은 경우 에러 발생
        for json in self.match_json:
            included = json['included']
            participants = []
            participants_name = []
            participants_team = []
            for i in included:
                if i['type'] == 'participant':
                    team_player = i['attributes']['stats']['name']
                    team = team_player.split('_')[0]
                    player = team_player.split('_')[1]
                    participants.append(team_player)
                    participants_team.append(team)
                    participants_name.append(player)
                else:
                    continue
            
            participant_df = pd.DataFrame({'player_id': participants, 'team': participants_team , 'player': participants_name})
            match_id = json['data']['id'] 
            participant_df['match_id'] = [match_id for i in range(len(participant_df))]
            globals()[match_id] = participant_df
        return_df = pd.concat([globals()[id] for id in self.match_id])
        return_df = return_df.loc[:, ['match_id', 'player_id', 'team', 'player']]
        return return_df
    def telemetry(self):
        # -> matches 클래스의 match_id를 입력하여 telemetry 클래스 획득
        return_telemetry = telemetry(api_key = self.api_key, telemetry_or_match_id=self.match_id)
        return return_telemetry

class telemetry:
    def __init__(self, api_key = None, telemetry_or_match_id = None):
        # -> self.api_key, self.tel_json, self.telemetry_link, self.match_id
        print('_____telemetry_class_____')
        self.api_key = api_key
        # tel_save_open: telemetry json을 local 경로에서 찾고, 있으면 local에서 불러오고, 없으면 API 호출을 통해 불러온 telemetry json을 local에 저장하고, 이 모든 과정에서 telemetry_json 내의 각 로그들에 match_id 항목을 추가하는 함수
        def tel_save_open(api_key, search_key):
            # API로 telemetry json 불러오는 함수
            def tel(api_key, telemetry_link):
                header = {
                    "Authorization": api_key ,
                    "Accept": "application/vnd.api+json"
                    }
                tel = requests.get(telemetry_link, headers=header).json()
                return tel      
            # local 경로에서 telemetry json 있는지 확인하는 함수
            def find_file(search_key):
                if os.path.isdir('4_json') is True:
                    dir_list = os.listdir('4_json')
                else:
                    os.mkdir('4_json')
                    dir_list = os.listdir('4_json')
                if search_key in dir_list:
                    file_exist = 'True'
                else:
                    file_exist = 'False'
                return file_exist           
            # telemetry json의 각 로그들에 match_id 항목 추가하는 함수
            def match_id_update(tele_json, match_id):
                for log in tele_json:
                    log['_matchid'] = match_id
                return tele_json           
            # 상기의 함수를 활용해 tel_save_open의 과정 수행하는 함수
            def tele_json(search_key, api_key):
                if len(search_key) > 36: #search_key가 telemetry link인 경우
                    ### telemetry link를 통할 경우, local의 모든 json 파일들이 match_id로 저장되어 있기 때문에 local에 저장된 json을 불러오기 위해 결국 API 호출로 telemetry json을 불러와야 하는 문제가 발생함. 따라서 match_id를 활용한 코드를 권장함.
                    telemetry_link = search_key
                    tele_json = tel(api_key, search_key)
                    match_id = [i['MatchId'][-36:] for i in tele_json if i['_T'] == 'LogMatchDefinition'][0]
                    tele_json = match_id_update(tele_json, match_id)
                    file_exist = find_file(match_id)
                    # local에 파일이 없다면 local에 json 파일 저장
                    if file_exist == 'True':
                        pass
                    else:
                        with open(file = '4_json/'+ match_id + '.json', mode = 'w', encoding = 'utf-8') as outfile:
                            json.dump(tele_json, outfile)
                else: # search_key가 match_id인 경우
                    match_id = search_key 
                    file_exist = find_file(match_id)
                    # local에 파일이 있다면 불러오고 local에 파일이 없다면 local에 json 파일 저장
                    if file_exist == 'True':
                        file = open('4_json/'+ match_id + '.json', 'r', encoding= 'utf-8')
                        tele_json = json.load(file)
                        tele_json = match_id_update(tele_json, match_id)
                    else:
                        telemetry_link = matches(api_key, match_id).telemetry_link
                        tele_json = tel(api_key, telemetry_link)
                        tele_json_ = match_id_update(tele_json, match_id)
                        with open(file = '4_json/'+ match_id + '.json', mode = 'w', encoding = 'utf-8') as outfile:
                            json.dump(tele_json_, outfile)
                return (tele_json_, match_id, telemetry_link)
            return tele_json(search_key, api_key)

        tel_json = []
        telemetry_list = []
        match_id_list = []

        # telemetry_or_match_id가 단수의 character인 경우, 복수의 key로 구성된 list인 경우 모두 대응
        if type(telemetry_or_match_id) == list:
            for id in telemetry_or_match_id:
                t_m_l = tel_save_open(self.api_key, id)
                tele = t_m_l[0]
                match_id = t_m_l[1]
                telemetry_l = t_m_l[2]
                tel_json += tele
                telemetry_list.append(telemetry_l)
                match_id_list.append(match_id)
    
        else:
            t_m_l = tel_save_open(self.api_key, telemetry_or_match_id)
            tele = t_m_l[0]
            match_id = t_m_l[1]
            telemetry_l = t_m_l[2]
            tel_json += tele
            telemetry_list.append(telemetry_l)
            match_id_list.append(match_id)

        self.tel_json = tel_json
        self.telemetry_link = telemetry_list
        self.match_id = match_id_list
        print('_match_id_count: ', len(self.match_id))
    def log_json(self, log_name):
        # -> telemetry의 log_name 로그들의 리스트 출력 (원하는 로그의 리스트 출력)
        log = [i for i in self.tel_json if i['_T'] == log_name]
        return log
    def kill_log_json(self):
        # -> telemetry의 'LogPlayerKill' 로그들의 리스트 출력
        kill_log = [i for i in self.tel_json if i['_T']== 'LogPlayerKill']
        return kill_log
    def attack_log_json(self):
        # -> telemetry의 'LogPlayerAttack' 로그들의 리스트 출력
        attack_log = [i for i in self.tel_json if i['_T']== 'LogPlayerAttack']
        return attack_log
    def damage_log_json(self):
        # -> telemetry의 'LogPlayerTakeDamage' 로그들의 리스트 출력
        damage_log = [i for i in self.tel_json if i['_T']== 'LogPlayerTakeDamage']
        return damage_log
    def groggy_log_json(self):
        # -> telemetry의 'LogPlayerMakeGroggy' 로그들의 리스트 출력
        dbno_log = [i for i in self.tel_json if i['_T'] == 'LogPlayerMakeGroggy']
        return dbno_log

class Indicators:
    def __init__(self, PUBG_esports, tournament_id_list = [], match_id_list = []):
        # -> self.PUBG_esports, self.match_id, self.tournament_id, self.raw_stats_df
        print('_____Indicators_class_____')
        self.PUBG_esports = PUBG_esports
        self.match_id = []
        # tournament_id_list로 key를 받은 경우, match_id로 key를 받은 경우 모두 대응
        if len(tournament_id_list) > 0:
            self.tournament_id = tournament_id_list
            for i in self.tournament_id:
                self.match_id += PUBG_esports.tournament(i).match_id
                time.sleep(40)
        else:
            self.match_id = match_id_list
        self.match_id = self.PUBG_esports.matches(self.match_id).match_id
        print('_match_id_count: ', len(self.match_id))
        # Indicators 클래스의 함수에서 사용될 raw_stats_df
        for match in self.match_id:
            globals()[match+'_stats'] = self.PUBG_esports.matches(match).raw_stats_df()
        stats_concat = pd.concat([globals()[a + '_stats'] for a in self.match_id])
        self.raw_stats_df = stats_concat           
    ### 1st depth
    def First_Indicators(self):
        # -> 1차 지표 DataFrame들 dictionary 형태로 출력
        stats = Indicators.stats_df(self.raw_stats_df)
        stats_groupby = Indicators.stats_groupby_df(stats)
        return {'stats_df': stats, 'stats_groupby_df': stats_groupby}
    def stats_df(raw_stats_df):
        # -> raw_stats_df 중 필요 지표만 선별한 DataFrame 출력
        stats_df = raw_stats_df.loc[:,['match_id', 'name', 'kills', 'damageDealt', 'DBNOs', 'timeSurvived', 'winPlace']].rename(columns = {'winPlace': 'team_rank'})
        stats_df['player_rank'] = stats_df.groupby('match_id')['timeSurvived'].rank(method = 'min', ascending = False).astype(int)
        stats_df['damageDealt'] = round(stats_df.damageDealt, 2)
        stats_df['timeSurvived'] = round(stats_df.timeSurvived / 60, 2)
        return stats_df
    def stats_groupby_df(stats_df):
        # -> stats_df를 선수 기준으로 groupby 한 Dataframe 출력
        stats_df = stats_df.loc[:,['name', 'match_id','kills', 'damageDealt', 'DBNOs', 'timeSurvived']]
        stats_groupby_df = stats_df.groupby('name').agg({'match_id': 'count','kills': 'sum',  'damageDealt': 'sum', 'DBNOs': 'sum', 'timeSurvived': 'sum'}).rename(columns = {'match_id': 'matches'})
        return stats_groupby_df
    ### 2nd depth
    def Second_Indicators(self):
        # -> 2차 지표 DataFrame들 dictionary 형태로 출력
        _stats_groupby_df = Indicators.First_Indicators(self)['stats_groupby_df']
        _stats_per_minute_df = Indicators.stats_per_minute_df(_stats_groupby_df)
        P = self.PUBG_esports
        T = P.telemetry(self.match_id)
        kill_log_json = T.kill_log_json()
        attack_log_json = T.attack_log_json()
        damage_log_json = T.damage_log_json()
        groggy_log_json = T.groggy_log_json()
        telemetry_json = T.tel_json
        _raw_attack_damage_df = Indicators.raw_attack_damage_df(attack_log_json, damage_log_json)
        _attack_damage_df = Indicators.attack_damage_df(_raw_attack_damage_df)
        _attack_damage_adj_df = Indicators.attack_damage_adj_df(_raw_attack_damage_df)
        _body_part_df = Indicators.body_part_df(_raw_attack_damage_df)
        _steal_kill_df = Indicators.steal_kill_df(kill_log_json, groggy_log_json)
        _heal_boost_revive_df = Indicators.heal_boost_revive_df(self.raw_stats_df, telemetry_json)
        _stats_selected_df = Indicators.stats_selected_df(_attack_damage_adj_df, _body_part_df, _steal_kill_df)
        return {'stats_per_minute_df': _stats_per_minute_df, 'raw_attack_damage_df': _raw_attack_damage_df, 'attack_damage_df': _attack_damage_df, 'attack_damage_adj_df': _attack_damage_adj_df, 'body_part_df': _body_part_df, 'steal_kill_df': _steal_kill_df, 'heal_boost_revive_df': _heal_boost_revive_df, 'stats_selected_df': _stats_selected_df}
    def stats_per_minute_df(stats_groupby_df):
        # -> stats의 분당 지표 Dataframe 출력
        stats_per_minute = stats_groupby_df.reset_index().loc[:,['name','timeSurvived', 'kills', 'damageDealt', 'DBNOs']]
        stats_per_minute['kills'] = round(stats_per_minute.kills / stats_per_minute.timeSurvived,2)
        stats_per_minute['damageDealt'] = round(stats_per_minute.damageDealt / stats_per_minute.timeSurvived,2)
        stats_per_minute['DBNOs'] = round(stats_per_minute.DBNOs / stats_per_minute.timeSurvived,2)
        stats_per_minute['timeSurvived'] = round(stats_per_minute['timeSurvived'],2)
        stats_per_minute = stats_per_minute.rename(columns = {'kills': 'kills_per_min', 'damageDealt': 'damageDealt_per_min', 'DBNOs': 'DBNOs_per_min'}).set_index('name')
        return stats_per_minute
    def raw_attack_damage_df(attack_log_json, damage_log_json):
        # -> attack, damage 로그를 활용한 지표 모두 포함된 Dataframe 출력
        # 선수별 attack 횟수 집계
        def attack(attack_log_json):
            # attack
            attack = []
            for attack_log in attack_log_json:
                if attack_log['weapon'].get('category') is not None:
                    attack.append(attack_log['attacker']['name'])
                else:
                    continue
            attacker = list(set(attack))
            attack_count = []
            for player in attacker:
                attack_cnt = sum([1 for i in attack if i == player])
                attack_count.append(attack_cnt)
            attack_df = pd.DataFrame({'attacker': attacker, 'attacks': attack_count}).reset_index()
            return attack_df
        # 선수별 activeshot 횟수, 딜량, 부위별 적중횟수 집계
        def damage(damage_log_json):
            # damage
            damage_attacker = []
            damage_deal = []
            headshot_cnt = []
            headshot_deal = []
            headshot_deal_adj = []
            torsoshot_cnt = []
            torsoshot_deal = []
            torsoshot_deal_adj = []
            pelvisshot_cnt = []
            pelvisshot_deal = []
            pelvisshot_deal_adj = []
            legshot_cnt = []
            legshot_deal = []
            legshot_deal_adj = []
            armshot_cnt = []
            armshot_deal = []
            armshot_deal_adj = []            
            for damage_log in damage_log_json:
                if damage_log.get('attacker') is not None:
                    damage_attacker.append(damage_log['attacker']['name'])
                    deal = damage_log['damage']
                    damage_deal.append(deal)
                    if damage_log['damageTypeCategory'] == 'Damage_Gun':
                        if damage_log['damageReason'] == 'HeadShot':
                            headshot_cnt.append(1)
                            torsoshot_cnt.append(0)
                            pelvisshot_cnt.append(0)
                            legshot_cnt.append(0)
                            armshot_cnt.append(0)
                            if deal == 0:
                                headshot_deal.append(deal)
                                ## 보정값 대입
                                headshot_deal_adj.append(76)
                            else:
                                headshot_deal.append(deal)
                                headshot_deal_adj.append(deal)
                            torsoshot_deal.append(0)
                            torsoshot_deal_adj.append(0)
                            pelvisshot_deal.append(0)
                            pelvisshot_deal_adj.append(0)
                            legshot_deal.append(0)
                            legshot_deal_adj.append(0)
                            armshot_deal.append(0)
                            armshot_deal_adj.append(0)
                        elif damage_log['damageReason'] == 'TorsoShot':
                            headshot_cnt.append(0)
                            torsoshot_cnt.append(1)
                            pelvisshot_cnt.append(0)
                            legshot_cnt.append(0)
                            armshot_cnt.append(0)
                            if deal == 0:
                                torsoshot_deal.append(deal)
                                ## 보정값 대입
                                torsoshot_deal_adj.append(35)
                            else:
                                torsoshot_deal.append(deal)
                                torsoshot_deal_adj.append(deal)
                            headshot_deal.append(0)
                            headshot_deal_adj.append(0)
                            pelvisshot_deal.append(0)
                            pelvisshot_deal_adj.append(0)
                            legshot_deal.append(0)
                            legshot_deal_adj.append(0)
                            armshot_deal.append(0)
                            armshot_deal_adj.append(0)
                        elif damage_log['damageReason'] == 'PelvisShot':
                            headshot_cnt.append(0)
                            torsoshot_cnt.append(0)
                            pelvisshot_cnt.append(1)
                            legshot_cnt.append(0)
                            armshot_cnt.append(0)
                            if deal == 0:
                                pelvisshot_deal.append(deal)
                                ## 보정값 대입
                                pelvisshot_deal_adj.append(33)
                            else:
                                pelvisshot_deal.append(deal)
                                pelvisshot_deal_adj.append(deal)
                            headshot_deal.append(0)
                            headshot_deal_adj.append(0)
                            torsoshot_deal.append(0)
                            torsoshot_deal_adj.append(0)
                            legshot_deal.append(0)
                            legshot_deal_adj.append(0)
                            armshot_deal.append(0)
                            armshot_deal_adj.append(0)
                        elif damage_log['damageReason'] == 'LegShot':
                            headshot_cnt.append(0)
                            torsoshot_cnt.append(0)
                            pelvisshot_cnt.append(0)
                            legshot_cnt.append(1)
                            armshot_cnt.append(0)
                            if deal == 0:
                                legshot_deal.append(deal)
                                ## 보정값 대입
                                legshot_deal_adj.append(21)
                            else:
                                legshot_deal.append(deal)
                                legshot_deal_adj.append(deal)
                            headshot_deal.append(0)
                            headshot_deal_adj.append(0)
                            pelvisshot_deal.append(0)
                            pelvisshot_deal_adj.append(0)
                            torsoshot_deal.append(0)
                            torsoshot_deal_adj.append(0)
                            armshot_deal.append(0)
                            armshot_deal_adj.append(0)
                        else:
                            headshot_cnt.append(0)
                            torsoshot_cnt.append(0)
                            pelvisshot_cnt.append(0)
                            legshot_cnt.append(0)
                            armshot_cnt.append(1)
                            if deal == 0:
                                armshot_deal.append(deal)
                                ## 보정값 대입
                                armshot_deal_adj.append(20)
                            else:
                                armshot_deal.append(deal)
                                armshot_deal_adj.append(deal)
                            headshot_deal.append(0)
                            headshot_deal_adj.append(0)
                            pelvisshot_deal.append(0)
                            pelvisshot_deal_adj.append(0)
                            legshot_deal.append(0)
                            legshot_deal_adj.append(0)
                            torsoshot_deal.append(0)
                            torsoshot_deal_adj.append(0)
                        
                        
                    else:
                        headshot_cnt.append(0)
                        torsoshot_cnt.append(0)
                        pelvisshot_cnt.append(0)
                        legshot_cnt.append(0)
                        armshot_cnt.append(0)
                        headshot_deal.append(0)
                        torsoshot_deal.append(0)
                        pelvisshot_deal.append(0)
                        legshot_deal.append(0)
                        armshot_deal.append(0)
                        headshot_deal_adj.append(0)
                        torsoshot_deal_adj.append(0)
                        pelvisshot_deal_adj.append(0)
                        legshot_deal_adj.append(0)
                        armshot_deal_adj.append(0)
                else:
                    continue
            damage_df = pd.DataFrame({'attacker': damage_attacker, 'deal': damage_deal,
                                    'headshot_cnt': headshot_cnt, 'headshot_deal': headshot_deal, 'headshot_deal_adj': headshot_deal_adj,
                                    'torsoshot_cnt': torsoshot_cnt, 'torsoshot_deal': torsoshot_deal,  'torsoshot_deal_adj': torsoshot_deal_adj,
                                    'pelvisshot_cnt': pelvisshot_cnt, 'pelvisshot_deal': pelvisshot_deal,  'pelvisshot_deal_adj': pelvisshot_deal_adj,
                                    'legshot_cnt': legshot_cnt, 'legshot_deal': legshot_deal,  'legshot_deal_adj': legshot_deal_adj,
                                    'armshot_cnt': armshot_cnt, 'armshot_deal': armshot_deal,  'armshot_deal_adj': armshot_deal_adj,})
            damage_df['gun_deal'] = damage_df['headshot_deal'] + damage_df['torsoshot_deal'] + damage_df['pelvisshot_deal'] + damage_df['legshot_deal'] + damage_df['armshot_deal']
            damage_df['gun_deal_adj'] =  damage_df['headshot_deal_adj'] + damage_df['torsoshot_deal_adj'] + damage_df['pelvisshot_deal_adj'] + damage_df['legshot_deal_adj'] + damage_df['armshot_deal_adj']
            damage_df['activeshots'] = damage_df['headshot_cnt'] + damage_df['torsoshot_cnt'] + damage_df['pelvisshot_cnt'] + damage_df['legshot_cnt'] + damage_df['armshot_cnt']            
            damage_sum_df = damage_df.groupby('attacker').sum().reset_index()
            
            return damage_sum_df
        attack_df = attack(attack_log_json)
        damage_df = damage(damage_log_json)
        return_df = pd.merge(attack_df, damage_df, how = 'left', on = 'attacker')
        return_df['deal_adj'] = round(return_df['deal'] + (return_df['gun_deal_adj'] - return_df['gun_deal']),2)
        return_df['activeshot_rate'] = round(return_df['activeshots']/ return_df['attacks']*100, 2)
        return_df['activeshot_deal'] = round(return_df['gun_deal'] / return_df['activeshots'],2)
        return_df['activeshot_deal_adj'] = round(return_df['gun_deal_adj'] / return_df['activeshots'],2)
        return_df['deal'] = round(return_df['deal'],2)
        return_df['gun_deal'] = round(return_df['gun_deal'],2)
        return_df['gun_deal_adj'] = round(return_df['gun_deal_adj'],2)
        return_df['activeshots'] = return_df['activeshots'].fillna(0).astype(int)
        return_df = return_df.fillna(0)
        return_df = return_df.rename(columns = {'attacker': 'name'}).set_index('name')
        return return_df
    def attack_damage_df(raw_attack_damage_df):
        #-> raw_attack_damage_df에서 보정되지 않은 attack, 딜량, activeshot 관련 지표만 선별한 Dataframe 출력
        return_df = raw_attack_damage_df.loc[:, ['attacks', 'deal', 'gun_deal', 'activeshot_deal','activeshots']]
        return return_df
    def attack_damage_adj_df(raw_attack_damage_df):
        #-> raw_attack_damage_df에서 보정된 지표만 선별한 Dataframe 출력
        return_df = raw_attack_damage_df.loc[:, ['deal_adj', 'gun_deal_adj', 'activeshot_deal_adj']]
        return return_df
    def body_part_df(raw_attack_damage_df):
        #-> raw_attack_damage_df에서 부위별 적중 정보만 선별하여 지표화한 Dataframe 출력
        part = raw_attack_damage_df.loc[:, ['attacks', 'deal_adj', 'activeshots',
                                            'headshot_cnt', 'headshot_deal_adj', 
                                            'torsoshot_cnt', 'torsoshot_deal_adj', 
                                            'pelvisshot_cnt', 'pelvisshot_deal_adj', 
                                            'legshot_cnt', 'legshot_deal_adj', 
                                            'armshot_cnt', 'armshot_deal_adj']].reset_index()
        return_df = part.loc[:, ['name']]
        return_df['headshot_cnt_rate'] = round(part['headshot_cnt'] / part['activeshots'] * 100 ,2)
        return_df['torsoshot_cnt_rate'] =round( part['torsoshot_cnt'] / part['activeshots'] * 100 ,2)
        return_df['pelvisshot_cnt_rate'] = round(part['pelvisshot_cnt'] / part['activeshots'] * 100 ,2)
        return_df['headshot_deal_rate'] = round(part['headshot_deal_adj'] / part['deal_adj'] * 100 ,2)
        return_df['torsoshot_deal_rate'] = round(part['torsoshot_deal_adj'] / part['deal_adj'] * 100 ,2)
        return_df['pelvisshot_deal_rate'] = round(part['pelvisshot_deal_adj'] / part['deal_adj'] * 100 ,2)
        return_df = return_df.set_index('name')
        return return_df
    def steal_kill_df(kill_log_json, groggy_log_json):
        # steal kill, stolen kill, dbno_to_kill 집계한 Dataframe 출력

        # Kill 로그의 DBNO_ID를 입력하여, 해당 DBNO ID를 가지고 있는 groggy_log의 attacker를 출력하는 함수
        def dbno_attacker(dbno_id, groggy_log):
            attacker = list(filter(lambda x: x['dBNOId'] == dbno_id, groggy_log))[0]
            if attacker == None:
                return_attacker = 'None'
            else:
                return_attacker = attacker['attacker']['name']
            return return_attacker

        # 같은 match_id를 가지고 있는 로그 안에서 집계한후, 이후 합산함
        match_id_list = list(set([i['_matchid'] for i in kill_log_json]))
        for match in match_id_list:
            kill_log = list(filter(lambda x: x['_matchid'] == match, kill_log_json))
            groggy_log = list(filter(lambda x: x['_matchid'] == match, groggy_log_json))

            killer = []
            victim = []
            dbno_id = []
            dbno_maker = []
            
            for i in range(len(kill_log)):
                kill = kill_log[i]
                if kill.get('killer') == None:
                    pass
                else:
                    killer.append(kill['killer']['name'])
                    victim.append(kill['victim']['name'])
                    dbno_id.append(kill['dBNOId'])
                    if kill['dBNOId'] == -1:
                        dbno_maker.append('None')
                    else:
                        dbno_maker.append(dbno_attacker(kill['dBNOId'], groggy_log))
            
            check = pd.DataFrame({'killer': killer, 'victim': victim, 'dbno_id': dbno_id, 'dbno_maker': dbno_maker})
            globals()[match + '_check'] = check
            
            
        kill_check = pd.concat([globals()[match + '_check'] for match in match_id_list])
        dbno_to_kill = kill_check.loc[kill_check['killer']== kill_check['dbno_maker']].loc[:, ['killer', 'victim']].rename(columns = {'killer': 'name', 'victim': 'dbno_to_kill'}).groupby('name').count()
        instant_kill = kill_check.loc[kill_check['dbno_id']== -1].loc[:, ['killer', 'victim']].rename(columns = {'killer': 'name', 'victim': 'instant_kill'}).groupby('name').count()
        kill_stealing = kill_check.loc[(kill_check['killer']!= kill_check['dbno_maker']) & (kill_check['dbno_id'] != -1)].loc[:, ['killer', 'victim']].rename(columns = {'killer': 'name', 'victim': 'kill_stealing'}).groupby('name').count() # 빼앗은 경우
        kill_stolen = kill_check.loc[(kill_check['killer']!= kill_check['dbno_maker']) & (kill_check['dbno_id'] != -1)].loc[:, ['dbno_maker', 'victim']].rename(columns = {'dbno_maker': 'name', 'victim': 'kill_stolen'}).groupby('name').count() # 빼앗긴 경우
        

        return_df = dbno_to_kill.merge(instant_kill, how = 'outer', left_index = True, right_index = True).merge(kill_stealing, how = 'outer', left_index = True, right_index = True).merge(kill_stolen, how = 'outer', left_index = True, right_index = True).fillna(0).astype(int)
            
            

        return return_df
    def heal_boost_revive_df(raw_stats_df, telemetry_json):
        # -> heal, boost, revive 관련 지표 Dataframe 출력
        def h_b_pickup_drop(telemetry_json):

            farming =[i for i in telemetry_json if i['_T'] == 'LogItemPickup']
            carepackage =[i for i in telemetry_json if i['_T'] == 'LogItemPickupFromCarepackage']
            lootbox =[i for i in telemetry_json if i['_T'] == 'LogItemPickupFromLootBox']
            pickup = farming + carepackage + lootbox
            pickup = [i for i in pickup if i['item']['category'] == 'Use']
            Boost_pickup_player = [i['character']['name'] for i in pickup if i['item']['itemId'].split('_')[1] == 'Boost']
            Boost_pickup_count = [i['item']['stackCount'] for i in pickup if i['item']['itemId'].split('_')[1] == 'Boost']
            Boost_pickup_df = pd.DataFrame({'name': Boost_pickup_player, 'Boost_pickup': Boost_pickup_count}).reset_index().groupby('name').sum()
            Heal_pickup_player = [i['character']['name'] for i in pickup if i['item']['itemId'].split('_')[1] == 'Heal']
            Heal_pickup_count = [i['item']['stackCount'] for i in pickup if i['item']['itemId'].split('_')[1] == 'Heal']
            Heal_pickup_df = pd.DataFrame({'name': Heal_pickup_player, 'Heal_pickup': Heal_pickup_count}).reset_index().groupby('name').sum()
            pickup_cnt = pd.merge(Boost_pickup_df, Heal_pickup_df, left_index= True, right_index= True, how = 'outer')
            
            #drop
            #drop =  telemetry_object.log_json('LogItemDrop')
            drop =[i for i in telemetry_json if i['_T'] == 'LogItemDrop']
            drop = [i for i in drop if i['item']['category'] == 'Use']
            Boost_drop_player = [i['character']['name'] for i in drop if i['item']['itemId'].split('_')[1] == 'Boost']
            Boost_drop_count = [i['item']['stackCount'] for i in drop if i['item']['itemId'].split('_')[1] == 'Boost']
            Boost_drop_df = pd.DataFrame({'name': Boost_drop_player, 'Boost_drop': Boost_drop_count}).groupby('name').sum()
            Heal_drop_player = [i['character']['name'] for i in drop if i['item']['itemId'].split('_')[1] == 'Heal']
            Heal_drop_count = [i['item']['stackCount'] for i in drop if i['item']['itemId'].split('_')[1] == 'Heal']
            Heal_drop_df = pd.DataFrame({'name': Heal_drop_player, 'Heal_drop': Heal_drop_count}).groupby('name').sum()
            drop_cnt = pd.merge(Boost_drop_df, Heal_drop_df, left_index= True, right_index= True, how = 'outer')
            
            # total cnt
            pickup_drop = pd.merge(pickup_cnt, drop_cnt, how = 'outer', left_index= True, right_index= True).fillna(0)
            pickup_drop['heal_have'] = pickup_drop['Heal_pickup'] - pickup_drop['Heal_drop']
            pickup_drop['boost_have'] = pickup_drop['Boost_pickup'] - pickup_drop['Boost_drop']
            return_df = pickup_drop.loc[:, ['heal_have', 'boost_have']].reset_index()
            return return_df
        def heal_amount(telemetry_json):
            heal_log = [i for i in telemetry_json if i['_T'] == 'LogHeal']
            heal_player = [i['character']['name'] for i in heal_log]
            heal_amount = [i['healamount'] for i in heal_log]
            heal_df = pd.DataFrame({'name': heal_player, 'amount': heal_amount}).groupby('name').sum()
            return heal_df
        
        stats_ = raw_stats_df.loc[:, ['name','boosts', 'revives', 'heals']].groupby('name').sum().reset_index()
        pickup_drop = h_b_pickup_drop(telemetry_json).reset_index()
        amount = heal_amount(telemetry_json).reset_index()
        return_df = pd.merge(stats_, pickup_drop, how = 'left', on= 'name').fillna(0)
        return_df = pd.merge(return_df, amount, how = 'left', left_on = 'name', right_on= 'name').fillna(0)
        return_df.loc[:,['boosts', 'revives', 'heals', 'heal_have', 'boost_have']] = return_df.loc[:,['boosts', 'revives', 'heals', 'heal_have', 'boost_have']].astype(int)
        return_df['heal_use_rate'] = round(return_df['heals'] / return_df['heal_have'] * 100, 2)
        return_df['boost_use_rate'] = round(return_df['boosts'] / return_df['boost_have'] * 100, 2)
        return_df['heal_amount'] = round(return_df['amount'], 2)
        return_df = return_df.set_index('name', drop= True).fillna(0)
        return return_df
    def stats_selected_df(attack_damage_adj_df, body_part_df, steal_kill_df):
        # -> 지표들 중 중요 지표만 선별한 Dataframe 출력
        activeshot_deal_adj = attack_damage_adj_df.loc[:, ['activeshot_deal_adj']]
        body_part = body_part_df.loc[:, ['headshot_cnt_rate', 'torsoshot_cnt_rate', 'pelvisshot_cnt_rate']]
        steal_kill = steal_kill_df.loc[:, ['kill_stealing', 'kill_stolen', 'dbno_to_kill']]
        body_part['head_torso_pelvis_shot_rate'] = round(body_part['headshot_cnt_rate'] + body_part['torsoshot_cnt_rate'] + body_part['pelvisshot_cnt_rate'],2)
        return_df_1 = pd.merge(activeshot_deal_adj, body_part[['head_torso_pelvis_shot_rate']], how= 'left', left_index= True, right_index= True)
        return_df_2 = pd.merge(return_df_1, steal_kill, how = 'left', left_index= True, right_index= True)
        return return_df_2

class Power_Rank:
    def __init__(self, Indicators = None):
        #self.Indicators, self.First_Indicators, self.Second_Indicators, self.PUBG_esports, self.raw_stats_df
        print('_____Power_Rank_class_____')
        if Indicators == None:
            pass
        else:
            self.Indicators = Indicators
            print('_Indicators_ready')
            self.First_Indicators = self.Indicators.First_Indicators()
            print('_First_Indicators_ready')
            self.Second_Indicators = self.Indicators.Second_Indicators()
            print('_Second_Indicators_ready')
            self.PUBG_esports = Indicators.PUBG_esports
            print('_PUBG_esports_ready')
            self.raw_stats_df = Indicators.raw_stats_df
            print('_Power_Rank_ready')
    def tournament_rank(self, tournament_tier):
        # -> 티어별로 구분된 토너먼트별 랭크 Dataframe 출력 (이때, 복수의 tournament_id가 입력된 경우, 복수의 match_id가 입력된 경우 모두 하나의 tournament로 전제)
        print('_tournemant_tier: ', tournament_tier, '_tier')
        _raw_attack_damage_df = self.Second_Indicators['raw_attack_damage_df']
        _steal_kill_df = self.Second_Indicators['steal_kill_df']
        match_list = self.Indicators.match_id
        print('_tournamant_match_count: ', len(match_list))
        _fight_ingrediants = Fight(self.PUBG_esports, match_id_list= match_list).Ingrediants_df()
        ingrediant_df = Power_Rank.ingrediant(self.raw_stats_df, _raw_attack_damage_df, _steal_kill_df, _fight_ingrediants)
        grb_ingrediant_df = ingrediant_df
        print('_power_rank_ingrediants_done')
        indicators_df = Power_Rank.indicators(ingrediant = grb_ingrediant_df)
        indicators_selected_df = indicators_df.loc[indicators_df['matches']> len(match_list) * 0.25]
        print('_power_rank_indicators_done')
        tournament_rank = Power_Rank.rank(indicators = indicators_selected_df, tournament_tier=tournament_tier)
        return {'rank': tournament_rank,'indicators': indicators_selected_df, 'ingrediants': grb_ingrediant_df }
    def ingrediant(raw_stats_df, raw_attack_damage_df, steal_kill_df, fight_ingrediants_df):
        # -> Power Rank 추출에 필요한 지표의 재료가 되는 집계값들 Dataframe 출력
        print('_power_rank_ingrediants')
        raw_stats_df['matches'] = raw_stats_df['match_id']
        return_1 = raw_stats_df.loc[:,['name','matches', 'timeSurvived', 'kills', 'DBNOs']].groupby('name').agg({'matches': 'count', 'timeSurvived': 'sum', 'kills': 'sum', 'DBNOs': 'sum'})
        return_2 = raw_attack_damage_df.loc[:,['deal_adj', 'attacks', 'activeshots', 'headshot_cnt','torsoshot_cnt', 'pelvisshot_cnt']].groupby('name').sum()
        return_3 = steal_kill_df.loc[:,['dbno_to_kill']].groupby('name').sum()
        return_4 = fight_ingrediants_df
        df = return_1.join(return_2, how = 'left').join(return_3, how = 'left').join(return_4, how = 'left')
        df['timeSurvived'] = round(df['timeSurvived'] / 60,2)
        df = df.fillna(0)
        return df            
    def indicators(ingrediant):
        # -> Power Rank 추출에 필요한 지표의 Dataframe 출력
        print('_power_rank_indicators')
        ingrediant_ = ingrediant.fillna(0)
        fight_indicators = Fight.fight_indicators_df(ingrediant_).set_index('name', drop = True)
        ingrediant_ = ingrediant.fillna(0)
        ingrediant_['deal_activeshot_adj'] = round(ingrediant_['deal_adj'] / ingrediant_['activeshots'],2)
        ingrediant_['activeshot_rate'] = round(ingrediant_['activeshots']/ingrediant_['attacks'] * 100, 2)
        ingrediant_['criticalshot_rate'] = round((ingrediant_['headshot_cnt'] + ingrediant_['torsoshot_cnt'] + ingrediant_['pelvisshot_cnt'])/ ingrediant['activeshots'] * 100,2)
        ingrediant_['kill_per_min'] = round(ingrediant_['kills']/ ingrediant_['timeSurvived'], 2)
        ingrediant_['down_per_min'] = round(ingrediant_['DBNOs']/ ingrediant_['timeSurvived'], 2)
        ingrediant_['down_to_kill_rate'] = round(ingrediant_['dbno_to_kill']/ ingrediant_['DBNOs'] * 100, 2)
        ingrediant_['deal_per_min_adj'] = round(ingrediant_['deal_adj']/ ingrediant_['timeSurvived'], 2)
        ingrediant_['activeshot_to_down_rate'] = round(ingrediant_['DBNOs'] / ingrediant_['activeshots'] * 100 , 2)
        return_df = ingrediant_.loc[:, ['matches','timeSurvived','kills','DBNOs','deal_activeshot_adj', 'activeshot_rate', 'criticalshot_rate', 'kill_per_min', 'down_per_min', 'down_to_kill_rate','activeshot_to_down_rate', 'deal_per_min_adj']]
        return_df_ = return_df.merge(fight_indicators, how = 'inner', left_index = True, right_index = True)
        return_df__ = return_df_.replace([np.inf, -np.inf], 0)
        return return_df__.fillna(0)    
    def rank(indicators, tournament_tier):
        # -> 토너먼트 티어에 따른 Power Score 계산하고 도출한 Power Rank의 Dataframe 출력
        print('_rank')
        # 절대평가 기준값으로 점수 부여하는 로직
        def rank_system(indi_df):
            indi_list = ['deal_activeshot_adj', 'activeshot_rate',
            'criticalshot_rate', 'kill_per_min', 'down_per_min','kills', 'DBNOs',
            'down_to_kill_rate', 'deal_per_min_adj', 'activeshot_to_down_rate', 'timeSurvived',
            'fight_survive_rate',
            'attacker_survive_rate', 'defender_survive_rate', 'fight_win_rate',
            'attacker_win_rate', 'defender_win_rate', 'fight_average_deal',
            'attacker_average_deal', 'defender_average_deal',
            'fight_attack_precision', 'attacker_attack_precision',
            'defender_attack_precision']
            #indi_df = indi_df.set_index('name', drop = True)
            indica= indi_df.loc[:, indi_list]
            score_dict = {}
            for indi in indi_list:
                indi_col = indica.loc[:, indi]
                indi_range = range[indi]
                def range__(x):
                    if x < indi_range[0]: 
                        return 0
                    elif (x >= indi_range[0]) & (x < indi_range[1]):
                        return 1
                    elif (x >= indi_range[1]) & (x < indi_range[2]):
                        return 2
                    elif (x >= indi_range[2]) & (x < indi_range[3]):
                        return 3
                    elif (x >= indi_range[3]) & (x < indi_range[4]):
                        return 4
                    elif (x >= indi_range[4]) & (x < indi_range[5]):
                        return 5
                    elif (x >= indi_range[5]) & (x < indi_range[6]):
                        return 6
                    elif (x >= indi_range[6]) & (x < indi_range[7]):
                        return 7
                    elif (x >= indi_range[7]) & (x < indi_range[8]):
                        return 8
                    elif (x >= indi_range[8]) & (x < indi_range[9]):
                        return 9
                    else:
                        return 10
                indi_col['score_' + indi] = indi_col.apply(lambda x: range__(x))
                globals()[indi] = indi_col['score_' + indi]
                score_dict[indi] = globals()[indi]
            score_df = pd.DataFrame(score_dict)
            return score_df
        # 토너먼트 기준별 절대평가 기준값
        if tournament_tier == 'SA':
            range = {'deal_activeshot_adj':[29.61, 30.87, 31.67, 32.34, 32.94, 33.75, 34.36, 35.46, 36.7, 38.2],
            'activeshot_rate': [5.43, 5.97, 6.89, 7.52, 8.46, 9.33, 10.08, 11.3, 12.53, 13.7],
            'criticalshot_rate': [69.67, 70.58, 72.83, 74.61, 75.91, 77.02, 78.2, 79.67, 82.02, 84.17], 
            'kill_per_min': [0.02, 0.02, 0.03, 0.03, 0.04, 0.05, 0.05, 0.06, 0.07, 0.08],
            'down_per_min': [0.02, 0.03, 0.03, 0.04, 0.04, 0.05, 0.05, 0.06, 0.07, 0.08],
            'kills': [10, 10, 20, 30, 40, 50, 60, 70, 80, 90, 90],
            'DBNOs': [10, 10, 20, 30, 40, 50, 60, 70, 80, 90, 90],
            'down_to_kill_rate': [44.19, 48.72, 53.97, 60.0, 62.71, 66.36, 68.48, 73.08, 78.33, 80.0], 
            'deal_per_min_adj': [7.4, 8.72, 9.81, 11.31, 12.99, 14.31, 15.69, 18.34, 20.38, 21.41], 
            'activeshot_to_down_rate': [8.01, 8.47, 9.29, 10.25, 10.69, 11.41, 11.79, 12.56, 14.44, 15.15],
            'fight_survive_rate': [77.36, 78.81, 80.48, 82.42, 83.52, 85.23, 86.19, 87.46, 88.97, 90.14],
            'timeSurvived': [100, 100, 200, 300, 400, 500, 600, 700, 800, 900, 900],
            'attacker_survive_rate': [86.55, 89.51, 90.36, 91.69, 92.57, 93.66, 94.57, 95.31, 96.27, 97.31], 
            'defender_survive_rate': [67.4, 68.53, 70.98, 73.26, 74.65, 76.5, 78.03, 79.29, 80.89, 81.47], 
            'fight_win_rate': [7.67, 8.36, 11.42, 13.48, 15.03, 16.53, 18.16, 20.42, 22.77, 23.84],
            'attacker_win_rate': [13.43, 14.79, 19.37, 21.83, 23.53, 25.93, 27.91, 31.05, 35.89, 40.43],
            'defender_win_rate': [1.27, 2.7, 4.07, 5.28, 6.33, 7.44, 8.68, 10.37, 11.5, 13.58], 
            'fight_average_deal': [2263.41, 2751.54, 3092.49, 3382.94, 3597.94, 3844.79, 4047.29, 4365.74, 4545.44, 4893.13], 
            'attacker_average_deal': [4644.77, 5043.8, 5190.2, 5385.66, 5568.62, 5775.31, 5918.26, 6178.86, 6365.4,  6472.86], 
            'defender_average_deal': [803.87, 1117.89, 1322.55, 1477.34, 1675.08, 1883.3, 2074.2, 2258.77, 2620.33, 2854.48], 
            'fight_attack_precision': [9.7, 10.01, 11.12, 11.88, 13.02, 14.09, 15.21, 16.82, 18.04, 18.31],
            'attacker_attack_precision': [11.2, 12.09, 13.35, 14.52, 15.72, 17.28, 18.88, 20.97, 23.18,  25.14], 
            'defender_attack_precision': [5.1,  5.71, 6.52,  7.51, 8.35, 9.18, 10.25, 11.69, 13.02, 13.3]}            
        else:
            range = {'deal_activeshot_adj': [28.99, 30.02, 31.06, 31.79, 32.5, 34.1, 35.07, 36.69, 39.37, 39.37], 
            'activeshot_rate': [5.0,  5.11, 7.22, 8.24, 8.7, 10.09, 11.48, 13.41, 16.82, 16.82], 
            'criticalshot_rate': [60.19, 66.67, 70.45, 73.33, 74.81, 78.0, 79.73, 82.29, 86.21, 86.21], 
            'kill_per_min': [0.01, 0.02, 0.03, 0.03, 0.04, 0.05, 0.06, 0.08, 0.09, 0.09], 
            'down_per_min': [0.01, 0.02, 0.03, 0.04, 0.04, 0.05, 0.06, 0.07, 0.09, 0.09], 
            'down_to_kill_rate': [25.0, 40.0, 52.63, 60.0, 63.64, 71.88, 77.08, 85.29, 100.0, 100.0], 
            'deal_per_min_adj': [6.31, 7.01, 9.31, 11.53, 12.6, 15.75, 17.84, 21.14, 26.26, 26.26], 
            'activeshot_to_down_rate': [4.14, 5.88, 8.44, 9.27, 9.89, 11.49, 12.5, 13.98, 16.18, 16.18], 
            'fight_survive_rate': [70.0, 73.53, 76.58, 78.46, 81.5, 84.0, 85.71, 87.74, 89.81, 89.81],
            'attacker_survive_rate': [78.79, 83.87, 86.67, 90.0, 91.04, 93.48, 95.03, 97.06, 100.0, 100.0],
            'defender_survive_rate': [41.67, 61.76, 66.67, 69.23, 70.97, 75.0, 76.92, 79.31, 81.87, 81.87],
            'fight_win_rate': [3.26,  6.33, 11.24, 13.64, 15.71, 19.83, 22.41, 25.17, 30.43, 30.43],
            'attacker_win_rate': [5.13,  12.31,  20.0, 22.54, 24.67, 30.26, 33.33, 38.71, 46.94, 46.94],
            'defender_win_rate': [0.0, 0.0, 3.12, 4.71, 5.81, 9.33, 11.76, 14.74, 18.42, 18.42],
            'fight_average_deal': [2075.13, 2411.92, 3076.81, 3476.79, 3691.58, 4194.65, 4507.18, 4993.07, 5512.41,  5512.41],
            'attacker_average_deal': [3846.44, 4643.38, 5198.13, 5532.6, 5752.93, 6158.06, 6337.8, 6669.83, 8533.25,  8533.25],
            'defender_average_deal': [801.22, 893.6, 1234.44, 1529.58, 1743.74, 2259.82, 2537.87, 2977.51, 4090.89,  4090.89],
            'fight_attack_precision': [7.58, 9.26, 10.51, 11.68, 13.0, 15.44, 17.28, 20.37,  28.63, 28.63],
            'attacker_attack_precision': [7.73, 10.21, 12.34, 14.28, 15.2, 19.0, 21.06, 25.88, 37.68, 37.68],
            'defender_attack_precision': [3.66, 4.81, 6.16, 7.29, 8.38, 10.86, 13.11, 16.12, 21.92, 21.92]}
        score = rank_system(indicators)
        # 영역별 점수, Power Score, Power Rank 계산
        score.loc[:,'Destructive_Power'] = score.loc[:,'deal_activeshot_adj'] 
        score.loc[:,'Accuracy'] = round(1/5 * (score.loc[:,'activeshot_rate'] + score.loc[:,'criticalshot_rate'] +(score.loc[:,'fight_attack_precision'] + score.loc[:,'attacker_attack_precision'] + score.loc[:,'defender_attack_precision'])),2)
        score.loc[:,'Finishing'] = round(1/4 * (score.loc[:,'kill_per_min'] + score.loc[:,'down_per_min'] + score.loc[:,'kills'] + score.loc[:,'DBNOs']),2)
        score.loc[:,'Concentration'] =  round(1/5  * (score.loc[:,'down_to_kill_rate'] + score.loc[:,'activeshot_to_down_rate'] + (score.loc[:,'fight_win_rate'] + score.loc[:,'attacker_win_rate'] + score.loc[:,'defender_win_rate'])),2)
        score.loc[:,'Threat'] = round(1/4 * (score.loc[:,'deal_per_min_adj'] + (score.loc[:,'fight_average_deal'] + score.loc[:,'attacker_average_deal'] + score.loc[:,'defender_average_deal'] )),2)
        score.loc[:,'Survival'] = round(1/4 * (score.loc[:,'timeSurvived'] +(score.loc[:,'fight_survive_rate'] + score.loc[:,'attacker_survive_rate'] + score.loc[:,'defender_survive_rate'])),2)
        score.loc[:,'Power_Score'] = round(10/ 6 * ( score.loc[:,'Destructive_Power'] + score.loc[:,'Accuracy'] + score.loc[:,'Finishing'] + score.loc[:,'Concentration'] + score.loc[:,'Threat'] + score.loc[:,'Survival'] ),2)
        ranking_ = score['Power_Score'].rank(method = 'dense', ascending = False).astype(int)
        score.loc[:,'Power_Rank'] = ranking_
        score = score.sort_values('Power_Rank')
        score_df = score.loc[:, ['Power_Rank', 'Power_Score', 
        'Destructive_Power', 'Accuracy','Finishing', 'Concentration', 'Threat', 'Survival',
        'deal_activeshot_adj','activeshot_rate', 'criticalshot_rate', 'fight_attack_precision', 'attacker_attack_precision','defender_attack_precision', 'kill_per_min', 'down_per_min', 'kills', 'DBNOs','down_to_kill_rate','activeshot_to_down_rate', 'fight_win_rate', 'attacker_win_rate', 'defender_win_rate','deal_per_min_adj','fight_average_deal', 'attacker_average_deal', 'defender_average_deal','timeSurvived','fight_survive_rate', 'attacker_survive_rate', 'defender_survive_rate']]
        return score_df
    def _rank(indicators, match_groupby_select):
        # z-score 활용했던 기존의 랭크 계산 함수 (for archive)
        def z_score_scoring(lst, indi):
            normalized_score = []
            for value in lst:
                normalized_num = (value - z_score_mean[indi]) / z_score_std[indi] + 5
                if indi in ['activeshot_rate', 'criticalshot_rate', 'kill_per_min', 'down_per_min']:
                    normalized_score.append(normalized_num/2)
                else:
                    normalized_score.append(normalized_num)
            return normalized_score
        def z_score_scoring_adj(lst, indi):
            normalized_score = []
            for value in lst:
                normalized_num = (value - z_score_mean[indi]) / z_score_std[indi] + 5
                if indi in ['activeshot_rate', 'criticalshot_rate', 'kill_per_min', 'down_per_min']:
                    normalized_score.append(normalized_num/2)
                else:
                    normalized_score.append(normalized_num)
            if indi in ['activeshot_rate', 'criticalshot_rate', 'kill_per_min', 'down_per_min']:
                adj_normalized_score = list(map(lambda x: 5 if x > 5 else(0 if x < 0 else x), normalized_score))
            else:
                adj_normalized_score = list(map(lambda x: 10 if x > 10 else(0 if x < 0 else x), normalized_score))
            return adj_normalized_score   
        if match_groupby_select == 'match':
            z_score_mean = {'deal_activeshot_adj': 29.30527222875049,
                            'activeshot_rate': 7.838117566106361,
                            'criticalshot_rate': 7.838117566106361,
                            'kill_per_min': 0.03294648166501487,
                            'down_per_min': 0.03790784313725491,
                            'down_to_kill_rate': 0.03790784313725491,
                            'deal_per_min_adj': 11.9336931206576}
            z_score_std = {'deal_activeshot_adj': 14.50658585036464,
                            'activeshot_rate': 5.794481945909203,
                            'criticalshot_rate': 5.794481945909203,
                            'kill_per_min': 0.042896031106013505,
                            'down_per_min': 0.044223090158774306,
                            'down_to_kill_rate': 0.044223090158774306,
                            'deal_per_min_adj': 9.684135540390615}
        else:

            z_score_mean = {'deal_activeshot_adj': 33.409130434782604,
                            'activeshot_rate': 8.816115107913669, 
                            'criticalshot_rate': 76.13918518518518, 
                            'kill_per_min': 0.040845070422535205, 
                            'down_per_min': 0.042624113475177305, 
                            'down_to_kill_rate': 62.47358208955223, 
                            'deal_per_min_adj': 13.401691176470589}
            z_score_std = {'deal_activeshot_adj': 1.3575556028652476, 
                           'activeshot_rate': 1.8792331632115788, 
                           'criticalshot_rate': 2.528243146960136, 
                           'kill_per_min': 0.01446184673236906, 
                           'down_per_min': 0.013871006041785034, 
                           'down_to_kill_rate': 6.50853428291793, 
                           'deal_per_min_adj': 3.109685664828487} 
        indicators_ = indicators
        indicator_list = ['deal_activeshot_adj', 'activeshot_rate','criticalshot_rate','kill_per_min', 'down_per_min','down_to_kill_rate', 'deal_per_min_adj']
        for indi in indicator_list:
            indicators_['score_'+indi] = z_score_scoring(list(indicators_[indi]), indi)
            indicators_['score_adj_'+indi] = z_score_scoring_adj(list(indicators_[indi]), indi)
        if match_groupby_select == 'match':
            indicators_['total_score'] =  indicators_.score_adj_activeshot_rate + indicators_.score_adj_criticalshot_rate + indicators_.score_adj_kill_per_min + indicators_.score_adj_down_per_min + indicators_.score_adj_deal_per_min_adj
        else:
            indicators_['total_score'] = indicators_.score_adj_deal_activeshot_adj + indicators_.score_adj_activeshot_rate + indicators_.score_adj_criticalshot_rate + indicators_.score_adj_kill_per_min + indicators_.score_adj_down_per_min + indicators_.score_adj_down_to_kill_rate + indicators_.score_adj_deal_per_min_adj
        indicators_['rank'] = indicators_['total_score'].rank(method='dense', ascending=False).astype(int)
        return_df = indicators_
        return_df['Destructive_Power'] = return_df['score_adj_deal_activeshot_adj']
        return_df['Accuracy'] = return_df['score_adj_activeshot_rate'] + return_df['score_adj_criticalshot_rate']
        return_df['Kill_Down_Finishing'] = return_df['score_adj_kill_per_min'] + return_df['score_adj_down_per_min']
        return_df['Momentary_Concentration'] = return_df['score_adj_down_to_kill_rate'] 
        return_df['Threat'] = return_df['score_adj_deal_per_min_adj']
        return_df = return_df.loc[:, [ 'matches','timeSurvived','rank','total_score', 'Destructive_Power', 'Accuracy', 'Kill_Down_Finishing', 'Momentary_Concentration','Threat','score_adj_deal_activeshot_adj', 'score_adj_activeshot_rate', 'score_adj_criticalshot_rate', 'score_adj_kill_per_min', 'score_adj_down_per_min', 'score_adj_down_to_kill_rate', 'score_adj_deal_per_min_adj', 'score_deal_activeshot_adj', 'score_activeshot_rate', 'score_criticalshot_rate', 'score_kill_per_min', 'score_down_per_min', 'score_down_to_kill_rate', 'score_deal_per_min_adj']]
        return_df = return_df.sort_values('rank')
        return return_df

class Fight:
    def __init__(self, PUBG_esports, tournament_id_list = [], match_id_list = []):
        # -> self.PUBG_esports, self.tournemant_id, self.match_id, self.telemetry_object
        print('_____Fight_class_____')
        self.PUBG_esports = PUBG_esports
        match_id_list_ = []
        if len(tournament_id_list) > 0:
            self.tournament_id = tournament_id_list
            for id in self.tournament_id:
                match_id_list_ += self.PUBG_esports.tournament(id).match_id
                time.sleep(50)
        else:
            match_id_list_ = match_id_list
        self.match_id = self.PUBG_esports.matches(match_id_list_).match_id
        print('_match_id_count: ', len(self.match_id))
        self.telemetry_object = self.PUBG_esports.telemetry(self.match_id)
    def Fights_dfs(self):
        # -> Fight 클래스에 입력된 key값으로 구한 교전 관련 Dataframe 출력
        _fight_log_df = Fight.fight_log_df(self.telemetry_object)
        _fight_groupby_df = Fight.fight_groupby_df(_fight_log_df)
        _fight_ingrediant_df = Fight.fight_ingrediants_df(_fight_groupby_df)
        _fight_indicator_df_ = Fight.fight_indicators_df(_fight_ingrediant_df)
        return {'fight_log_df': _fight_log_df, 'fight_groupby_df': _fight_groupby_df, 'fight_indicators_df': _fight_indicator_df_, 'fight_ingrediants_df': _fight_ingrediant_df }            
    def Log_df(self):
        # -> Fight 클래스에 입력된 key값으로 구한 교전 로그 Dataframe 출력
        _fight_log_df = Fight.fight_log_df(self.telemetry_object)
        return _fight_log_df
    def Groupby_df(self):
        # -> Fight 클래스에 입력된 key값으로 구한 교전별 정보 Dataframe 출력
        _fight_log_df = Fight.fight_log_df(self.telemetry_object)
        _fight_groupby_df = Fight.fight_groupby_df(_fight_log_df)
        return _fight_groupby_df
    def Ingrediants_df(self):
        # -> Fight 클래스에 입력된 key값으로 구한 선수별 교전 관련 정보 집계값 Dataframe 출력
        _fight_log_df = Fight.fight_log_df(self.telemetry_object)
        _fight_groupby_df = Fight.fight_groupby_df(_fight_log_df)
        _fight_ingrediant_df = Fight.fight_ingrediants_df(_fight_groupby_df)
        return _fight_ingrediant_df
    def Indicators_df(self):
        # -> Fight 클래스에 입력된 key값으로 구한 선수별 교전 관련 지표 Dataframe 출력
        _fight_log_df = Fight.fight_log_df(self.telemetry_object)
        _fight_groupby_df = Fight.fight_groupby_df(_fight_log_df)
        _fight_ingrediant_df = Fight.fight_ingrediants_df(_fight_groupby_df)
        _fight_indicator_df_ = Fight.fight_indicators_df(_fight_ingrediant_df)    
        return _fight_indicator_df_ 
    def fight_log_df(telemetry_object):
        # -> 교전 로그 DataFrame 출력
        match_id_list = []
        timing = []
        log_type = []
        attacker = []
        attacker_team = []
        attacker_x = []
        attacker_y = []
        attacker_z = []
        victim = []
        victim_team = []
        victim_x = []
        victim_y = []
        victim_z = []
        deal = []
        damage_type = []
        damage_reason = []
        
        def damage_(log):
            log_type.append('Damage')
            if log.get('attacker') is None:
                attacker.append('Null')
                attacker_team.append('Null')
                # attacker 가 없는 경우, BLUEZONE이거나 DROWN
                attacker_x.append('Null')
                attacker_y.append('Null')
                attacker_z.append('Null')
            else:
                attacker.append(log['attacker']['name'])
                attacker_team.append(log['attacker']['name'].split('_')[0])
                attacker_x.append(log['attacker']['location']['x'])
                attacker_y.append(log['attacker']['location']['y'])
                attacker_z.append(log['attacker']['location']['z'])
            victim.append(log['victim']['name'])
            victim_team.append(log['victim']['name'].split('_')[0])
            victim_x.append(log['victim']['location']['x'])
            victim_y.append(log['victim']['location']['y'])
            victim_z.append(log['victim']['location']['z'])
            deal.append(log['damage'])
            damage_type.append(log['damageTypeCategory'])
            damage_reason.append(log['damageReason'])
        def attack_(log):
            log_type.append('Attack')
            attacker.append(log['attacker']['name'])
            attacker_team.append(log['attacker']['name'].split('_')[0])
            attacker_x.append(log['attacker']['location']['x'])
            attacker_y.append(log['attacker']['location']['y'])
            attacker_z.append(log['attacker']['location']['z'])
            victim.append('Null')
            victim_team.append('Null')
            victim_x.append('Null')
            victim_y.append('Null')
            victim_z.append('Null')
            deal.append('Null')
            damage_type.append('Null')
            damage_reason.append('Null') 
        def kill1_(log):
            log_type.append('Kill')
            if log.get('killer') is None:
                attacker.append('Null')
                attacker_team.append('Null')
                attacker_x.append('Null')
                attacker_y.append('Null')
                attacker_z.append('Null')
            else:
                attacker.append(log['killer']['name'])
                attacker_team.append(log['killer']['name'].split('_')[0])
                attacker_x.append(log['killer']['location']['x'])
                attacker_y.append(log['killer']['location']['y'])
                attacker_z.append(log['killer']['location']['z'])
            victim.append(log['victim']['name'])
            victim_team.append(log['victim']['name'].split('_')[0])
            victim_x.append(log['victim']['location']['x'])
            victim_y.append(log['victim']['location']['y'])
            victim_z.append(log['victim']['location']['z'])
            deal.append('Null')
            damage_type.append(log['damageTypeCategory'])
            damage_reason.append(log['damageReason'])  
        def kill2_(log):
            log_type.append('Kill')
            if log.get('killer') is None:
                attacker.append('Null')
                attacker_team.append('Null')
                attacker_x.append('Null')
                attacker_y.append('Null')
                attacker_z.append('Null')
            else:
                attacker.append(log['killer']['name'])
                attacker_team.append(log['killer']['name'].split('_')[0])
                attacker_x.append(log['killer']['location']['x'])
                attacker_y.append(log['killer']['location']['y'])
                attacker_z.append(log['killer']['location']['z'])
            victim.append(log['victim']['name'])
            victim_team.append(log['victim']['name'].split('_')[0])
            victim_x.append(log['victim']['location']['x'])
            victim_y.append(log['victim']['location']['y'])
            victim_z.append(log['victim']['location']['z'])
            deal.append('Null')
            damage_type.append(log['finishDamageInfo']['damageTypeCategory'])
            damage_reason.append(log['finishDamageInfo']['damageReason'])

        fight_log = telemetry_object.damage_log_json() + telemetry_object.kill_log_json() + telemetry_object.attack_log_json()

        for log in fight_log:
            timing.append(log['_D'])
            match_id_list.append(log['_matchid'])
            type = log['_T']
            if type == 'LogPlayerTakeDamage':
                damage_(log)
            if type == 'LogPlayerAttack':
                attack_(log)
            if type == 'LogPlayerKill':
                kill1_(log)

        fight_log = pd.DataFrame({'match_id': match_id_list,'timing': timing, 'log_type': log_type, 
                                'attacker': attacker, 'attacker_team': attacker_team, 'attacker_x': attacker_x, 'attacker_y': attacker_y, 'attacker_z': attacker_z,
                                'victim': victim, 'victim_team': victim_team, 'victim_x': victim_x, 'victim_y': victim_y, 'victim_z': victim_z,
                                'deal': deal, 'damage_type': damage_type, 'damage_reason': damage_reason})
        fight_log['timing'] =  pd.to_datetime(fight_log['timing']).dt.tz_convert(None)
        return fight_log.reset_index(drop = True)   
         
    def fight_groupby_df(fight_log_df):
        # -> 교전별 정보 DataFrame 출력

        def damage(fight_log):
            # damage
            damage = fight_log.loc[(fight_log['log_type'] == 'Damage') & (fight_log['damage_type'] == 'Damage_Gun')]
            damage = damage.loc[damage['deal'] != 0]
            return damage

        def fight_damage(damage):
            damage_grb = damage.groupby(by = ['attacker', 'victim']).agg({'deal': 'sum', 'damage_type': 'count'}).reset_index().rename(columns={'damage_type': 'count', 'victim': 'defender'})
            fight_damage= pd.merge(damage_grb, damage_grb, how = 'left', left_on = ['attacker', 'defender'], right_on= ['defender', 'attacker']).drop(columns=['attacker_y', 'defender_y']).rename(columns={'attacker_x':'attacker', 'defender_x': 'defender', 'deal_x': 'attacker_deal', 'count_x': 'attacker_active_attack', 'deal_y': 'defender_deal', 'count_y': 'defender_active_attack'})   
            fight_damage['defender_active_attack'] = fight_damage['defender_active_attack'].fillna(0).astype(int)
            fight_damage['defender_deal'] = fight_damage['defender_deal'].fillna(0)
            fight_damage['defender_deal'] = [round(i,2) for i in fight_damage['defender_deal']]
            fight_damage['attacker_deal'] = [round(i,2) for i in fight_damage['attacker_deal']]
            return fight_damage

        def fight_time(damage):
            damage['timing_1'] = damage['timing']
            damage['timing_2'] = damage['timing']
            time_grb= damage.groupby(by = ['attacker', 'victim']).agg({'timing_1':'min', 'timing_2': 'max'}).reset_index().rename(columns={'victim': 'defender', 'timing_1': 'min_time', 'timing_2': 'max_time'})
            fight_time = pd.merge(time_grb, time_grb, how = 'left', left_on = ['attacker', 'defender'], right_on= ['defender', 'attacker']).drop(columns=['attacker_y', 'defender_y'])
            fight_len = []
            start_timing = []
            end_timing = []
            for a in range(len(fight_time)):
                if fight_time['min_time_y'][a] is None:
                    duration = (fight_time['max_time_x'][a] - fight_time['min_time_x'])
                    fight_len.append(duration.seconds + duration.microseconds * 1/1000000) ##
                    start_timing.append(fight_time['min_time_x'][a])
                    end_timing.append(fight_time['max_time_y'][a])
                else: 
                    end = max(fight_time['max_time_x'][a], fight_time['max_time_y'][a])
                    duration = (end - fight_time['min_time_x'][a])
                    fight_len.append(duration.seconds + duration.microseconds * 1/1000000) ##
                    start_timing.append(fight_time['min_time_x'][a])
                    end_timing.append(end)
            fight_time['start'] = start_timing
            fight_time['end'] = end_timing
            fight_time['duration'] = fight_len
            fight_time = fight_time[['attacker_x', 'defender_x', 'start', 'end', 'duration']].rename(columns = {'attacker_x': 'attacker', 'defender_x': 'defender'})
            return fight_time

        def fight_attack(fight_log, fight_time):
            attack = fight_log.loc[fight_log['log_type'] == 'Attack'].reset_index(drop=True)
            attacker_attack = []
            defender_attack = []
            for a in range(len(fight_time)):
                fight_attacker = fight_time['attacker'][a]
                fight_defender = fight_time['defender'][a]
                fight_start = fight_time['start'][a]  - datetime.timedelta(seconds = 1)
                fight_end = fight_time['end'][a]
                attacker_cnt = 0
                defender_cnt = 0        
                for b in range(len(attack)):
                    attacker = attack['attacker'][b]
                    attack_time = attack['timing'][b]
                    if fight_attacker == attacker and (attack_time >= fight_start) and (attack_time <= fight_end):
                        attacker_cnt += 1
                    elif fight_defender == attacker and (attack_time >= fight_start ) and (attack_time <= fight_end):
                        defender_cnt += 1
                    else:
                        continue
                attacker_attack.append(attacker_cnt)
                defender_attack.append(defender_cnt)

            fight_attack = fight_time.loc[:,['attacker', 'defender']]
            fight_attack['attacker_attack'] = attacker_attack
            fight_attack['defender_attack'] = defender_attack
            return fight_attack

        def fight_location_distance(fight_log, fight_time):
            attacker_walkdistance_list = []
            defender_walkdistance_list = []
            attacker_loc = []
            defender_loc = []
            fight_loc = []
            fight_distance = []
            for a in range(len(fight_time)):
                #attacker
                attacker_move = fight_log.loc[(fight_log['timing'] <= fight_time.end[a])&(fight_log['timing']>= fight_time.start[a])].loc[(fight_log['attacker'] == fight_time.attacker[a])|(fight_log['victim'] == fight_time.attacker[a])][['timing', 'log_type', 'attacker', 'victim', 'attacker_x', 'attacker_y', 'attacker_z', 'victim_x', 'victim_y', 'victim_z']].reset_index(drop= True)
                attacker_x = []
                attacker_y = []
                attacker_z = []
                for b in range(len(attacker_move)):
                    attacker_move_loc = attacker_move.loc[b]
                    if attacker_move_loc.attacker == fight_time.attacker[a]:
                        attacker_x.append(attacker_move_loc.attacker_x)
                        attacker_y.append(attacker_move_loc.attacker_y)
                        attacker_z.append(attacker_move_loc.attacker_z)
                    elif attacker_move_loc.victim == fight_time.attacker[a]:
                        attacker_x.append(attacker_move_loc.victim_x)
                        attacker_y.append(attacker_move_loc.victim_y)
                        attacker_z.append(attacker_move_loc.victim_z)
                    else:
                        continue
                attacker_move = []
                for c in range(len(attacker_x)):
                    if c == 0:
                        continue
                    else:
                        distance = ((attacker_x[c] - attacker_x[c-1])**2 + (attacker_y[c] - attacker_y[c-1])**2 + (attacker_z[c] - attacker_z[c-1])**2)**0.5
                        attacker_move.append(distance)
                attacker_move_sum = round(sum(attacker_move),2)
                attacker_walkdistance_list.append(attacker_move_sum)
                attacker_location = (round(np.mean(attacker_x),2),round(np.mean(attacker_y),2),round(np.mean(attacker_z)))
                attacker_loc.append(attacker_location)
                #defender
                defender_move = fight_log.loc[(fight_log['timing'] <= fight_time.end[a])&(fight_log['timing']>= fight_time.start[a])].loc[(fight_log['attacker'] == fight_time.defender[a])|(fight_log['victim'] == fight_time.defender[a])][['timing', 'log_type', 'attacker', 'victim', 'attacker_x', 'attacker_y', 'attacker_z', 'victim_x', 'victim_y', 'victim_z']].reset_index(drop= True)
                defender_x = []
                defender_y = []
                defender_z = []
                for b in range(len(defender_move)):
                    if defender_move.attacker[b] == fight_time.defender[a]:
                        defender_x.append(defender_move.attacker_x[b])
                        defender_y.append(defender_move.attacker_y[b])
                        defender_z.append(defender_move.attacker_z[b])
                    elif defender_move.victim[b] == fight_time.defender[a]:
                        defender_x.append(defender_move.victim_x[b])
                        defender_y.append(defender_move.victim_y[b])
                        defender_z.append(defender_move.victim_z[b])
                    else:
                        ConnectionRefusedError
                defender_move = []
                for c in range(len(defender_x)):
                    if c == 0:
                        continue
                    else:
                        distance = ((defender_x[c] - defender_x[c-1])**2 + (defender_y[c] - defender_y[c-1])**2 + (defender_z[c] - defender_z[c-1])**2)**0.5
                        defender_move.append(distance)
                
                defender_move_sum = round(sum(defender_move),2)
                defender_walkdistance_list.append(defender_move_sum)
                defender_location = (round(np.mean(defender_x),2), round(np.mean(defender_y),2), round(np.mean(defender_z),2))
                defender_loc.append(defender_location)
                fight_loc.append((round(np.mean([attacker_location[0], defender_location[0]]),2), round(np.mean([attacker_location[1], defender_location[1]]),2), round(np.mean([attacker_location[2], defender_location[2]]),2)))
                fight_distance_ = ((attacker_location[0] - defender_location[0])**2 + (attacker_location[0] - defender_location[0])**2 + (attacker_location[0] - defender_location[0])**2)**0.5
                fight_distance.append(round(fight_distance_,2))

            fight_location_distance = fight_time.loc[:,['attacker', 'defender']]
            fight_location_distance['attacker_move_distance'] = attacker_walkdistance_list
            fight_location_distance['defender_move_distance'] = defender_walkdistance_list
            fight_location_distance['attacker_location'] = attacker_loc
            fight_location_distance['defender_location'] = defender_loc
            fight_location_distance['fight_location'] = fight_loc
            fight_location_distance['fight_distance'] = fight_distance
            return fight_location_distance

        def fight_result(fight_log, fight):
            fight_kill = fight_log.loc[fight_log['log_type'] == 'Kill'].reset_index(drop= True).rename(columns = {'attacker': 'killer', 'victim': 'killed'}) 
            attacker_kill = pd.merge(fight, fight_kill, how = 'left', left_on = ['attacker', 'defender'], right_on= ['killer', 'killed'])[['attacker', 'defender', 'killer', 'killed']].rename(columns= {'killer': 'attacker_killer', 'killed': 'defender_killed'})
            defender_kill = pd.merge(fight, fight_kill, how = 'left', left_on = ['defender', 'attacker'], right_on= ['killer', 'killed'])[['attacker', 'defender', 'killer', 'killed']].rename(columns = {'killer': 'defender_killer', 'killed': 'attacker_killed'})
            kill_result = pd.merge(attacker_kill, defender_kill, how = 'inner', on = ['attacker', 'defender']).fillna(0)
            result = []
            for a in range(len(kill_result)):
                if kill_result.attacker_killer[a] == 0 and kill_result.defender_killer[a] == 0:
                    result.append('tie') 
                elif kill_result.attacker_killer[a] != 0 and kill_result.defender_killed[a] != 0:
                    result.append('attacker_win')
                elif kill_result.defender_killer[a] != 0 and kill_result.attacker_killed[a] != 0:
                    result.append('defender_win') 
                elif kill_result.defender_killer[a] != 0 and kill_result.attacker_killer[a] != 0:
                    result.append('tie_kill')
            kill_result['result'] = result
            fight_result = kill_result[['attacker', 'defender', 'result']]
            return fight_result

        def fights_(match_id,fight_damage, fight_time, fight_attack, fight_location_distance, fight_result):
            match_id_list = [match_id for i in range(len(fight_result))]
            fight = pd.merge(fight_result, pd.merge(fight_location_distance, pd.merge(fight_attack, pd.merge(fight_damage, fight_time, how = 'inner', on = ['attacker', 'defender']),how = 'inner', on = ['attacker', 'defender']),how = 'inner', on = ['attacker', 'defender']),how = 'inner', on = ['attacker', 'defender'])
            fight['match_id'] = match_id_list
            return fight
        print('_fight_groupby_df_')
        match_id_list = list(set(fight_log_df.match_id))
        for match_id in match_id_list:
            print(match_id)
            fight_log = fight_log_df.loc[fight_log_df['match_id'] == match_id]
            fight_log = fight_log.loc[:,['timing', 'log_type', 'attacker', 'attacker_team', 'attacker_x',
                'attacker_y', 'attacker_z', 'victim', 'victim_team', 'victim_x',
                'victim_y', 'victim_z', 'deal', 'damage_type', 'damage_reason']]
            damage_ = damage(fight_log)
            fight_damage_ = fight_damage(damage_)
            fight_ = fight_damage_[['attacker', 'defender']]
            fight_time_ = fight_time(damage_)
            fight_attack_ = fight_attack(fight_log, fight_time_)
            fight_location_distance_ = fight_location_distance(fight_log, fight_time_)
            fight_result_ = fight_result(fight_log, fight_)
            fight_df = fights_(match_id, fight_damage_, fight_time_, fight_attack_, fight_location_distance_, fight_result_)
            fight_df = fight_df[['match_id','start', 'end', 'duration', 'attacker', 'defender', 'result', 'attacker_attack', 'attacker_active_attack', 'attacker_deal', 'defender_attack', 'defender_active_attack', 'defender_deal', 'fight_location', 'fight_distance', 'attacker_location', 'attacker_move_distance', 'defender_location', 'defender_move_distance']]
            globals()[match_id + '_fight_df'] = fight_df
        return_df = pd.concat([globals()[id + '_fight_df'] for id in match_id_list])
        return return_df.reset_index(drop = True) 

    def fight_ingrediants_df(fight_groupby_df):
        # -> 교전 관련 정보 집계값 Dataframe 출력
        print('_fight_ingrediants_df_')
        fight_df = fight_groupby_df
        def result_ing(fight_df):
            attacker_tie = []
            attacker_win = []
            attacker_lose = []
            defender_tie = []
            defender_win = []
            defender_lose = []
            attacker_survive = []
            defender_survive = []
            for attacker_result in fight_df.attacker_result:
                if attacker_result == 'tie':
                    attacker_tie.append(1)
                    defender_tie.append(1)
                    attacker_win.append(0)
                    defender_win.append(0)
                    attacker_lose.append(0)
                    defender_lose.append(0)
                    attacker_survive.append(1)
                    defender_survive.append(1)
                elif attacker_result == 'attacker_win':
                    attacker_tie.append(0)
                    defender_tie.append(0)
                    attacker_win.append(1)
                    defender_win.append(0)
                    attacker_lose.append(0)
                    defender_lose.append(1)
                    attacker_survive.append(1)
                    defender_survive.append(0)      
                elif attacker_result == 'defender_win':
                    attacker_tie.append(0)
                    defender_tie.append(0)
                    attacker_win.append(0)
                    defender_win.append(1)
                    attacker_lose.append(1)
                    defender_lose.append(0)
                    attacker_survive.append(0)
                    defender_survive.append(1)

            result = fight_df.loc[:,['attacker', 'defender']]
            result['attacker_tie'] = attacker_tie
            result['attacker_win'] = attacker_win
            result['attacker_lose'] = attacker_lose
            result['defender_tie'] =  defender_tie
            result['defender_win'] = defender_win
            result['defender_lose'] = defender_lose
            result['attacker_survive'] = attacker_survive
            result['defender_survive'] = defender_survive

            defender_result = result.loc[:,['defender', 'defender_tie', 'defender_win', 'defender_lose', 'defender_survive']].groupby('defender').sum()
            attacker_result = result.loc[:,['attacker', 'attacker_tie', 'attacker_win', 'attacker_lose', 'attacker_survive']].groupby('attacker').sum()
            player_result = pd.merge(defender_result, attacker_result, how='outer', left_index= True, right_index= True).fillna(0).astype(int)
            player_result['defender_count'] = player_result['defender_tie'] + player_result['defender_win'] + player_result['defender_lose']
            player_result['attacker_count'] = player_result['attacker_tie'] + player_result['attacker_win'] + player_result['attacker_lose']
            player_result['fight_count'] = player_result['defender_count'] + player_result['attacker_count']
            player_result['fight_survive'] = player_result['defender_survive'] + player_result['attacker_survive']
            player_result['fight_win'] = player_result['defender_win'] + player_result['attacker_win']
            player_result['fight_lose'] = player_result['defender_lose'] + player_result['attacker_lose']
            player_result_df = player_result.loc[:,['fight_count', 'fight_survive', 'fight_win', 'fight_lose', 'attacker_count', 'attacker_survive', 'attacker_tie', 'attacker_win', 'attacker_lose', 'defender_count', 'defender_survive', 'defender_tie', 'defender_win', 'defender_lose']]
            return player_result_df        
        def attack_deal_ing(fight_df):
            attack_deal = fight_df.loc[:, ['attacker', 'defender', 'attacker_attack', 'attacker_active_attack', 'attacker_deal', 'defender_attack', 'defender_active_attack', 'defender_deal']]
            attacker_attack_deal = attack_deal.loc[:, ['attacker', 'attacker_attack', 'attacker_active_attack', 'attacker_deal']].groupby('attacker').agg({'attacker': 'count', 'attacker_attack': 'sum', 'attacker_active_attack': 'sum', 'attacker_deal': 'sum'}).rename(columns = {'attacker': 'attacker_count'})
            defender_attack_deal = attack_deal.loc[:, ['defender', 'defender_attack', 'defender_active_attack', 'defender_deal']].groupby('defender').agg({'defender': 'count', 'defender_attack': 'sum', 'defender_active_attack': 'sum', 'defender_deal': 'sum'}).rename(columns = {'defender': 'defender_count'})

            player_attack_deal = pd.merge(attacker_attack_deal, defender_attack_deal, how = 'outer', left_index= True, right_index= True).fillna(0)
            player_attack_deal['fight_count'] = player_attack_deal['attacker_count'] + player_attack_deal['defender_count']
            return player_attack_deal

        match_id_list = list(set(fight_df.match_id))
        for id in match_id_list:
            print(id)
            fight_df_ = fight_df.loc[fight_df['match_id'] == id, :]           
            fight_df_.loc[:,['defender_result']] = fight_df_.loc[:, ['result']]
            fight_df_ = fight_df_.rename(columns = {'result': 'attacker_result'})
            globals()[id + '_result_ing'] = result_ing(fight_df_)
            globals()[id + '_attack_deal_ing'] = attack_deal_ing(fight_df_) 
        result_ing_ = pd.concat([globals()[id + '_result_ing'] for id in match_id_list])
        result_ing_ = result_ing_.groupby(level= 0).sum()
        attack_deal_ing_ = pd.concat([globals()[id + '_attack_deal_ing'] for id in match_id_list])
        attack_deal_ing_ = attack_deal_ing_.groupby(level = 0).sum()
        fight_ing = pd.merge(result_ing_, attack_deal_ing_.drop(columns=['fight_count', 'attacker_count', 'defender_count']), how = 'inner', left_index= True, right_index= True)
        return fight_ing
    def fight_indicators_df(fight_ingrediants_df):
        # -> 교전 관련 지표 Dataframe 출력
        print('_fight_indicators_df_')
        def result_ind(result_ing):
            player_result = result_ing
            result_index = player_result.loc[:, ['fight_count']]
            result_index['fight_attacker_rate'] = round(player_result['attacker_count'] / result_index['fight_count'] * 100,2)
            result_index['fight_defender_rate'] = round(player_result['defender_count'] / result_index['fight_count'] * 100,2)
            result_index['fight_survive_rate'] = round(player_result['fight_survive'] / result_index['fight_count'] * 100,2)
            result_index['attacker_survive_rate'] = round(player_result['attacker_survive'] / player_result['attacker_count'] * 100,2)
            result_index['defender_survive_rate'] = round(player_result['defender_survive'] / player_result['defender_count'] * 100,2)
            result_index['fight_win_rate'] = round(player_result['fight_win'] / result_index['fight_count'] * 100,2)
            result_index['attacker_win_rate'] = round(player_result['attacker_win'] / player_result['attacker_count'] * 100,2)
            result_index['defender_win_rate'] = round(player_result['defender_win'] / player_result['defender_count'] * 100,2)

            return result_index
        def attack_deal_ind(attack_deal_ing):
            player_attack_deal = attack_deal_ing
            attack_deal_index = player_attack_deal.loc[:, ['fight_count','attacker_count','defender_count']].astype(int)
            attack_deal_index['fight_average_deal'] = round((player_attack_deal['attacker_deal'] + player_attack_deal['defender_deal']) / attack_deal_index['fight_count'] * 100,2)
            attack_deal_index['fight_attack_precision'] = round((player_attack_deal['attacker_active_attack'] + player_attack_deal['defender_active_attack']) / (player_attack_deal['attacker_attack']+ player_attack_deal['defender_attack']) * 100,2)
            attack_deal_index['attacker_average_deal'] = round(player_attack_deal['attacker_deal'] / attack_deal_index['attacker_count'] * 100,2)
            attack_deal_index['attacker_attack_precision'] = round(player_attack_deal['attacker_active_attack'] / player_attack_deal['attacker_attack'] * 100,2)
            attack_deal_index['defender_average_deal'] = round(player_attack_deal['defender_deal'] / attack_deal_index['defender_count'] * 100,2)
            attack_deal_index['defender_attack_precision'] = round(player_attack_deal['defender_active_attack'] / player_attack_deal['defender_attack'] * 100,2)
            attack_deal_index = attack_deal_index.fillna(0)
            return attack_deal_index
        fight_ingrediants_df = fight_ingrediants_df.loc[:, ['fight_count', 'fight_survive', 'fight_win', 'fight_lose',
                                                                        'attacker_count', 'attacker_survive', 'attacker_tie', 'attacker_win',
                                                                        'attacker_lose', 'defender_count', 'defender_survive', 'defender_tie',
                                                                        'defender_win', 'defender_lose', 'attacker_attack',
                                                                        'attacker_active_attack', 'attacker_deal', 'defender_attack',
                                                                        'defender_active_attack', 'defender_deal']]
        result_df = result_ind(fight_ingrediants_df)
        attack_deal_df = attack_deal_ind(fight_ingrediants_df).drop(columns=['fight_count', 'attacker_count', 'defender_count'])
        fight_indi = pd.merge(result_df, attack_deal_df, how = 'inner', left_index= True, right_index= True)
        fight_indi = fight_indi.reset_index().rename(columns= {'index': 'name'})
        fight_indi = fight_indi.loc[:, ['name','fight_count', 'fight_attacker_rate', 'fight_defender_rate', 'fight_survive_rate', 'attacker_survive_rate', 'defender_survive_rate', 'fight_win_rate', 'attacker_win_rate', 'defender_win_rate', 'fight_average_deal', 'attacker_average_deal', 'defender_average_deal', 'fight_attack_precision', 'attacker_attack_precision', 'defender_attack_precision']] 
        return fight_indi.reset_index(drop = True)

