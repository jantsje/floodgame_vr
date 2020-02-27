from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from floodgame_norms.extra_pages import Check as UnderstandingQuestionsPage
import locale
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils import translation
from django.conf import settings


class TransMixin:
    def get_context_data(self, **context):
        user_language = self.session.config.get('language', 'en')
        translation.activate(user_language)
        if hasattr(settings, 'LANGUAGE_SESSION_KEY'):
            self.request.session[settings.LANGUAGE_SESSION_KEY] = user_language
        return super().get_context_data(**context)
        print(user_language)


class Page(TransMixin, Page):
    pass


class WaitPage(TransMixin, WaitPage):
    pass


class No(Page):

    def dispatch(self, request, *args, **kwargs):
        from otree.models import Participant
        participant = Participant.objects.get(code=kwargs.get('participant_code'))
        if request.method == 'GET':
            address = 'https://www.websiteonlinepanel.com/id=' + str(participant.label)
            # screen-out (not in target group)
            return HttpResponseRedirect(address)
        return super(Page, self).dispatch(request, *args, **kwargs)

    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1 and not self.player.participant.vars["target_group"] and not \
            self.session.vars["quota_full"]


def vars_for_all_templates(self):
    player = self.player
    participant = self.participant
    return_vars = {'progress': progress(self),
                   'cumulative_payoff': participant.vars["cumulative_payoff"],
                   'risk': player.risk, 'round': player.round_number,
                   'scenario_nr': player.scenario_nr,
                   'insurance_choice': participant.vars["insurance_choice"],
                   'language_code': self.session.config['language']
                   }
    return_vars.update(self.player.vars_for_scenarios())
    return return_vars


def progress(p):
    progress_rel = p.round_number/Constants.num_rounds*100
    return str(locale.atof(str(progress_rel)))
    # this looks really bad but it has to do with the NL language settings in Django
    # and the fact that the progressbar does not work with comma separators for decimals


class Spelpagina(Page):
    def get_form_fields(self):
        return self.form_fields + ['opened']


class ParticipantStarted(Page):
    timeout_seconds = 0.00001

    def is_displayed(self):
        return self.round_number == 1 and not self.session.vars["quota_full"]

    def before_next_page(self):
        if not self.session.config['demo']:  # in that case the treatment was chosen via the demo page
            self.player.participant_started()


class Welcome(Page):
    form_model = 'player'
    form_fields = ['opened', 'homeowner', 'zip_code_nrs', 'zip_code_letters']

    def vars_for_template(self):
        return {'participation_fee': self.session.config['participation_fee'],
                'page_title': ''}

    def is_displayed(self):
        return self.round_number == 1 and not self.session.vars["quota_full"]

    def before_next_page(self):
        self.player.browser = self.request.META.get('HTTP_USER_AGENT')
        self.player.set_max_payoff()
        if self.participant.vars["treatment"] == 'not yet':
            self.player.set_treatment()
            self.participant.vars["demo"] = False
        else:
            self.participant.vars["quota_full"] = False
            self.participant.vars["demo"] = True
        self.player.store_homeowner()
        self.player.storing_treatment()


class Consent(Page):
    form_model = 'player'
    form_fields = ['opened', 'consent']

    def is_displayed(self):
        return self.round_number == 1 and not self.session.vars["quota_full"] and \
               self.player.participant.vars["target_group"]

    def before_next_page(self):
        self.player.store_consent()


class Full(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.participant.vars["quota_full"]

    def dispatch(self, request, *args, **kwargs):
        from otree.models import Participant
        participant = Participant.objects.get(code=kwargs.get('participant_code'))
        if request.method == 'GET':
            address = 'https://www.websiteonlinepanel.com/id=' + str(participant.label)
            # quota-full link here
            return HttpResponseRedirect(address)
        return super(Page, self).dispatch(request, *args, **kwargs)


class Start(Page):
    form_model = 'player'

    def before_next_page(self):
        self.player.store_follow_up()

    def get_form_fields(self):
        if self.round_number == 1:
            return ['flood_prone', 'evacuated', 'damaged']
        elif self.round_number == 2:
            the_list = []
            if self.player.participant.vars["damaged_amount_needed"]:
                the_list.append('damaged_amount')
            the_list.append('flood_prob')
            the_list.append('water_levels')
            the_list.append('expected_damage')
            return the_list
        elif self.round_number == 3:
            return ['worry', 'concern', 'trust_dikes']
        elif self.round_number == 4:
            return ['exact_flood_risk_perception']

    def is_displayed(self):
        return self.round_number <= Constants.num_start_pages and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]


