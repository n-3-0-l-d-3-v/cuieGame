import math
import random
import pygame

WIDTH, HEIGHT = 1280, 720
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)


class SentinelsGame:
    def __init__(self):
        self.targets = []
        self.score = 0
        self.miss_count = 0
        self.timer = pygame.time.get_ticks()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.math.Vector2(event.pos)
            for tgt in self.targets[:]:
                if mouse_pos.distance_to(tgt["pos"]) <= tgt["radius"]:
                    self.targets.remove(tgt)
                    self.score += 1
                    if self.score >= 10 and not getattr(self, "impossible_mode", False):
                        return True
        return False

    def update(self):
        current_time = pygame.time.get_ticks()
        impossible = getattr(self, "impossible_mode", False)

        spawn_delay = 140 if impossible else 600
        max_targets = 8 if impossible else 4

        if current_time - self.timer > spawn_delay and len(self.targets) < max_targets:
            self.timer = current_time
            pos = pygame.math.Vector2(
                random.randint(100, WIDTH - 100),
                random.randint(100, HEIGHT - 160),
            )
            rad = max(16, 40 - self.score * 2)
            life = random.randint(220, 420) if impossible else random.randint(1500, 2000)
            if impossible:
                vel = pygame.math.Vector2(
                    random.choice([-1, 1]) * random.randint(8, 14),
                    random.choice([-1, 1]) * random.randint(8, 14),
                )
            else:
                vel = pygame.math.Vector2(0, 0)
            self.targets.append(
                {
                    "pos": pos,
                    "radius": rad,
                    "spawn_time": current_time,
                    "life": life,
                    "vel": vel,
                }
            )

        for tgt in self.targets:
            if impossible:
                tgt["pos"] += tgt["vel"]
                if tgt["pos"].x < 40 or tgt["pos"].x > WIDTH - 40:
                    tgt["vel"].x *= -1
                if tgt["pos"].y < 40 or tgt["pos"].y > HEIGHT - 180:
                    tgt["vel"].y *= -1

        before = len(self.targets)
        self.targets = [
            tgt for tgt in self.targets if current_time - tgt["spawn_time"] < tgt["life"]
        ]
        self.miss_count += before - len(self.targets)

        return False

    def draw(self, screen, font):
        title = font.render(f"Targets Hit: {self.score} / 10", True, WHITE)
        screen.blit(title, (20, 20))

        if getattr(self, "impossible_mode", False):
            miss = font.render(f"Misses: {self.miss_count} / 35", True, (255, 170, 170))
            warn = font.render("Signal corruption detected! Targets unstable.", True, (255, 200, 80))
            screen.blit(miss, (20, 60))
            screen.blit(warn, (20, 100))

        current_time = pygame.time.get_ticks()
        for tgt in self.targets:
            life = current_time - tgt["spawn_time"]
            color = (255, 50, 50) if life < (tgt["life"] // 2) else (255, 150, 150)
            pygame.draw.circle(screen, color, (int(tgt["pos"].x), int(tgt["pos"].y)), tgt["radius"])
            pygame.draw.circle(screen, WHITE, (int(tgt["pos"].x), int(tgt["pos"].y)), tgt["radius"], 2)


class MediaGame:
    def __init__(self):
        self.bar_x = 100
        self.direction = 1
        self.speed = 10
        self.score = 0
        self.target_zone = (WIDTH // 2 - 100, WIDTH // 2 + 100)
        self.message = ""
        self.msg_timer = 0
        self.miss_count = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            in_zone = self.target_zone[0] <= self.bar_x <= self.target_zone[1]
            if in_zone and not getattr(self, "impossible_mode", False):
                self.score += 1
                self.speed += 3
                self.message = "PERFECT!"
                new_width = max(20, (self.target_zone[1] - self.target_zone[0]) - 20)
                center = WIDTH // 2
                self.target_zone = (center - new_width // 2, center + new_width // 2)
                if self.score >= 5:
                    return True
            else:
                self.message = "MISS!"
                self.miss_count += 1
            self.msg_timer = pygame.time.get_ticks()
        return False

    def update(self):
        impossible = getattr(self, "impossible_mode", False)

        move_speed = self.speed * (2.2 if impossible else 1)
        self.bar_x += move_speed * self.direction
        if self.bar_x > WIDTH - 100 or self.bar_x < 100:
            self.direction *= -1

        if impossible:
            zone_width = 45
            center = (self.target_zone[0] + self.target_zone[1]) // 2
            center += random.choice([-1, 1]) * random.randint(18, 34)
            center = max(170, min(center, WIDTH - 170))
            self.target_zone = (center - zone_width // 2, center + zone_width // 2)

    def draw(self, screen, font):
        title = font.render(f"The Perfect Shot: {self.score}/5", True, WHITE)
        screen.blit(title, (20, 20))

        if getattr(self, "impossible_mode", False):
            miss = font.render(f"Misses: {self.miss_count} / 35", True, (255, 170, 170))
            screen.blit(miss, (20, 60))

        inst = font.render("Press SPACE when the yellow bar is in the Green Zone!", True, (200, 200, 200))
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 100))

        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (self.target_zone[0], HEIGHT // 2 - 50, self.target_zone[1] - self.target_zone[0], 100),
        )
        pygame.draw.rect(screen, (255, 255, 0), (int(self.bar_x), HEIGHT // 2 - 60, 10, 120))

        if pygame.time.get_ticks() - self.msg_timer < 500:
            msg = font.render(self.message, True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 + 100))


class FinanceGame:
    # Budget Balancer
    def __init__(self):
        self.score = 0
        self.max_score = 300
        self.slider_x = WIDTH // 2
        self.target_center = WIDTH // 2
        self.time_offset = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.slider_x = max(100, min(event.pos[0], WIDTH - 100))
        return False

    def update(self):
        self.time_offset += 0.03
        offset = math.sin(self.time_offset) * 200 + math.sin(self.time_offset * 0.43) * 150
        self.target_center = WIDTH // 2 + offset
        self.target_center = max(150, min(self.target_center, WIDTH - 150))

        if abs(self.slider_x - self.target_center) < 75:
            self.score += 1
            if self.score >= self.max_score:
                return True
        else:
            self.score = max(0, self.score - 1)

        return False

    def draw(self, screen, font):
        title = font.render(f"The Budget Balancer: {int(self.score / self.max_score * 100)}%", True, WHITE)
        screen.blit(title, (20, 20))

        inst = font.render("Move your mouse to track the shifting Green budget zone with your needle!", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 100))

        pygame.draw.rect(screen, (50, 50, 50), (100, HEIGHT // 2 - 20, WIDTH - 200, 40))
        pygame.draw.rect(screen, GREEN, (self.target_center - 75, HEIGHT // 2 - 20, 150, 40))
        pygame.draw.rect(screen, (255, 100, 0), (int(self.slider_x) - 5, HEIGHT // 2 - 40, 10, 80))


class LogisticsGame:
    # Gear Stack dropping blocks
    def __init__(self):
        self.player_x = WIDTH // 2
        self.speed = 15
        self.items = []
        self.score = 0
        self.miss_count = 0
        self.timer = pygame.time.get_ticks()

    def handle_event(self, event):
        return False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.player_x += self.speed
        self.player_x = max(50, min(self.player_x, WIDTH - 50))

        impossible = getattr(self, "impossible_mode", False)
        spawn_gap = 150 if impossible else max(250, 1000 - (self.score * 30))
        min_fall, max_fall = (13, 22) if impossible else (5, 10)

        current_time = pygame.time.get_ticks()
        if current_time - self.timer > spawn_gap:
            self.items.append({"x": random.randint(100, WIDTH - 100), "y": 0, "s": random.randint(min_fall, max_fall)})
            self.timer = current_time

        for item in self.items[:]:
            if impossible and abs(item["x"] - self.player_x) < 100 and HEIGHT - 180 <= item["y"] <= HEIGHT - 40:
                if item["x"] <= self.player_x:
                    item["x"] -= 18
                else:
                    item["x"] += 18
                item["x"] = max(40, min(item["x"], WIDTH - 40))

            item["y"] += item["s"]

            if HEIGHT - 100 <= item["y"] + 40 <= HEIGHT - 60 and self.player_x - 60 <= item["x"] <= self.player_x + 60:
                self.score += 1
                self.items.remove(item)
                if self.score >= 15 and not impossible:
                    return True
            elif item["y"] > HEIGHT:
                self.items.remove(item)
                self.miss_count += 1

        return False

    def draw(self, screen, font):
        title = font.render(f"The Gear Stack (Catch): {self.score}/15", True, WHITE)
        screen.blit(title, (20, 20))

        if getattr(self, "impossible_mode", False):
            miss = font.render(f"Misses: {self.miss_count} / 35", True, (255, 170, 170))
            warn = font.render("Items are glitched and dodging your cart!", True, (255, 200, 80))
            screen.blit(miss, (20, 60))
            screen.blit(warn, (20, 100))

        inst = font.render("Use LEFT/RIGHT arrows to catch dropped gear in your cart!", True, WHITE)
        screen.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 100))

        pygame.draw.rect(screen, BLUE, (self.player_x - 50, HEIGHT - 100, 100, 40))

        for item in self.items:
            pygame.draw.rect(screen, (200, 150, 50), (item["x"] - 20, item["y"], 40, 40))


class DocumentationGame:
    # Memory card match
    def __init__(self):
        self.grid = []
        colors = [RED, BLUE, GREEN, (255, 255, 0), (255, 0, 255), (0, 255, 255)] * 2
        random.shuffle(colors)

        for i in range(12):
            col = i % 4
            row = i // 4
            x = WIDTH // 2 - 250 + (col * 120)
            y = 200 + (row * 150)
            self.grid.append({"rect": pygame.Rect(x, y, 100, 130), "color": colors[i], "open": False, "matched": False})

        self.selection = []
        self.wait_time = 0
        self.matched_pairs = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.wait_time > 0 and pygame.time.get_ticks() < self.wait_time:
                return False

            if self.wait_time > 0:
                for idx in self.selection:
                    self.grid[idx]["open"] = False
                self.selection = []
                self.wait_time = 0

            mouse_pos = event.pos
            for i, card in enumerate(self.grid):
                if card["rect"].collidepoint(mouse_pos) and not card["open"] and not card["matched"]:
                    card["open"] = True
                    self.selection.append(i)

                    if len(self.selection) == 2:
                        if self.grid[self.selection[0]]["color"] == self.grid[self.selection[1]]["color"]:
                            self.grid[self.selection[0]]["matched"] = True
                            self.grid[self.selection[1]]["matched"] = True
                            self.matched_pairs += 1
                            self.selection = []
                            if self.matched_pairs == 6:
                                return True
                        else:
                            self.wait_time = pygame.time.get_ticks() + 1000
        return False

    def update(self):
        return False

    def draw(self, screen, font):
        title = font.render(f"Archive Match: Pairs {self.matched_pairs}/6", True, WHITE)
        screen.blit(title, (20, 20))

        if self.wait_time > 0 and pygame.time.get_ticks() >= self.wait_time:
            for idx in self.selection:
                self.grid[idx]["open"] = False
            self.selection = []
            self.wait_time = 0

        for card in self.grid:
            pygame.draw.rect(screen, WHITE, card["rect"], 3)
            if card["open"] or card["matched"]:
                pygame.draw.rect(screen, card["color"], card["rect"].inflate(-6, -6))
            else:
                pygame.draw.rect(screen, (50, 50, 50), card["rect"].inflate(-6, -6))


class CableNode:
    def __init__(self, shape_type):
        if shape_type == "L":
            self.base = [True, False, True, False]
        elif shape_type == "C":
            self.base = [True, True, False, False]
        elif shape_type == "T":
            self.base = [True, True, False, True]
        else:
            self.base = [False, False, False, False]

        self.rot = random.randint(0, 3)

    def get_ports(self):
        return self.base[-self.rot:] + self.base[:-self.rot]


class DevOpsGame:
    # Rotate cables to connect the network puzzle
    def __init__(self):
        self.grid = []
        layout = [["C", "L", "C", "C"], ["C", "T", "C", "L"], ["L", "C", "L", "C"]]

        for x in range(4):
            col = []
            for y in range(3):
                col.append(CableNode(layout[y][x]))
            self.grid.append(col)

        self.powered = set()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            for x in range(4):
                for y in range(3):
                    rect = pygame.Rect(400 + x * 120, 180 + y * 120, 120, 120)
                    if rect.collidepoint((mouse_x, mouse_y)):
                        self.grid[x][y].rot = (self.grid[x][y].rot + 1) % 4
        return False

    def update(self):
        self.powered = set()
        stack = [(0, 1)]

        if not self.grid[0][1].get_ports()[3]:
            return False

        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in self.powered:
                continue

            self.powered.add((cx, cy))
            ports = self.grid[cx][cy].get_ports()

            if cx == 3 and cy == 1 and ports[1]:
                return True

            dirs = [(0, -1, 0, 2), (1, 0, 1, 3), (0, 1, 2, 0), (-1, 0, 3, 1)]
            for dx, dy, my_port, their_port in dirs:
                if ports[my_port]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < 4 and 0 <= ny < 3:
                        if self.grid[nx][ny].get_ports()[their_port]:
                            stack.append((nx, ny))
        return False

    def draw(self, screen, font):
        title = font.render("The Signal Path - Rotate cables to connect START to EXIT!", True, WHITE)
        screen.blit(title, (20, 20))

        start_t = font.render("START ->", True, GREEN)
        screen.blit(start_t, (250, 180 + 120 + 40))

        exit_t = font.render("-> EXIT", True, WHITE)
        screen.blit(exit_t, (400 + 4 * 120 + 20, 180 + 120 + 40))

        for x in range(4):
            for y in range(3):
                rect = pygame.Rect(400 + x * 120, 180 + y * 120, 120, 120)
                is_powered = (x, y) in self.powered
                color = GREEN if is_powered else GRAY

                cx, cy = rect.center
                bw = 14
                pygame.draw.circle(screen, color, (cx, cy), bw // 2)

                ports = self.grid[x][y].get_ports()
                if ports[0]:
                    pygame.draw.rect(screen, color, (cx - bw // 2, rect.top, bw, rect.height // 2))
                if ports[1]:
                    pygame.draw.rect(screen, color, (cx, cy - bw // 2, rect.width // 2, bw))
                if ports[2]:
                    pygame.draw.rect(screen, color, (cx - bw // 2, cy, bw, rect.height // 2))
                if ports[3]:
                    pygame.draw.rect(screen, color, (rect.left, cy - bw // 2, rect.width // 2, bw))

                pygame.draw.rect(screen, (50, 50, 50), rect, 2)
