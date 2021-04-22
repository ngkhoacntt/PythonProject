from bs4 import BeautifulSoup
import pyautogui
import time
import math

popular_league_list = ["Giải Anh - Premier League",
                       "Italy - Serie A",
                       "Germany - 1.Bundesliga",
                       "Giải La Liga, Tây Ban Nha",
                       "Giải Pháp - Ligue 1"]

club_allow_list = ["Leicester", "Atletico Madrid"]


def main():
    file_name = 'sport.sbtyo.com'
    # switch to firefox screen
    pyautogui.hotkey('winleft', '4')
    pyautogui.hotkey('ctrl', 's')
    time.sleep(1)  # wait to show save window
    pyautogui.typewrite(file_name + '.html')
    pyautogui.press('enter')
    time.sleep(1)  # wait to show override dialog
    pyautogui.press('left')
    pyautogui.press('enter')
    time.sleep(3)  # wait to save successful

    # switch to command screen
    pyautogui.hotkey('altleft', 'tab')

    soup = BeautifulSoup(open("C:/Users/Nguyen Khoa Hung/Downloads/" + file_name + ".html", encoding="utf8"), "html.parser")

    live_and_upcoming_match_divs = soup.find_all(attrs={"data-uat": "container-av-events-panel-event-list"})
    # do not have live match, only have upcoming match
    if len(live_and_upcoming_match_divs) == 1:
        print("Do not have live match \n")
        print("Upcoming match \n")
        print_match_info(live_and_upcoming_match_divs[0].find_all(class_="rj-asian-events__single-league"), False)

    else:  # have both live match and upcoming match
        print("Live match \n")
        live_match_divs = live_and_upcoming_match_divs[0].find_all(class_="rj-asian-events__single-league")
        print_match_info(live_match_divs, True)

        print("Upcoming match \n")
        upcoming_match_divs = live_and_upcoming_match_divs[1].find_all(class_="rj-asian-events__single-league")
        print_match_info(upcoming_match_divs, False)


def change_odd_format(original_odd, change_odd):
    if float(original_odd) > 0:
        new_odd = round(float(original_odd) - change_odd, 2)
    else:
        new_odd = round(1 + (1 + float(original_odd) - change_odd), 2)

    if math.isclose(new_odd, 1.0, rel_tol=0.001):
        return "đủ"
    else:
        return str(new_odd)

    # new_odd = round(float(original_odd) - change_odd, 2)
    # if new_odd > 0:
    #     # if round(abs(new_odd - 1.00), 2) < 0.01:
    #     #     return "đủ"
    #     if math.isclose(new_odd, 1.0, rel_tol=0.01):
    #         return "đủ"
    #     return str(new_odd)
    # return str(new_odd)


def change_handicap_format(original_handicap_odd, is_handicap_odd):
    is_under_dog_team = original_handicap_odd.startswith("+")
    new_handicap_odd = original_handicap_odd.replace("+", "")
    odd_after_split = new_handicap_odd.split("-")

    if ("-" not in original_handicap_odd) or (original_handicap_odd.startswith("-") and len(odd_after_split) < 3):
        return original_handicap_odd

    if new_handicap_odd.startswith("-") and len(odd_after_split) > 2:
        new_handicap_odd = str(round(float(odd_after_split[1]) + 0.25, 2))
    else:
        new_handicap_odd = str(round(float(odd_after_split[0]) + 0.25, 2))

    if is_handicap_odd:
        if is_under_dog_team:
            return "+" + new_handicap_odd
        else:
            return "-" + new_handicap_odd
    else:
        return new_handicap_odd


def reduce_handicap_odd_value(home_team, home_handicap, home_handicap_value, away_team, away_handicap_value):
    print("{0} {1} ăn {2}, {3} ăn {4}".format(home_team,
                                              change_handicap_format(home_handicap, True),
                                              change_odd_format(home_handicap_value, 0.05),
                                              away_team,
                                              change_odd_format(away_handicap_value, 0.05)))


def reduce_over_under_odd_value(over_under_odd, over_odd_value, under_odd_value):
    print("Tài {0} ăn {1}, xỉu ăn {2} \n".format(change_handicap_format(over_under_odd, False),
                                                 change_odd_format(over_odd_value, 0.05),
                                                 change_odd_format(under_odd_value, 0.05)))


def print_match_info(match_divs, is_live_match):
    home_team_temp = ""
    number_of_repeat_match = 0
    for match_div in match_divs:
        if match_div.div.h4.string not in popular_league_list:
            continue
        print(match_div.div.h4.string + "\n")  # show league name
        for row in match_div.find_all(class_="rj-asian-events__row"):
            home_team = row.find(attrs={"data-uat": "event-details-team-a-name"}).string
            away_team = row.find(attrs={"data-uat": "event-details-team-b-name"}).string
            if home_team == home_team_temp:
                if number_of_repeat_match > 0:
                    continue
                number_of_repeat_match = number_of_repeat_match + 1
            else:
                number_of_repeat_match = 0

            home_team_temp = home_team
            # filter match depends on club
            if home_team not in club_allow_list and away_team not in club_allow_list:
                continue

            if is_live_match:
                # show score and team name
                print(row.find(class_="rj-asian-events__event-time--live").string + " " + row.div.div.string)
                print(row.div.div.string + " " + home_team + " vs " + away_team)
            else:
                # show time and team name
                print(row.div.div.string + " " + home_team + " vs " + away_team)

            # get handicap and over under odd
            match_info_div = row.find(class_="rj-asian-events__column rj-asian-events__half-time-column")
            home_handicap = match_info_div.find(attrs={"data-uat": "av-event-odd-line-hdp-home"}).find(
                class_="rj-asian-events__odd-type").string

            try:
                # home is underdog
                if home_handicap is None:
                    home_handicap = "+" + match_info_div.find(attrs={"data-uat": "av-event-odd-line-hdp-away"}).find(
                        class_="rj-asian-events__odd-type").string
                else:
                    home_handicap = "-" + home_handicap
                home_handicap_value = match_info_div.find(attrs={"data-uat": "av-event-odd-line-hdp-home"}).find(
                    class_="rj-asian-events__odd-value").string
                away_handicap_value = match_info_div.find(attrs={"data-uat": "av-event-odd-line-hdp-away"}).find(
                    class_="rj-asian-events__odd-value").string
                over_under_odd = match_info_div.find(attrs={"data-uat": "av-event-odd-line-ou-home"}).find(
                    class_="rj-asian-events__odd-type").string
                over_odd_value = match_info_div.find(attrs={"data-uat": "av-event-odd-line-ou-home"}).find(
                    class_="rj-asian-events__odd-value").string
                under_odd_value = match_info_div.find(attrs={"data-uat": "av-event-odd-line-ou-away"}).find(
                    class_="rj-asian-events__odd-value").string
            except TypeError:
                print("\n")
                continue

            # show odd from site
            print("{0} {1} ăn {2}, {3} ăn {4}".format(home_team, change_handicap_format(home_handicap, True),
                                                      change_odd_format(home_handicap_value, 0),
                                                      away_team, change_odd_format(away_handicap_value, 0)))
            print("Tài {0} ăn {1}, xỉu ăn {2}".format(change_handicap_format(over_under_odd, False),
                                                      change_odd_format(over_odd_value, 0),
                                                      change_odd_format(under_odd_value, 0)))
            # show odd after reduce
            reduce_handicap_odd_value(home_team, home_handicap, home_handicap_value, away_team, away_handicap_value)
            reduce_over_under_odd_value(over_under_odd, over_odd_value, under_odd_value)


if __name__ == "__main__":
    main()
