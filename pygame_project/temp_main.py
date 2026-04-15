import re
with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add impossible_mode initialization
code = code.replace(
'''                            current_state = STATE_MINIGAME_ACTIVE
                            active_minigame_start_time = pygame.time.get_ticks()''',
'''                            current_state = STATE_MINIGAME_ACTIVE
                            active_minigame_start_time = pygame.time.get_ticks()
                            if globals().get('recruited_vertical') == active_minigame_name:
                                active_minigame.impossible_mode = True'''
)

# Replace timeout with miss_count
code = code.replace(
'''        # Check for recruited vertical timeout (2 seconds)
        if globals().get('recruited_vertical') == active_minigame_name:
            if pygame.time.get_ticks() - active_minigame_start_time > 2000:''',
'''        # Check for recruited vertical impossible mode threshold
        if globals().get('recruited_vertical') == active_minigame_name:
            if getattr(active_minigame, 'miss_count', 0) > 30:'''
)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Updated main.py successfully')
