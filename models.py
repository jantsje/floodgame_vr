from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c
)

from django.utils.translation import ugettext_lazy as _
import random  # necessary for random risk_high
from django import forms

author = 'Jantsje Mol'

doc = """
Investeringsspel voor huiseigenaren (online versie in het Nederlands)
"""


class Constants(BaseConstants):
    name_in_url = 'onderzoek'
    players_per_group = None
    scenarios = ["LH"]
    scenarios_no_insurance = ["risk1"]
    num_start_pages = 4
    num_end_pages = 12
    num_test_years = 1
    num_def_years = 1
    num_rounds = num_start_pages + num_test_years + num_def_years + num_end_pages
    risk = 1
    damage = c(50000)  # size of damage in case of a flood
    lower_premium = 0.8
    jaar = 25
    scaling_lossfunction = -0.0002
    house_value = c(240000)
    initial_endowment = c(65000)
    total_earnings = house_value + initial_endowment
    willingness_values = list(range(0, 11))
    fair = c(40)
    monthly_subsidized = c(32)

    ''' houses for floodrisk  '''
    itemss = list(range(1, 51))
    items = ["{0:0=3d}".format(value) for value in itemss]
    itemss2 = list(range(51, 101))
    items2 = ["{0:0=3d}".format(value) for value in itemss2]

    translated_languages = ['en', 'es', 'nl']  # list of allowed languages


TRNSL_ERR_MSG = 'Translation for this language does not exist'


