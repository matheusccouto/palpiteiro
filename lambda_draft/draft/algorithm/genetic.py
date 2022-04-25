"""Genetic algorithm."""

from typing import List, Sequence
import random

from . import BaseAlgorithm, DraftError
from .. import Player, Scheme, LineUp


class Genetic(BaseAlgorithm):
    """Genetic algorithm."""

    # pylint: disable=too-few-public-methods

    def __init__(
        self,
        players: List[Player],
        n_generations: int = 350,
        n_individuals: int = 150,
        n_elite: int = 10,
        crossover_proba: float = 0.5,
        mutation_proba: float = 0.5,
        max_n_mutations: int = 3,
    ):
        # pylint: disable=too-many-arguments
        super().__init__(players)
        self.n_generations = n_generations
        self.n_individuals = n_individuals
        self.n_elite = n_elite
        self.crossover_proba = crossover_proba
        self.mutation_proba = mutation_proba
        self.n_mutations = max_n_mutations
        self.history: List[float] = []

    @staticmethod
    def _create(players: List[Player], scheme: Scheme) -> LineUp:
        """Create a random line up."""
        line_up = LineUp(scheme=scheme, players=[], bench=[])
        random.shuffle(players)
        for player in players:

            if line_up.missing[player.position]:
                line_up.add_player(player)

            if line_up.is_valid():
                line_up.players.sort(key=lambda x: x.position)
                return line_up

        raise DraftError("There are not enough players to form a line-up.")

    @staticmethod
    def _fitness(line_up: LineUp, max_price: float, max_players_per_club: int) -> float:
        """Calculate fitness metric. The greater the better"""
        if line_up.price > max_price:
            return max_price - line_up.price
        if line_up.max_players_per_club > max_players_per_club:
            return max_players_per_club - line_up.max_players_per_club
        return line_up.points

    def _rank(
        self,
        line_ups: Sequence[LineUp],
        max_price: float,
        max_players_per_club: int,
    ) -> Sequence[LineUp]:
        """Rank line ups based on the fitness."""
        return sorted(
            line_ups,
            key=lambda line_up: self._fitness(
                line_up=line_up,
                max_price=max_price,
                max_players_per_club=max_players_per_club,
            ),
            reverse=True,
        )

    @staticmethod
    def _crossover(line_up1: LineUp, line_up2: LineUp):
        """Crossover two teams."""
        for player1, player2 in zip(line_up1.players, line_up2.players):
            if random.random() > 0.5:
                if player1 not in line_up2.players and player2 not in line_up1.players:
                    line_up1.remove_player(player1)
                    line_up2.add_player(player1)
                    line_up2.remove_player(player2)
                    line_up1.add_player(player2)

    def _mutate(self, line_up: LineUp):
        """Change a random player from the line up."""
        to_remove = random.choice(line_up.players)
        players_available = self.players_per_position[to_remove.position]
        new_player = random.choice(players_available)

        if new_player in line_up:
            self._mutate(line_up)
        else:
            line_up.remove_player(to_remove)
            line_up.add_player(new_player)

    def _offsprings(self, line_ups: Sequence[LineUp]):
        """Create offsprings."""
        line_ups = line_ups[: self.n_elite]

        offsprings: List[LineUp] = []
        while len(offsprings) < self.n_individuals:
            line_up1 = random.choice(line_ups).copy()
            line_up2 = random.choice(line_ups).copy()

            if random.random() > self.crossover_proba:
                self._crossover(line_up1, line_up2)

            if random.random() > self.mutation_proba:
                for _ in range(self.n_mutations):
                    self._mutate(line_up1)
                    self._mutate(line_up2)

            offsprings.append(line_up1)
            offsprings.append(line_up2)

        return offsprings[: self.n_individuals]

    def draft(self, price: float, scheme: Scheme, max_players_per_club: int) -> LineUp:
        """Draft players following an specified scheme."""
        line_ups = [
            self._create(self.players, scheme) for _ in range(self.n_individuals)
        ]

        for gen in range(self.n_generations):

            ranked_line_ups = self._rank(
                line_ups,
                max_price=price,
                max_players_per_club=max_players_per_club,
            )
            self.history.append(ranked_line_ups[0].points)

            best = ranked_line_ups[0]
            if gen == self.n_generations - 1:
                best.bench = self._draft_bench(best)
                return best

            line_ups = self._offsprings(ranked_line_ups)
            line_ups[0] = best

        raise DraftError("Reached end of iterations without exiting.")
