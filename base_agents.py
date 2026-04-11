# -*- coding: utf-8 -*-
from negmas import ResponseType
from scml.oneshot import *
from scml.utils import anac2024_oneshot

from scml_agents import get_agents

#tournament
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

#BaseAgent
class SimpleAgent(OneShotAgent):
    """A greedy agent based on OneShotAgent"""

    def propose(self, negotiator_id: str, state) -> "Outcome":
        return self.best_offer(negotiator_id)

    def respond(self, negotiator_id, state, source=""):
        offer = state.current_offer
        my_needs = self._needed(negotiator_id)
        if my_needs <= 0:
            return ResponseType.END_NEGOTIATION
        return (
            ResponseType.ACCEPT_OFFER
            if offer[QUANTITY] <= my_needs
            else ResponseType.REJECT_OFFER
        )

    def best_offer(self, negotiator_id):
        my_needs = self._needed(negotiator_id)
        if my_needs <= 0:
            return None
        ami = self.get_nmi(negotiator_id)
        if not ami:
            return None
        quantity_issue = ami.issues[QUANTITY]

        offer = [-1] * 3
        offer[QUANTITY] = max(
            min(my_needs, quantity_issue.max_value), quantity_issue.min_value
        )
        offer[TIME] = self.awi.current_step
        offer[UNIT_PRICE] = self._find_good_price(ami)
        return tuple(offer)

    def _find_good_price(self, ami):
        """Finds a good-enough price."""
        unit_price_issue = ami.issues[UNIT_PRICE]
        if self._is_selling(ami):
            return unit_price_issue.max_value
        return unit_price_issue.min_value

    def is_seller(self, negotiator_id):
        return negotiator_id in self.awi.current_negotiation_details["sell"].keys()

    def _needed(self, negotiator_id=None):
        return (
            self.awi.needed_sales
            if self.is_seller(negotiator_id)
            else self.awi.needed_supplies
        )

    def _is_selling(self, ami):
        return ami.annotation["product"] == self.awi.my_output_product


class BetterAgent(SimpleAgent):
    """A greedy agent based on OneShotAgent with more sane strategy"""

    def __init__(self, *args, concession_exponent=0.2, **kwargs):
        super().__init__(*args, **kwargs)
        self._e = concession_exponent

    def respond(self, negotiator_id, state, source=""):
        offer = state.current_offer
        if offer is None:
            return ResponseType.REJECT_OFFER
        response = super().respond(negotiator_id, state, source)
        if response != ResponseType.ACCEPT_OFFER:
            return response
        nmi = self.get_nmi(negotiator_id)
        return (
            response
            if self._is_good_price(nmi, state, offer[UNIT_PRICE])
            else ResponseType.REJECT_OFFER
        )

    def _is_good_price(self, nmi, state, price):
        """Checks if a given price is good enough at this stage"""
        mn, mx = self._price_range(nmi)
        th = self._th(state.step, nmi.n_steps)
        # a good price is one better than the threshold
        if self._is_selling(nmi):
            return (price - mn) >= th * (mx - mn)
        else:
            return (mx - price) >= th * (mx - mn)

    def _find_good_price(self, nmi):
        """Finds a good-enough price conceding linearly over time"""
        state = nmi.state
        mn, mx = self._price_range(nmi)
        th = self._th(state.step, nmi.n_steps)
        # offer a price that is around th of your best possible price
        if self._is_selling(nmi):
            return int(mn + th * (mx - mn))
        else:
            return int(mx - th * (mx - mn))

    def _price_range(self, nmi):
        """Finds the minimum and maximum prices"""
        mn = nmi.issues[UNIT_PRICE].min_value
        mx = nmi.issues[UNIT_PRICE].max_value
        return mn, mx

    def _th(self, step, n_steps):
        """calculates a descending threshold (0 <= th <= 1)"""
        return ((n_steps - step - 1) / (n_steps - 1)) ** self._e

    


#tournament
pd.options.display.float_format = '{:,.2f}'.format

def shorten_names(results):
    # just make agent types more readable
    results.score_stats.agent_type = results.score_stats.agent_type.str.split(".").str[-1]
    results.kstest.a = results.kstest.a.str.split(".").str[-1]
    results.kstest.b = results.kstest.b.str.split(".").str[-1]
    results.total_scores.agent_type = results.total_scores.agent_type.str.split(".").str[-1]
    results.scores.agent_type = results.scores.agent_type.str.split(".").str[-1]
    results.winners = [_.split(".")[-1] for _ in results.winners]
    return results

# 昨年の優勝エージェントを取得
# 他の年のエージェントを入れる場合はversionを変更
winners_2025 = get_agents(version=2025, track="oneshot", winners_only=True, as_class=True)

tournament_types = [SimpleAgent, BetterAgent] + list(winners_2025) #自分のエージェントクラスをここに追加して実行
    # may take a long time
if __name__ == '__main__':
    results = anac2024_oneshot(
        competitors=tournament_types,
        n_configs=1, # number of different configurations to generate
        n_competitors_per_world=len(tournament_types),
        n_runs_per_world=5, # number of times to repeat every simulation (with agent assignment)
        n_steps=10, # number of days (simulation steps) per simulation 本番は50, 125, 200
        print_exceptions=True,
        verbose = True,
    )

    results = shorten_names(results)

    print(len(results.scores.run_id.unique()))

    print(results.score_stats)

    results.scores["level"] = results.scores.agent_name.str.split("@", expand=True).loc[:, 1]
    results.scores = results.scores.sort_values("level")
    sns.lineplot(data=results.scores[["agent_type", "level", "score"]],
                x="level", y="score", hue="agent_type")
    plt.plot([0.0] * len(results.scores["level"].unique()), "b--")
    plt.show()
    