class Subsession(BaseSubsession):

    def creating_session(self):
        assert self.session.config.get('language', 'en') \
               in Constants.translated_languages, TRNSL_ERR_MSG

        if self.round_number == 1:

            self.session.vars["mitigation_cost"] = [0, 1000, 5000, 10000, 15000]
            #                               name treatment        niet doelgroep, doelgroep, completed
            self.session.vars["telling"] = {"baseline":             ([], [], []),
                                            # "norm_all":             ([], [], []),
                                            # "norm_high":            ([], [], []),
                                            "norm_focusing":        ([], [], []),
                                            "norm_focusing_1":      ([], [], []),
                                            "baseline_1":           ([], [], []),
                                            "not yet":              ([], [], [])
                                            }

            self.session.vars["combinations"] = []
            if not self.session.config['demo']:
                self.session.vars["combinations"].extend(['baseline'] * self.session.config['quota_baseline'])
                # self.session.vars["combinations"].extend(['norm_all'] * self.session.config['quota_norm_all'])
                # self.session.vars["combinations"].extend(['norm_high'] * self.session.config['quota_norm_high'])
                self.session.vars["combinations"].extend(['norm_focusing'] * self.session.config['quota_norm_focusing'])
                self.session.vars["combinations"].extend(['baseline_1'] * self.session.config['quota_baseline_1'])
                self.session.vars["combinations"].extend(['norm_focusing_1'] *
                                                         self.session.config['quota_norm_focusing_1'])

        for p in self.get_players():

            sconfig = self.session.config

            p.participant.vars["treatment"] = 'not yet'  # you need something here to be able to append

            if self.round_number == 1:
                p.participant.vars["completed"] = False
                p.participant.vars["flooded"] = False
                p.participant.vars["mitigated"] = False
                self.session.vars["quota_full"] = False
                p.participant.vars["target_group"] = 'not answered yet'
                p.participant.vars["conversion"] = sconfig.get('real_world_currency_per_point')
                p.participant.vars["max_payoff"] = 0
                p.participant.vars["demo"] = False
                p.participant.vars["timespent"] = ''
                p.participant.vars["belief"] = 999
                p.participant.vars["insurance_choice"] = False
                p.participant.vars["edu_text_needed"] = False
                p.participant.vars["page_title"] = ''
                p.participant.vars["damaged_amount_needed"] = False
                p.participant.vars["other_text"] = ''
                p.participant.vars["evacuated_text_needed"] = False
                p.participant.vars["responsible_needed"] = False
                p.participant.vars["floor_size_needed"] = True
                p.participant.vars["neighbors_needed"] = False
                p.participant.vars["opened_instructions"] = 0
                p.participant.vars["selected_scenario"] = random.randint(1, 6)
                p.participant.vars["selected_pref"] = random.randint(1, 7)
                p.participant.vars["selected_additional"] = random.randint(1, 3)
                p.participant.vars["payoff_small"] = 0
                p.participant.vars["left_selected"] = random.choice([True, False])
                p.participant.vars["left_selected2"] = random.choice([True, False])
                p.participant.vars["cumulative_payoff"] = 0
                p.participant.vars["mitigate_more"] = 0
                p.participant.vars["payoff_scenario1"] = 0
                p.participant.vars["page_title"] = ""
                p.participant.vars["reduced_damage"] = (c(50000), c(45242), c(30327), c(18394), c(11157))
                p.participant.vars["mitigation_cost"] = ([c(0), c(1000), c(5000), c(10000), c(15000)])
                p.participant.vars["mitigated_before"] = 0
                p.participant.vars["in_scenario"] = False
                p.participant.vars["mitigated_this_scenario"] = 999
                p.participant.vars["mitigation_cost_this_scenario"] = 999
                p.participant.vars["floodrisk_percent"] = 999
                p.participant.vars["reduced_damage_this_scenario"] = Constants.damage
                p.participant.vars["total_opened"] = 0
                p.mitigation_cost = 0

            if self.round_number == 5 or self.round_number == 6:

                flood_nrs = []
                for year in range(1, 25 + 1):
                    flood_nr = random.sample(range(1, 101), Constants.risk)
                    flood_nrs.append(*flood_nr)
                flood_nrs_unique = list(set(flood_nrs))
                p.flood_nrs = str(["{0:0=3d}".format(value) for value in flood_nrs_unique])
                if "012" in p.flood_nrs:
                    p.flooded = True
                else:
                    p.flooded = False

            p.high_risk = False
            p.risk = Constants.risk

    def vars_for_admin_report(self):
        target_group = [len(self.session.vars["telling"]["baseline"][0]) +
                        # len(self.session.vars["telling"]["norm_all"][0]) +
                        # len(self.session.vars["telling"]["norm_high"][0]) +
                        len(self.session.vars["telling"]["baseline_1"][0]) +
                        len(self.session.vars["telling"]["norm_focusing"][0]) +
                        len(self.session.vars["telling"]["norm_focusing_1"][0])
                        ]
        dropouts = [len(self.session.vars["telling"]["baseline"][1]) -
                    len(self.session.vars["telling"]["baseline"][2]),
                    # len(self.session.vars["telling"]["norm_all"][1]) -
                    # len(self.session.vars["telling"]["norm_all"][2]),
                    # len(self.session.vars["telling"]["norm_high"][1]) -
                    # len(self.session.vars["telling"]["norm_high"][2]),
                    len(self.session.vars["telling"]["baseline_1"][1]) -
                    len(self.session.vars["telling"]["baseline_1"][2]),
                    len(self.session.vars["telling"]["norm_focusing"][1]) -
                    len(self.session.vars["telling"]["norm_focusing"][2]),
                    len(self.session.vars["telling"]["norm_focusing_1"][1]) -
                    len(self.session.vars["telling"]["norm_focusing_1"][2]),
                    len(self.session.vars["telling"]["not yet"][1])]
        completes = [len(self.session.vars["telling"]["baseline"][2]),
                     len(self.session.vars["telling"]["baseline_1"][2]),
                     # len(self.session.vars["telling"]["norm_all"][2]),
                     # len(self.session.vars["telling"]["norm_high"][2]),
                     len(self.session.vars["telling"]["norm_focusing"][2]),
                     len(self.session.vars["telling"]["norm_focusing_1"][2])
                     ]
        quota = [self.session.config['quota_baseline'],
                 # self.session.config['quota_norm_all'],
                 # self.session.config['quota_norm_high'],
                 self.session.config['quota_baseline_1'],
                 self.session.config['quota_norm_focusing'],
                 self.session.config['quota_norm_focusing_1']]
        vars_admin_list = [[p.participant.code,
                            p.participant.vars["treatment"],
                            p.participant.vars["mitigation_cost_this_scenario"],
                            p.participant.vars["belief"],
                            p.participant.vars["timespent"]]
                           for p in self.get_players()]
        return {'vars_admin_list': vars_admin_list,  'target_group': target_group,
                'dropouts': dropouts, 'dropouts_totaal': sum(dropouts),
                'completes_totaal': sum(completes), 'completes': completes,
                'quota': quota, 'quota_totaal': sum(quota)}


class Group(BaseGroup):  # it is an individual decision making game
    pass