class FinalQuestions(Page):
    form_model = 'player'

    def vars_for_template(self):
        the_dict = {'measures_taken': self.participant.vars["responsible_needed"]}
        if self.participant.vars["other_text"]:
            the_dict['other_text'] = self.participant.vars["other_text"]
        return the_dict

    def before_next_page(self):
        self.player.store_follow_up()
        if self.round_number == 18:
            self.player.store_complete()

    def get_form_fields(self):
        if self.round_number == 6:
            the_list = []
            if self.participant.vars["treatment"] == 'norm_all' or self.participant.vars["treatment"] == "norm_high":
                the_list.append('trust_messenger')
            if self.player.participant.vars["flooded"] and self.player.participant.vars["mitigated_this_scenario"] < 4:
                the_list.append('regret1')
            elif not self.player.participant.vars["flooded"] and \
                    self.player.participant.vars["mitigated_this_scenario"] == 0:
                the_list.append('regret3')
            else:
                the_list.append('regret2')
            the_list.append('difficult')
            the_list.append('explain_strategy')
            return the_list
        elif self.round_number == 7:
            return['measures', 'other_text', 'neighbors_measures']
        elif self.round_number == 8:
            measures_taken = self.participant.vars["responsible_needed"]
            return_measures = []
            measures = ["cellar", "furniture", "floor_elevated", "foundation",
                        "walls", "floor_water_resistant", "sockets_raised", "valves",
                        "sandbags", "appliances_elevated", "boiler",
                        "meter_elevated", "insured", "other"]
            for measure in measures:
                if measure in measures_taken:
                    return_measures.append(measure + '_responsible')
            return return_measures
        elif self.round_number == 9:
            return ['neighbors_relation', 'other_text']
        elif self.round_number == 10:
            return['perceived_efficacy', 'perceived_cost', 'self_efficacy', 'self_responsibility', 'personal_norm']
        elif self.round_number == 11:
            return ['independence1', 'independence2', 'independence3']
        elif self.round_number == 12:
            return ['risk_qual', 'time_qual']
        elif self.round_number == 13:
            return ['collectivism1_r', 'collectivism2', 'collectivism3_r', 'collectivism4_r',
                    'collectivism5_r', 'collectivism6', 'collectivism7_r', 'collectivism8',
                    'collectivism9_r', 'collectivism10', 'collectivism11']
        elif self.round_number == 14:
            return ['sns1', 'sns2', 'sns3']
        elif self.round_number == 15:
            return ['gender', 'age', 'house_type', 'other_text']
        elif self.round_number == 16:
            return ['edu', 'other_text']
        elif self.round_number == 17:
            the_list = ['income', 'home']
            if self.player.participant.vars["floor_size_needed"]:
                the_list.append('floor_size')
            return the_list
        elif self.round_number == 18:
            return ['clicked_button', 'feedback']

    def is_displayed(self):
        if self.participant.vars["quota_full"]:
            return False
        elif self.round_number == 9 and not self.participant.vars["neighbors_needed"]:
            return False
        else:
            if not self.player.participant.vars["target_group"]:
                return False
            elif self.round_number == 8:
                if self.participant.vars["responsible_needed"]:
                    return True
                else:
                    return False
            else:
                return self.round_number >= 6


class Scenario(Page):
    form_model = 'player'

    def get_form_fields(self):
        return self.form_fields + ['opened']

    def vars_for_template(self):
        return {'max_payoff': self.participant.vars["max_payoff"]}

    def is_displayed(self):
        return self.round_number == Constants.num_start_pages and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]

    def before_next_page(self):
        self.player.new_scenario_method()


class Instructions(Page):
    form_model = 'player'

    def get_form_fields(self):
        return self.form_fields + ['opened']

    def is_displayed(self):
        return self.round_number == Constants.num_start_pages and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]


class StartScenario(Spelpagina):
    form_model = 'player'
    form_fields = ['opened']

    def before_next_page(self):
        self.player.opened_instructions()

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]

    def vars_for_template(self):
        if self.player.scenario_nr == 0:
            return{'page_title': _('Test scenario')}
        else:
            return{'page_title': _('Final scenario')}


class Check(UnderstandingQuestionsPage):
    page_title = 'Revisión'
    set_correct_answers = False  # APPS_DEBUG
    form_model = 'player'
    form_fields = ['opened']
    form_field_n_wrong_attempts = 'understanding_questions_wrong_attempts'

    def get_questions(self):
        return self.player.get_questions_method()

    def before_next_page(self):
        self.player.opened_instructions()
        self.player.new_scenario_method()

    def is_displayed(self):
        return self.round_number == Constants.num_start_pages + Constants.num_test_years and \
               self.player.participant.vars["target_group"] and not self.participant.vars["quota_full"]


