import re
import os

with open('main.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Handle imports correctly
code = code.replace("import cv2", """try:
    import cv2
    from ffpyplayer.player import MediaPlayer
    CAN_PLAY_VIDEO = True
except ImportError:
    CAN_PLAY_VIDEO = False""")

# 2. Fix video logic conditional
code = code.replace('if os.path.exists("images/booting_animation.webm"):', 'if CAN_PLAY_VIDEO and os.path.exists("images/booting_animation.webm"):')

# 3. Handle `fade_out_and_quit` to be async
old_fade = '''def fade_out_and_quit(surface):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(30)
    pygame.quit()
    sys.exit()'''

new_fade = '''async def fade_out_and_quit(surface):
    global running
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade.set_alpha(alpha)
        surface.blit(fade, (0, 0))
        pygame.display.flip()
        await asyncio.sleep(0.03)
    running = False'''

code = code.replace(old_fade, new_fade)
code = code.replace('fade_out_and_quit(screen)', 'await fade_out_and_quit(screen)')

# 4. Wrap game loop inside async def main():
start_idx = code.find('running = True')
if start_idx != -1:
    pre_code = code[:start_idx]
    main_code = code[start_idx:]
    
    # Strip existing sys.exit and quit
    main_code = main_code.replace('pygame.quit()\n', '')
    main_code = main_code.replace('sys.exit()\n', '')
    
    # Needs to be indented + globals if needed
    lines = main_code.split(r'\n') # wait I must split by real newline
    
    # Actually just split correctly
    lines = main_code.split('\n')
    indented_lines = ['    ' + line if line.strip() else line for line in lines]
    indented_main = '\n'.join(indented_lines)
    
    indented_main = indented_main.replace('    clock.tick(FPS)', '    await asyncio.sleep(0)\n        clock.tick(FPS)')
    
    final_code = pre_code + '''
async def main():
    global current_state, active_minigame, active_minigame_name, active_minigame_start_time
    global credit_index, recruited_vertical, running, video_playing

''' + indented_main + '''
    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())
'''
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(final_code)
    print("Patched main.py successfully.")
else:
    print("Could not find start point.")
