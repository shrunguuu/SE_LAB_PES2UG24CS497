import random
import pygame

GRID_SIZE = 8
TILE_SIZE = 60
GEM_COLORS = [
    (220, 50, 50),   # Red
    (50, 200, 50),   # Green
    (50, 100, 240),  # Blue
    (240, 200, 40),  # Yellow
    (180, 50, 220),  # Purple
    (240, 130, 40),  # Orange
]


class Gem:
   
    def __init__(self, color, target_row, col, is_bomb=False, bomb_direction=None):
        self.color = color
        self.target_row = target_row
        self.col = col
        self.is_bomb = is_bomb
        self.bomb_direction = bomb_direction  # "row" or "column"
        # Start higher up to animate falling down
        self.current_y = (target_row - 2) * TILE_SIZE
        self.target_y = target_row * TILE_SIZE
        self.fall_speed = 12.0

    def update(self):
        if self.current_y < self.target_y:
            self.current_y += self.fall_speed
            if self.current_y > self.target_y:
                self.current_y = self.target_y

    def is_animating(self):
        return self.current_y < self.target_y


class Board:
    """Manages animated gem grid, gravity drops, score, and game limits."""

    def __init__(self, offset_x, offset_y, target_score=500, max_moves=20):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.target_score = target_score
        self.max_moves = max_moves
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.score = 0
        self.moves_remaining = max_moves
        self.last_activity_time = pygame.time.get_ticks()
        self.hint_positions = None
        self.reset()

    def reset(self):
        """Reset board grid, score, and move limits."""
        self.score = 0
        self.moves_remaining = self.max_moves
        self.selected = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = gem.target_y  # Snap instantly on initial start
                self.grid[r][c] = gem

        self.resolve_matches()

    def is_animating(self):
        """Returns True if any gem is currently dropping down."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] and self.grid[r][c].is_animating():
                    return True
        return False

    def swap_gems(self, pos1, pos2):
        """Swap positions and target render coordinates of two gems."""
        r1, c1 = pos1
        r2, c2 = pos2

        g1, g2 = self.grid[r1][c1], self.grid[r2][c2]
        self.grid[r1][c1], self.grid[r2][c2] = g2, g1

        if self.grid[r1][c1]:
            self.grid[r1][c1].target_row = r1
            self.grid[r1][c1].target_y = r1 * TILE_SIZE
            self.grid[r1][c1].current_y = r1 * TILE_SIZE

        if self.grid[r2][c2]:
            self.grid[r2][c2].target_row = r2
            self.grid[r2][c2].target_y = r2 * TILE_SIZE
            self.grid[r2][c2].current_y = r2 * TILE_SIZE

    def is_adjacent(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1
    def find_hint_move(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                pos1 = (r, c)

                for dr, dc in [(0, 1), (1, 0)]:
                    r2 = r + dr
                    c2 = c + dc

                    if r2 >= GRID_SIZE or c2 >= GRID_SIZE:
                        continue

                    pos2 = (r2, c2)

                    self.swap_gems(pos1, pos2)
                    matches = self.find_matches()
                    self.swap_gems(pos1, pos2)

                    if matches:
                        return (pos1, pos2)

        return None

    def find_matches(self):
        matched = set()
        self.bomb_matches = []

        for r in range(GRID_SIZE):
            c = 0
            while c < GRID_SIZE:
                if self.grid[r][c] is None:
                    c += 1
                    continue

                color = self.grid[r][c].color
                start = c

                while c < GRID_SIZE and self.grid[r][c] is not None and self.grid[r][c].color == color:
                    c += 1

                length = c - start

                if length >= 3:
                    for col in range(start, c):
                        matched.add((r, col))

                if length >= 4:
                    bomb_col = start + length // 2
                    self.bomb_matches.append((r, bomb_col, "row"))

        for c in range(GRID_SIZE):
            r = 0
            while r < GRID_SIZE:
                if self.grid[r][c] is None:
                    r += 1
                    continue

                color = self.grid[r][c].color
                start = r

                while r < GRID_SIZE and self.grid[r][c] is not None and self.grid[r][c].color == color:
                    r += 1

                length = r - start

                if length >= 3:
                    for row in range(start, r):
                        matched.add((row, c))

                if length >= 4:
                    bomb_row = start + length // 2
                    self.bomb_matches.append((bomb_row, c, "column"))

        return matched

    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            empty_slots = 0

            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_slots += 1
                elif empty_slots > 0:
                    gem = self.grid[r][c]
                    gem.target_row = r + empty_slots
                    gem.target_y = (r + empty_slots) * TILE_SIZE
                    self.grid[r + empty_slots][c] = gem
                    self.grid[r][c] = None

            for r in range(empty_slots):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = -((empty_slots - r) * TILE_SIZE)
                self.grid[r][c] = gem

    def resolve_matches(self):
        cascade = 1

        while True:
            matches = self.find_matches()
            if not matches:
                break

            bomb_to_create = None
            bomb_color = None

            if self.bomb_matches:
                r, c, direction = self.bomb_matches[0]
                if self.grid[r][c]:
                    bomb_to_create = (r, c, direction)
                    bomb_color = self.grid[r][c].color

            for r, c in matches:
                if bomb_to_create and (r, c) == bomb_to_create[:2]:
                    continue
                self.grid[r][c] = None

            if bomb_to_create:
                r, c, direction = bomb_to_create
                bomb = Gem(bomb_color, r, c, True, direction)
                bomb.current_y = r * TILE_SIZE
                bomb.target_y = r * TILE_SIZE
                self.grid[r][c] = bomb

            self.score += len(matches) * 10 * cascade
            self.drop_and_refill()
            cascade += 1

    def process_swap(self, pos1, pos2):
        if not self.is_adjacent(pos1, pos2) or self.is_game_over() or self.is_animating():
            return False
        
        self.last_activity_time = pygame.time.get_ticks()
        self.hint_positions = None
        self.swap_gems(pos1, pos2)
        matches = self.find_matches()

        if not matches:
            self.swap_gems(pos1, pos2)
            return False

        self.moves_remaining -= 1
        self.resolve_matches()
        return True

    def is_game_over(self):
        return self.score >= self.target_score or self.moves_remaining <= 0

    def check_result(self):
        if self.score >= self.target_score:
            return "WIN"
        if self.moves_remaining <= 0:
            return "LOSS"
        return None

    def update(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]:
                    self.grid[r][c].update()

        current_time = pygame.time.get_ticks()

        if current_time - self.last_activity_time > 5000:
            if self.hint_positions is None:
                self.hint_positions = self.find_hint_move()
    def render(self, surface):
        board_rect = pygame.Rect(
            self.offset_x, self.offset_y, GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
        )
        pygame.draw.rect(surface, (20, 22, 28), board_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 65, 75), board_rect, width=3, border_radius=8)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.grid[r][c]
                if gem:
                    x = self.offset_x + c * TILE_SIZE
                    y = self.offset_y + gem.current_y
                    tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)

                    if gem.is_bomb:
                       pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                       pygame.draw.rect(surface, (255, 215, 0), tile_rect, width=4, border_radius=10)
                       pygame.draw.circle(surface, (20, 20, 20), tile_rect.center, 10)
                    else:
                       pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                       pygame.draw.rect(
                              surface, (255, 255, 255), tile_rect, width=1, border_radius=10
                       )
                if self.hint_positions and (r, c) in self.hint_positions:
                    pulse = abs(pygame.time.get_ticks() % 1000 - 500) // 4
                    hint_rect = pygame.Rect(
                        x + 2 - pulse // 4,
                        y + 2 - pulse // 4,
                        TILE_SIZE - 4 + pulse // 2,
                        TILE_SIZE - 4 + pulse // 2
                    )
                    pygame.draw.rect(
                        surface,
                        (255, 255, 255),
                        hint_rect,
                        width=3,
                        border_radius=10
                    )

                if self.selected == (r, c):
                    sel_x = self.offset_x + c * TILE_SIZE
                    sel_y = self.offset_y + r * TILE_SIZE
                    sel_rect = pygame.Rect(sel_x + 2, sel_y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, (255, 255, 255), sel_rect, width=4, border_radius=10
                    )