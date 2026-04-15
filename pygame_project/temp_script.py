import re
with open('minigames.py', 'r', encoding='utf-8') as f:
    code = f.read()

# SentinelsGame
code = code.replace(
    'class SentinelsGame:\n    def __init__(self):\n        self.targets = []\n        self.score = 0\n        self.timer = pygame.time.get_ticks()',
    'class SentinelsGame:\n    def __init__(self):\n        self.targets = []\n        self.score = 0\n        self.miss_count = 0\n        self.timer = pygame.time.get_ticks()'
)

code = re.sub(
    r'    def update\(self\):\n        current_time = pygame.time.get_ticks\(\)\n        if current_time - self.timer > 600.*?\n        self.targets = \[tgt for tgt in self.targets.*]',
r'''    def update(self):
        current_time = pygame.time.get_ticks()
        is_impossible = getattr(self, 'impossible_mode', False)
        spawn_delay = 150 if is_impossible else 600
        
        if current_time - self.timer > spawn_delay and len(self.targets) < 4:
            self.timer = current_time
            pos = pygame.math.Vector2(random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
            rad = max(20, 40 - self.score*2)
            life = random.randint(300, 500) if is_impossible else random.randint(1500, 2000)
            self.targets.append({"pos": pos, "radius": rad, "spawn_time": current_time, "life": life})
            
        old_count = len(self.targets)
        self.targets = [tgt for tgt in self.targets if current_time - tgt["spawn_time"] < tgt["life"]]
        self.miss_count += old_count - len(self.targets)''',
    code, flags=re.DOTALL
)

# MediaGame
code = code.replace(
    'class MediaGame:\n    def __init__(self):\n        self.bar_x = 100\n        self.direction = 1\n        self.speed = 10\n        self.score = 0\n        self.target_zone = (WIDTH//2 - 100, WIDTH//2 + 100)\n        self.message = ""\n        self.msg_timer = 0',
    'class MediaGame:\n    def __init__(self):\n        self.bar_x = 100\n        self.direction = 1\n        self.speed = 10\n        self.score = 0\n        self.miss_count = 0\n        self.target_zone = (WIDTH//2 - 100, WIDTH//2 + 100)\n        self.message = ""\n        self.msg_timer = 0'
)

code = re.sub(
    r'            else:\n                self.message = "MISS!"\n            self.msg_timer = pygame.time.get_ticks\(\)',
r'''            else:
                self.message = "MISS!"
                self.miss_count += 1
            self.msg_timer = pygame.time.get_ticks()''',
    code
)

code = re.sub(
    r'    def update\(self\):\n        self.bar_x \+= self.speed \* self.direction\n        if self.bar_x > WIDTH - 100 or self.bar_x < 100:\n            self.direction \*= -1',
r'''    def update(self):
        is_impossible = getattr(self, 'impossible_mode', False)
        current_speed = self.speed * 4 if is_impossible else self.speed
        self.bar_x += current_speed * self.direction
        if self.bar_x > WIDTH - 100 or self.bar_x < 100:
            self.direction *= -1
            
        if is_impossible:
            import random
            tz_width = self.target_zone[1] - self.target_zone[0]
            center = (self.target_zone[0] + self.target_zone[1]) // 2
            center += random.randint(-40, 40)
            center = max(200, min(1280 - 200, center))
            self.target_zone = (center - tz_width//2, center + tz_width//2)
            self.miss_count += 0.05  # passive gain''',
    code
)

# LogisticsGame
code = code.replace(
    'class LogisticsGame:\n    # Gear Stack dropping blocks\n    def __init__(self):\n        self.player_x = WIDTH // 2\n        self.speed = 15\n        self.items = [] # dict of x, y, speed, color\n        self.score = 0\n        self.timer = pygame.time.get_ticks()',
    'class LogisticsGame:\n    # Gear Stack dropping blocks\n    def __init__(self):\n        self.player_x = WIDTH // 2\n        self.speed = 15\n        self.items = [] # dict of x, y, speed, color\n        self.score = 0\n        self.miss_count = 0\n        self.timer = pygame.time.get_ticks()'
)

code = re.sub(
    r'        current_time = pygame.time.get_ticks\(\)\n        if current_time - self.timer > 1000 - \(self.score \* 30\):\n            self.items.append\({"x": random.randint\(100, WIDTH-100\), "y": 0, "s": random.randint\(5, 10\)}\)\n            self.timer = current_time\n\n        for item in self.items\[:\]:\n            item\["y"\] \+= item\["s"\]\n            # Collision with player catch box\n            if HEIGHT - 100 <= item\["y"\] \+ 40 <= HEIGHT - 60 and self.player_x - 60 <= item\["x"\] <= self.player_x \+ 60:\n                self.score \+= 1\n                self.items.remove\(item\)\n                if self.score >= 15:\n                    return True  # Fixed bug: The game now actively ends here!\n            elif item\["y"\] > HEIGHT:\n                self.items.remove\(item\)',
r'''        current_time = pygame.time.get_ticks()
        is_impossible = getattr(self, 'impossible_mode', False)
        
        spawn_rate = 150 if is_impossible else 1000 - (self.score * 30)
        if current_time - self.timer > spawn_rate:
            import random
            speed = random.randint(15, 25) if is_impossible else random.randint(5, 10)
            self.items.append({"x": random.randint(100, 1280-100), "y": 0, "s": speed})
            self.timer = current_time

        for item in self.items[:]:
            item["y"] += item["s"]
            
            if is_impossible:
                if abs(item["x"] - self.player_x) < 80:
                    sign = 1 if item["x"] > self.player_x else -1
                    item["x"] += 10 * sign
            
            # Collision with player catch box
            if 720 - 100 <= item["y"] + 40 <= 720 - 60 and self.player_x - 60 <= item["x"] <= self.player_x + 60:
                self.score += 1
                self.items.remove(item)
                if self.score >= 15:
                    return True  # Fixed bug: The game now actively ends here!
            elif item["y"] > 720:
                self.items.remove(item)
                self.miss_count += 1''',
    code
)

with open('minigames.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated minigames.py successfully')