class Decision(Spelpagina):
    form_model = 'player'
    form_fields = ['mitigate']

    def vars_for_template(self):
        vars_for_this_template = self.player.vars_for_invest()
        vars_for_this_template.update({'page_title': _("Investment")})
        return vars_for_this_template

    def before_next_page(self):
        self.player.set_payoff()
        self.player.pay_mitigation_method()
        self.player.opened_instructions()

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]


class BE1(Spelpagina):
    form_model = 'player'
    form_fields = ['belief']

    def vars_for_template(self):
        vars_for_this_template = self.player.vars_for_invest()
        vars_for_this_template.update({'page_title': _("Prediction")})
        return vars_for_this_template

    def before_next_page(self):
        self.player.set_payoff()
        self.player.pay_mitigation_method()
        self.player.opened_instructions()

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"] and \
            (self.participant.vars["treatment"] == 'norm_focusing' or
                self.participant.vars["treatment"] == 'norm_focusing_1') and \
            self.player.scenario_nr == 1


class BE2(Spelpagina):
    form_model = 'player'
    form_fields = ['belief']

    def vars_for_template(self):
        vars_for_this_template = self.player.vars_for_invest()
        vars_for_this_template.update({'page_title': _("Prediction")})
        return vars_for_this_template

    def before_next_page(self):
        self.player.opened_instructions()
        self.player.pay_mitigation_method()  # to save belief for Admin report

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"] and \
            (self.participant.vars["treatment"] == 'baseline' or self.participant.vars["treatment"] == 'baseline_1')\
            and self.player.scenario_nr == 1


class Floods(Spelpagina):
    form_model = 'player'
    form_fields = ['opened', 'pay_damage']

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]

    def vars_for_template(self):
        player = self.player
        the_list = {'flood_nrs': player.flood_nrs,
                    'items': models.Constants.items,
                    'items2': models.Constants.items2,
                    'page_title': _('Floods')
                    }
        return the_list

    def before_next_page(self):
        self.player.pay_after_flood()
        self.player.save_payoff()
        self.player.opened_instructions()

        if self.player.flooded:
            self.player.participant.vars["flooded"] = True
        else:
            self.player.participant.vars["flooded"] = False

        if self.player.round_number == Constants.num_start_pages + Constants.num_test_years:
            pass
        else:
            self.player.save_final_payoffs()


class Overview(Spelpagina):
    form_model = 'player'

    def vars_for_template(self):
        vars_for_this_template = self.player.vars_for_invest()
        vars_for_this_template.update({'page_title': _('Overview of the past 25 years ')})
        return vars_for_this_template

    def before_next_page(self):
        self.player.opened_instructions()

    def is_displayed(self):
        return self.player.in_scenario() and self.player.participant.vars["target_group"] and not \
            self.participant.vars["quota_full"]


class Results(Spelpagina):
    form_model = 'player'
    form_fields = ['selected']

    def before_next_page(self):
        self.player.store_instructions()

    def is_displayed(self):
        return self.round_number == Constants.num_rounds - Constants.num_end_pages and \
               self.player.participant.vars["target_group"] and not self.participant.vars["quota_full"]

    def vars_for_template(self):
        vars_for_this_template = self.player.vars_for_payment()
        vars_for_this_template.update({'page_title': ""})
        return vars_for_this_template


class Thanks(Page):
    form_model = 'player'

    def vars_for_template(self):
        return {'page_title': _('Thanks for your participation')}

    def is_displayed(self):
        return self.player.participant.vars["completed"] and self.session.config['demo']


class Complete(Page):

    def dispatch(self, request, *args, **kwargs):
        from otree.models import Participant
        participant = Participant.objects.get(code=kwargs.get('participant_code'))
        if request.method == 'GET':
            address = 'https://www.websiteonlinepanel.com/id=' + str(participant.label)
            # complete link here
            return HttpResponseRedirect(address)
        return super(Page, self).dispatch(request, *args, **kwargs)

    form_model = 'player'

    def is_displayed(self):
        return not self.session.config['demo'] and self.player.participant.vars["completed"]


page_sequence = [
    ParticipantStarted,
    Welcome,
    Consent,
    Full,
    No,
    Start,
    Scenario,
    Instructions,
    StartScenario,
    BE1,
    Decision,
    Floods,
    Overview,
    BE2,
    Check,
    Results,
    FinalQuestions,
    Thanks,
    Complete
]