class Player(BasePlayer):

    # you first need to set up fields for the variables,
    # they are later changed in the set_payoffs and before_session_starts methods
    consent = models.BooleanField()
    browser = models.StringField()
    store_treatment = models.StringField()
    high_risk = models.BooleanField()

    understanding_questions_wrong_attempts = models.PositiveIntegerField()
    # number of wrong attempts on understanding questions page

    pay_premium = models.StringField()
    mitigate = models.IntegerField(initial=0)  # is necessary for numpy to have an initial value
    belief = models.IntegerField()
    homeowner = models.BooleanField()
    accept_fair = models.BooleanField()
    accept_lower = models.BooleanField()
    mitigation_cost = models.CurrencyField()
    pay_damage = models.StringField()
    floodnr = models.IntegerField()
    flooded = models.BooleanField()
    buy_house = models.StringField()
    scenario = models.StringField()
    scenario_nr = models.IntegerField()
    year = models.IntegerField()
    opened = models.IntegerField(initial=0)
    total_opened = models.IntegerField()

    risk = models.IntegerField()

    premium = models.CurrencyField()
    flood_nrs = models.StringField()

    selected = models.StringField()
    selected2 = models.StringField()
    selected_button = models.StringField()
    bigprize = models.StringField()

    clicked_button = models.IntegerField(initial=0)

    # SAVING PAYOFFS FOR RESULTS #######
    payoff_scenario1 = models.CurrencyField()
    total_payoff = models.FloatField()

    # ''' vragen moeten hier anders werkt het dynamisch kiezen van een taal niet '''

    difficult = models.IntegerField(
        label=_("How easy or difficult was it to make a choice in the investment game you just played?"),
        choices=[(1, _("Very easy")),
                 (2, _("Somewhat easy")),
                 (3, _("Neither easy/nor difficult")),
                 (4, _("Somewhat difficult")),
                 (5, _("Very difficult"))])

    # note: without this default option, an empty checkbox will be displayed that is initially selected)

    explain_strategy = models.LongStringField(
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 100}),
        label=_("Please briefly explain how you made decisions in the investment game."))

    age = models.PositiveIntegerField(label=_("What is your age?"),
                                      help_text=_("years"), min=18, max=120)

    gender = models.IntegerField(choices=[(0, _('Male')), (1, _('Female'))],
                                 label=_("What is your gender?"),
                                 widget=widgets.RadioSelectHorizontal,
                                 )

    flood_prob = models.IntegerField(
        label=_("What is the likelihood that your home will be flooded in the next 25 years?"),
        choices=[(0, _("The probability is zero")),
                 (1, _("Very low")),
                 (2, _("Low")),
                 (3, _("Not low/not high")),
                 (4, _("High")),
                 (5, _("Very high")),
                 (99, _("Don't know"))]
    )

    water_levels = models.IntegerField(
        label=_("Imagine your neighborhood is flooded. What height do you think the water would reach in your home?"),
        choices=[(0, _("The water would not reach my home")),
                 (1, _("Low (1-10 cm)")),
                 (2, _("Pretty high (10-50 cm)")),
                 (3, _("Fairly high (50-100 cm)")),
                 (4, _("High (1-2 meter)")),
                 (5, _("Very high (more than 2 meter)"))]
    )

    measures = models.StringField(widget=forms.CheckboxSelectMultiple,
                                  label=_("Please indicate which measures you have taken in your current home to "
                                          "protect your home against flood damage. (You can specify more than one.)"),
                                  blank=True)

    cellar_responsible = models.IntegerField(blank=True, label=_("No valuables in basement"))

    furniture_responsible = models.IntegerField(blank=True, label=_("Water-resistant furniture on ground floor"))

    floor_elevated_responsible = models.IntegerField(blank=True, label=_("Elevated ground floor"))

    foundation_responsible = models.IntegerField(blank=True, label=_("Strengthened foundation"))

    walls_responsible = models.IntegerField(blank=True, label=_("Walls made of water-resistant materials"))

    floor_water_resistant_responsible = models.IntegerField(blank=True, label=_(
        "Floor of ground floor made of water-resistant materials (e.g. tile floor)"))

    sockets_raised_responsible = models.IntegerField(blank=True, label=_("Raised power sockets on ground floor"))

    valves_responsible = models.IntegerField(blank=True, label=_("Anti-backflow valves"))

    sandbags_responsible = models.IntegerField(blank=True, label=_("(Empty) sand bags or flood barriers at home"))

    appliances_elevated_responsible = models.IntegerField(blank=True, label=_("Elevated electrical appliances"))

    boiler_responsible = models.IntegerField(blank=True, label=_("Elevated boiler"))

    meter_elevated_responsible = models.IntegerField(blank=True, label=_("Elevated electricity meter"))

    insured_responsible = models.IntegerField(blank=True, label=_("Bought separate flood insurance"))

    other_responsible = models.IntegerField(blank=True, label="Other:")

    other_text = models.StringField(blank=True)

    income = models.IntegerField(
        label=_("What is your household monthly income (after taxes)?"),
        choices=[(0, _("Less than €500")),
                 (1, _("Between €500 and €999")),
                 (2, _("Between €1,000 and €1,499")),
                 (3, _("Between €1,500 and €1,999")),
                 (4, _("Between €2,000 and €2,499")),
                 (5, _("Between €2,500 and €2,999")),
                 (6, _("Between €3,000 and €3,499")),
                 (7, _("Between €3,500 and €3,999")),
                 (8, _("Between €4,000 and €4,499")),
                 (9, _("Between €4,500 and €4,999")),
                 (10, _("Between €5,000 and €5,499")),
                 (11, _("Between €5,500 and €5,999")),
                 (12, _("€6,000 or more")),
                 (99, _("Don’t know")),
                 (88, _("Rather not say"))
                 ]
    )

    neighbors_measures = models.IntegerField(
        label=_("Do you know anyone in your community who has taken one or more of these measures?"),
        choices=[(1, _("Yes")), (0, _("No"))],
        widget=widgets.RadioSelectHorizontal)

    neighbors_relation = models.StringField(label=_("Please indicate your relationship to the person(s) who "
                                                     "invested in one or more damage reducing measures."),
                                             blank=True,
                                             widget=forms.CheckboxSelectMultiple)

    house_type = models.IntegerField(label=_("Please indicate which of the following "
                                             "best describes the home you live in."))

    edu = models.IntegerField(label=_("What is the highest level of education you have completed?"))

    postcode = models.StringField(
        label=_("What is your zipcode?"),
        blank=True)

    zip_code_nrs = models.IntegerField(blank=True)
    zip_code_letters = models.StringField(blank=True)

    feedback = models.LongStringField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 130}),
                                      label=_(
                                          "This is the end of the survey. "
                                          "In case you have comments, please leave them here."),
                                      blank=True)

    evacuated = models.IntegerField(label=_("Have you ever been evacuated due to a threat of flooding?"),
                                    choices=[(1, _("Yes")), (0, _("No"))],
                                    widget=widgets.RadioSelectHorizontal,
                                    )

    expected_damage = models.IntegerField(
        label=_("In the event of a future flood, how much damage would you expect to your home and property?"),
        choices=[(0, _("Less than €500")),
                 (1, _("Between €500 and €999")),
                 (2, _("Between €1,000 and €4,999")),
                 (3, _("Between €5,000 and €9,999")),
                 (4, _("Between €10,000 and €24,999")),
                 (5, _("Between €25,000 and €49,999")),
                 (6, _("Between €50,000 and €74,499")),
                 (7, _("Between €75,000 and €99,999")),
                 (8, _("Between €100,000 and €249,999")),
                 (9, _("Between €250,000 and €499,999")),
                 (10, _("€500,000 or more")),
                 (99, _("Don’t know")),
                 ])

    home = models.IntegerField(label=_("What is the approximate market value of your home?"),
                               choices=[(0, _("Less than €100,000")),
                                        (1, _("Between €100,000 and €149,000")),
                                        (2, _("Between €150,000 and €199,999")),
                                        (3, _("Between €200,000 and €249,000")),
                                        (4, _("Between €250,000 and €299,999")),
                                        (5, _("Between €300,000 and €349,000")),
                                        (6, _("Between €350,000 and €399,999")),
                                        (7, _("Between €400,000 and €449,000")),
                                        (8, _("Between €450,000 and €499,999")),
                                        (9, _("Between €500,000 and €549,000")),
                                        (10, _("Between €550,000 and €599,999")),
                                        (11, _("Between €600,000 and €649,000")),
                                        (12, _("Between €650,000 and €699,999")),
                                        (13, _("Between €700,000 and €749,000")),
                                        (14, _("Between €750,000 and €799,999")),
                                        (15, _("€800,000 or more")),
                                        (99, _("Don’t know")),
                                        (88, _("Rather not say"))
                                        ])

    floor_size = models.IntegerField(label=_("Please indicate the size of your ground floor in square meters."),
                                     help_text="m2")

    flood_prone = models.IntegerField(
        label=_("Do you currently live in a flood-prone area?"),
        choices=[(1, _("Yes, I am certain that I live in a flood-prone area.")),
                 (2, _("Yes, I think that I live in a flood-prone area, but I am not sure.")),
                 (3, _("No, I am certain that I do not live in a flood-prone area.")),
                 (99, _("Don't know"))],
        widget=widgets.RadioSelect,
    )

    damaged = models.IntegerField(
        label=_("Have you ever experienced damage to your home due to a flood?"),
        choices=[(1, _("Yes")), (0, _("No"))],
        widget=widgets.RadioSelectHorizontal,
    )

    damaged_amount = models.IntegerField(
        label=_("What was the total cost of flood damage to your home and its content, as a result of this flood?"),
        choices=[(0, _("Less than €500")),
                 (1, _("Between €500 and €999")),
                 (2, _("Between €1,000 and €4,999")),
                 (3, _("Between €5,500 and €9,999")),
                 (4, _("Between €10,000 and €24,999")),
                 (5, _("Between €25,000 and €49,999")),
                 (6, _("Between €50,000 and €74,499")),
                 (7, _("Between €75,000 and €99,999")),
                 (8, _("Between €100,000 and €249,999")),
                 (9, _("Between €250,000 and €499,999")),
                 (10, _("€500,000 or more")),
                 (99, _("Don’t know")),
                 ])

    exact_flood_risk_perception = models.StringField(
        label=_("Please estimate how often your neighborhood could be flooded. "
                "You may enter any number (not only the numbers on the scale). "),
        help_text=_("years")
    )

    regret1 = models.IntegerField(
        label=_("When a flood occurred in the scenario, "
                "I felt regret about not investing (more) in protection."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    regret2 = models.IntegerField(
        label=_("When no flood occurred in the scenario, I felt regret about paying for protection."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    regret3 = models.IntegerField(
        label=_("I would feel regret about not investing in protection, "
                "if a flood would have occurred in the scenario."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    norm1 = models.IntegerField(
        label=_("People in my direct environment would approve an investment in damage reducing measures."),
        blank=True)

    norm2 = models.IntegerField(
        label=_("People in my direct environment think that I should invest in damage reducing measures."),
        blank=True)

    personal_norm = models.IntegerField(
        label=_("I am morally obligated to take measures to reduce flood risk to my home."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    worry = models.IntegerField(
        label=_("I am worried about the danger of flooding at my current residence."),
        blank=True)

    trust_dikes = models.IntegerField(
        label=_("I am confident that the dikes in my country are maintained well."),
        blank=True)

    concern = models.IntegerField(
        label=_("The probability of flooding at my current residence is too low to be concerned about."),
        blank=True)

    self_responsibility = models.IntegerField(
        label=_("It is the responsibility of a property owner to protect their property from flood damage."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    trust_messenger = models.IntegerField(
        label=_("The information presented in the scenario about previous participants is trustworthy."),
        choices=[(1, _("Strongly disagree")),
                 (2, _("Disagree")),
                 (3, _("Neither agree nor disagree")),
                 (4, _("Agree")),
                 (5, _("Strongly agree"))
                 ])

    time_qual = models.IntegerField(
        label=_("How willing are you to give up money today in order to benefit from it in the future?"))

    risk_qual = models.IntegerField(
        label=_("In general, how willing or unwilling are you to take risks?"))

    perceived_efficacy = models.IntegerField(
        label=_(
            "How effective is it to invest in flood protection measures that limit flood damage for your current home?"),
        choices=[(1, _("Very effective")),
                 (2, _("Effective")),
                 (3, _("Neither effective nor ineffective")),
                 (4, _("Ineffective")),
                 (5, _("Very ineffective")),
                 (99, _("Don't know"))]
    )

    perceived_cost = models.IntegerField(
        label=_("How costly is it to take flood protection measures that limit flood damage for your current home?"),
        choices=[(1, _("Very cheap")),
                 (2, _("Cheap")),
                 (3, _("Neither cheap nor costly")),
                 (4, _("Costly")),
                 (5, _("Very costly")),
                 (99, _("Don't know"))]

    )

    self_efficacy = models.IntegerField(
        label=_("Aside from the cost, how difficult is it to take flood protection measures that limit "
                "flood damage for your current home?"),
        choices=[(1, _("Very easy")),
                 (2, _("Somewhat easy")),
                 (3, _("Neither easy/nor difficult")),
                 (4, _("Somewhat difficult")),
                 (5, _("Very difficult")),
                 (99, _("Don't know"))]
    )

    sns1 = models.IntegerField(
        label=_("How good are you at working with fractions?"))

    sns2 = models.IntegerField(
        label=_("How good are you at figuring out how much a shirt will cost if it is 25% off?"))

    sns3 = models.IntegerField(
        label=_("How often do you find numerical information to be useful?"))

    collectivism1_r = models.IntegerField(
        label=_("I would not let my cousin(s) use my car (if I have one)."))

    collectivism2 = models.IntegerField(
        label=_("It is enjoyable to meet and talk with my neighbors regularly."))

    collectivism3_r = models.IntegerField(
        label=_("I would not discuss newly acquired knowledge with my parents."))

    collectivism4_r = models.IntegerField(
        label=_("It is not appropriate for a colleague to ask me for money."))

    collectivism5_r = models.IntegerField(
        label=_("I would not let my neighbors borrow things from me or my family."))

    collectivism6 = models.IntegerField(
        label=_("When deciding what kind of education to have, I would pay no attention to my uncles’ advice."))

    collectivism7_r = models.IntegerField(
        label=_("I would not share ideas with my parents."))

    collectivism8 = models.IntegerField(
        label=_("I would help, within my means, if a relative told me that he/she is in financial difficulty."))

    collectivism9_r = models.IntegerField(
        label=_("I am not interested in knowing what my neighbors are really like."))

    collectivism10 = models.IntegerField(
        label=_("Neighbors should greet each other when we come across each other."))

    collectivism11 = models.IntegerField(
        label=_("A person ought to help a colleague at work who has financial problems."))

    independence1 = models.IntegerField(
        label=_("Admitting that your tastes are different from those of your friends."))

    independence2 = models.IntegerField(
        label=_("Arguing with a friend about an issue on which s/he has a very different opinion."))

    independence3 = models.IntegerField(
        label=_("Defending an unpopular issue that you believe in at a social occasion."))

    def storing_treatment(self):
        self.store_treatment = self.participant.vars["treatment"]
        # now store these in player class to save them to database

    def store_instructions(self):
        self.total_opened = self.participant.vars["opened_instructions"]
        # now store these in player class to save them to database

    def set_treatment(self):
        if self.round_number == 1:
            if not self.session.vars["combinations"]:  # empty list returns False
                self.participant.vars["quota_full"] = True
            else:
                self.participant.vars["quota_full"] = False
                self.participant.vars["treatment"] = random.choice(self.session.vars["combinations"])

    def participant_started(self):  # to assign not yet
        if self.round_number == 1:
            self.session.vars["telling"][self.participant.vars["treatment"]][1].append(self.id_in_group)
        print(self.session.vars["telling"])

    def store_homeowner(self):  # to assign treatment
        if not self.homeowner:
            self.participant.vars["target_group"] = False
            if not self.participant.vars["demo"]:
                self.session.vars["telling"][self.participant.vars["treatment"]][0].append(self.id_in_group)
        else:
            self.participant.vars["target_group"] = True
            if not self.participant.vars["demo"]:
                self.session.vars["telling"][self.participant.vars["treatment"]][1].append(self.id_in_group)
        if not self.participant.vars["demo"]:
            self.session.vars["telling"]["not yet"][1].remove(self.id_in_group)

    def store_consent(self):
        if not self.consent:
            self.participant.vars["target_group"] = False

    def store_complete(self):
        self.participant.vars["completed"] = True
        if not self.session.config['demo']:
            self.session.vars["telling"][self.participant.vars["treatment"]][2].append(self.id_in_group)
            if self.participant.vars["treatment"] == "baseline" and \
                    "baseline" in self.session.vars["combinations"]:
                # and \
                # len(self.session.vars["telling"]["baseline"][2]) == \
                # self.session.config['quota_baseline']:
                self.session.vars["combinations"].remove('baseline')
            # elif self.participant.vars["treatment"] == "norm_all" and \
            #         len(self.session.vars["telling"]["norm_all"][2]) == \
            #         self.session.config['quota_norm_all']:
            #     self.session.vars["combinations"].remove('norm_all')
            # elif self.participant.vars["treatment"] == "norm_high" and \
            #         len(self.session.vars["telling"]["norm_high"][2])\
            #         == self.session.config['quota_norm_high']:
            #     self.session.vars["combinations"].remove('norm_high')
            elif self.participant.vars["treatment"] == "norm_focusing" and \
                    "norm_focusing" in self.session.vars["combinations"]:
                # and \
                #     len(self.session.vars["telling"]["norm_focusing"][2]) == \
                #     self.session.config['quota_norm_focusing']:
                self.session.vars["combinations"].remove('norm_focusing')
            elif self.participant.vars["treatment"] == "norm_focusing_1" and \
                    "norm_focusing_1" in self.session.vars["combinations"]:
                # and \
                #     len(self.session.vars["telling"]["norm_focusing_1"][2]) == \
                #     self.session.config['quota_norm_focusing_1']
                self.session.vars["combinations"].remove('norm_focusing_1')
            elif self.participant.vars["treatment"] == "baseline_1" and \
                    "baseline_1" in self.session.vars["combinations"]:
                # and \
                # len(self.session.vars["telling"]["baseline_1"][2]) == \
                # self.session.config['quota_baseline_1']\
                self.session.vars["combinations"].remove('baseline_1')
        # print(self.session.vars["combinations"], " are the combinations")
        # print(self.session.vars["telling"], " is the telling")

    def store_follow_up(self):
        if self.damaged == 1:
            self.participant.vars["damaged_amount_needed"] = True
        if self.house_type == 2:
            self.participant.vars["floor_size_needed"] = False
        if self.neighbors_measures == 1:
            self.participant.vars["neighbors_needed"] = True
        if self.measures:
            self.participant.vars["responsible_needed"] = self.measures
        if self.other_text:
            self.participant.vars["other_text"] = self.other_text

    def get_questions_method(self):
        questions = [
            {
                'question': '¿Cuál fue la probabilidad de una inundación durante el escenario de prueba?',
                'options': ["1% por año",
                            "2% por año",
                            "5% por año",
                            "10% por año",
                            "21% por año",
                            "22% por año"],
                'correct': "1% por año",
                'hint': "Respuesta incorrecta. Por favor inténtelo de nuevo."
            },              {
                    'question': "¿Qué sucederá si su casa se inunda y usted no ha "
                                "invertido en medidas para reducir el daño?",
                    'options': ['Tendré que pagar el daño total: ' + str(Constants.damage),
                                'Tengo que pagar un precio pequeño',
                                'El gobierno me compensará'
                                ],
                    'correct': 'Tendré que pagar el daño total: ' + str(Constants.damage),
                    'hint': "Respuesta incorrecta. Por favor inténtelo de nuevo."

                }


        ]

        return questions

    def vars_for_scenarios(self):
        participant = self.participant
        return_vars = {'opened': self.opened,
                       'mitigate': self.mitigate, 'mitigated_before': participant.vars["mitigated_before"],
                       'mitigated_this_scenario': participant.vars["mitigated_this_scenario"],
                       'reduced_damage_this_scenario': participant.vars["reduced_damage_this_scenario"],
                       'homeowner': self.homeowner,
                       'treatment': participant.vars["treatment"]
                       }
        if self.scenario_nr == '0' or self.scenario_nr == 0:
            scenario_type = _('test scenario')
            return_vars.update({'scenario_type': scenario_type})
        elif self.scenario_nr == '1' or self.scenario_nr == 1:
            scenario_type = _('final scenario')
            return_vars.update({'scenario_type': scenario_type})
        else:
            return_vars.update({'scenario_type': ''})
        return return_vars

    def vars_for_invest(self):
        participant = self.participant
        return {'treatment': participant.vars["treatment"],
                'mitigation_cost0': participant.vars["mitigation_cost"][0],
                'mitigation_cost1': participant.vars["mitigation_cost"][1],
                'mitigation_cost2': participant.vars["mitigation_cost"][2],
                'mitigation_cost3': participant.vars["mitigation_cost"][3],
                'mitigation_cost4': participant.vars["mitigation_cost"][4],
                'mitigation_cost_this_scenario': participant.vars["mitigation_cost_this_scenario"],
                'reduced_damage0': participant.vars["reduced_damage"][0],
                'reduced_damage1': participant.vars["reduced_damage"][1],
                'reduced_damage2': participant.vars["reduced_damage"][2],
                'reduced_damage3': participant.vars["reduced_damage"][3],
                'reduced_damage4': participant.vars["reduced_damage"][4],
                'reduced_damage_this_scenario': participant.vars["reduced_damage_this_scenario"],
                }

    def vars_for_payment(self):
        participant = self.participant
        payoff1 = max(c(participant.vars["payoff_scenario1"]).to_real_world_currency(self.session),
                      c(0).to_real_world_currency(self.session))
        payoff_small_1 = payoff1*0.01

        return {'payoff_small': payoff_small_1, 'payoff': payoff1,
                'payoff_scenario1': participant.vars["payoff_scenario1"],
                'participation_fee': self.session.config['participation_fee'],
                'selected': self.selected,
                }

    def vars_for_payment_prize(self):
        participant = self.participant
        # max to make sure participants do not get a negative payment
        payoff1 = max(c(participant.vars["payoff_scenario1"]).to_real_world_currency(self.session),
                      c(0).to_real_world_currency(self.session))
        payoff_if_selected = payoff1
        self.bigprize = payoff_if_selected
        self.total_payoff = participant.vars["payoff_small"] \
            + self.session.config["participation_fee"] + participant.vars["payoff_additional"]
        payoff_small = participant.vars["payoff_small"]

        return {'participation_fee': self.session.config['participation_fee'],
                'selected_pref': self.participant.vars["selected_pref"],
                'payoff1': str(payoff1) + " now",
                'payoff_small': payoff_small,
                'selected_button': self.selected_button,
                'total_payoff': self.total_payoff,
                'payoff_if_selected': payoff_if_selected,
                'bigprize': self.bigprize,
                }

    def opened_instructions(self):
        self.participant.vars["opened_instructions"] += self.opened

    def pay_after_flood(self):
        if self.pay_damage == "paid_damage":
            self.participant.vars["cumulative_payoff"] -= self.participant.vars["reduced_damage_this_scenario"]

    def pay_mitigation_method(self):
        if 0 < self.mitigate < 999:
            self.participant.vars["mitigation_cost_this_scenario"] = self.session.vars["mitigation_cost"][self.mitigate]
            self.participant.vars["cumulative_payoff"] -= self.participant.vars["mitigation_cost_this_scenario"]
            self.participant.vars["mitigated_this_scenario"] = self.mitigate
        elif self.mitigate == 0:
            self.participant.vars["mitigation_cost_this_scenario"] = self.session.vars["mitigation_cost"][self.mitigate]
            # is zero
            self.participant.vars["mitigated_this_scenario"] = 0
        self.participant.vars["belief"] = self.belief

    def new_scenario_method(self):
        self.participant.vars["floodrisk_percent"] = self.risk
        self.participant.vars["cumulative_payoff"] = Constants.initial_endowment
        # resetting cumulative payoff to initial endowment
        self.participant.vars["mitigated_this_scenario"] = 999  # new scenario
        self.participant.vars["in_scenario"] = True
        self.participant.vars["mitigated_before"] = 0
        self.participant.vars["reduced_damage_this_scenario"] = Constants.damage

    def set_payoff(self):
        # SET MITIGATION COST AND REDUCED DAMAGE ###############
        if 0 < self.mitigate <= 4:
            self.participant.vars["reduced_damage_this_scenario"] = \
                self.participant.vars["reduced_damage"][self.mitigate]
            self.mitigation_cost = self.session.vars["mitigation_cost"][self.mitigate]
        else:
            self.mitigation_cost = 0  # initially
            self.participant.vars["reduced_damage_this_scenario"] = Constants.damage

    def set_max_payoff(self):
        if self.participant.vars["treatment"] == "baseline" or self.participant.vars["treatment"] == "baseline_1":
            self.participant.vars["max_payoff"] = (Constants.initial_endowment - 25 *
                                                   (float(Constants.risk) * 0.01 *
                                                    Constants.damage)) * self.participant.vars["conversion"]
        else:
            self.participant.vars["max_payoff"] = Constants.initial_endowment * self.participant.vars["conversion"]

    def save_payoff(self):
        self.participant.vars["payoff_scenario1"] = self.participant.vars["cumulative_payoff"]

    def save_final_payoffs(self):

        self.payoff_scenario1 = self.participant.vars["payoff_scenario1"]

        self.participant.payoff = self.payoff_scenario1*0.01
        self.participant.vars["payoff_small"] = max(self.payoff_scenario1.to_real_world_currency(self.session)*0.01,
                                                    c(0).to_real_world_currency(self.session))

    def in_scenario(self):
        if self.round_number == Constants.num_start_pages + Constants.num_test_years:
            self.scenario_nr = 0
            return True
        elif self.round_number == Constants.num_start_pages + Constants.num_test_years + Constants.num_def_years:
            self.scenario_nr = 1
            return True
        else:
            return False


