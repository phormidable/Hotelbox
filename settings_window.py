# settings_window.py
import pygame
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UIDropDownMenu, UILabel
import config


class SettingsWindow:
    def __init__(self, manager):
        self.window = UIWindow(
            rect=pygame.Rect((100, 80), (400, 480)),
            window_display_title="Game Settings",
            manager=manager
        )

        y_offset = 15

        # Helper rects to keep code clean
        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))

        # Player 1 Name
        UILabel(relative_rect=label_rect, text="Player 1 Name:", manager=manager, container=self.window)
        self.p1_name = UITextEntryLine(relative_rect=input_rect, manager=manager, container=self.window)
        self.p1_name.set_text(config.PLAYER_NAMES[1])
        y_offset += 45

        # Player 2 Name
        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Player 2 Name:", manager=manager, container=self.window)
        self.p2_name = UITextEntryLine(relative_rect=input_rect, manager=manager, container=self.window)
        self.p2_name.set_text(config.PLAYER_NAMES[2])
        y_offset += 45

        # Grid Size X
        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Grid Width (X):", manager=manager, container=self.window)
        self.grid_x = UITextEntryLine(relative_rect=input_rect, manager=manager, container=self.window)
        self.grid_x.set_text(str(config.GRID_X))
        y_offset += 45

        # Grid Size Y
        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Grid Height (Y):", manager=manager, container=self.window)
        self.grid_y = UITextEntryLine(relative_rect=input_rect, manager=manager, container=self.window)
        self.grid_y.set_text(str(config.GRID_Y))
        y_offset += 45

        # Rules Dropdown
        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Rules:", manager=manager, container=self.window)

        current_rule = 'Classic (Any 4 sides)' if config.RULES == 'classic' else '4 Sides (Same color)'
        self.rules = UIDropDownMenu(
            options_list=['Classic (Any 4 sides)', '4 Sides (Same color)'],
            starting_option=current_rule,
            relative_rect=input_rect,
            manager=manager,
            container=self.window
        )
        y_offset += 45

        # Color Dropdowns
        color_options = ['Green', 'Blue', 'Red', 'Purple', 'Orange', 'Cyan']

        # Map current RGB colors back to their string names for the dropdown
        rgb_to_name = {
            (34, 139, 34): 'Green', (30, 144, 255): 'Blue', (255, 0, 0): 'Red',
            (128, 0, 128): 'Purple', (255, 165, 0): 'Orange', (0, 255, 255): 'Cyan'
        }
        p1_color_name = rgb_to_name.get(config.PLAYER_COLORS[1], 'Green')
        p2_color_name = rgb_to_name.get(config.PLAYER_COLORS[2], 'Blue')

        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Player 1 Color:", manager=manager, container=self.window)
        self.p1_color = UIDropDownMenu(
            options_list=color_options,
            starting_option=p1_color_name,
            relative_rect=input_rect,
            manager=manager, container=self.window
        )
        y_offset += 45

        label_rect = pygame.Rect((15, y_offset), (140, 30))
        input_rect = pygame.Rect((165, y_offset), (200, 30))
        UILabel(relative_rect=label_rect, text="Player 2 Color:", manager=manager, container=self.window)
        self.p2_color = UIDropDownMenu(
            options_list=color_options,
            starting_option=p2_color_name,
            relative_rect=input_rect,
            manager=manager, container=self.window
        )
        y_offset += 55

        # Accept Button
        self.accept_button = UIButton(
            relative_rect=pygame.Rect((150, y_offset), (100, 35)),
            text="Accept",
            manager=manager,
            container=self.window
        )