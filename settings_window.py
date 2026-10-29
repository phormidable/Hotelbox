import pygame
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UIDropDownMenu, UILabel, UICheckBox
import config

class SettingsWindow:
    def __init__(self, manager, grid_x, grid_y, rules, p1_name, p2_name, p1_color_rgb, p2_color_rgb, extra_turn_on_square):
        self.manager = manager
        self.window = UIWindow(rect=pygame.Rect((100, 80), (400, 525)), window_display_title="Game Settings", manager=manager)
        y_offset = 15

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Name:", manager=manager, container=self.window)
        self.p1_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p1_name.set_text(p1_name)
        y_offset += 45

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Name:", manager=manager, container=self.window)
        self.p2_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p2_name.set_text(p2_name)
        y_offset += 45

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Width (X):", manager=manager, container=self.window)
        self.grid_x = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_x.set_text(str(grid_x))
        y_offset += 45

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Height (Y):", manager=manager, container=self.window)
        self.grid_y = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_y.set_text(str(grid_y))
        y_offset += 45

        current_rule = 'Classic (Any 4 sides)' if rules == 'classic' else '4 Sides (Same color)'
        self.rules = UIDropDownMenu(
            options_list=['Classic (Any 4 sides)', '4 Sides (Same color)'],
            starting_option=current_rule,
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager, container=self.window
        )
        y_offset += 45

        # --- Complete Square Dropdown ---
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Complete Square:", manager=manager, container=self.window)
        current_extra_turn = 'Extra turn' if extra_turn_on_square else 'No extra turn'
        self.extra_turn = UIDropDownMenu(options_list=['Extra turn', 'No extra turn'],
            starting_option=current_extra_turn,
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager, container=self.window
        )
        y_offset += 45

        self.all_colors = list(config.PLAYER_COLOR_CHOICES.keys())
        p1_color_name = config.COLOR_NAME_BY_RGB.get(p1_color_rgb, "Green")
        p2_color_name = config.COLOR_NAME_BY_RGB.get(p2_color_rgb, "Blue")

        if p1_color_name == p2_color_name:
            p2_color_name = next((c for c in self.all_colors if c != p1_color_name), "Blue")

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Color:", manager=manager, container=self.window)
        self.p1_color_rect = pygame.Rect((165, y_offset), (200, 30))
        self.p1_color = UIDropDownMenu(
            options_list=[c for c in self.all_colors if c != p2_color_name],
            starting_option=p1_color_name,
            relative_rect=self.p1_color_rect,
            manager=manager, container=self.window
        )
        y_offset += 45

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Color:", manager=manager, container=self.window)
        self.p2_color_rect = pygame.Rect((165, y_offset), (200, 30))
        self.p2_color = UIDropDownMenu(
            options_list=[c for c in self.all_colors if c != p1_color_name],
            starting_option=p2_color_name,
            relative_rect=self.p2_color_rect,
            manager=manager, container=self.window
        )
        y_offset += 55

        self.accept_button = UIButton(
            relative_rect=pygame.Rect((150, y_offset), (100, 35)),
            text="Accept",
            manager=manager,
            container=self.window
        )

    def update_color_options(self):
        p1_sel = self.p1_color.selected_option
        p2_sel = self.p2_color.selected_option

        new_p1_opts = [c for c in self.all_colors if c != p2_sel]
        new_p2_opts = [c for c in self.all_colors if c != p1_sel]

        if set(new_p1_opts) != set(self.p1_color.options_list):
            self.p1_color.kill()
            self.p1_color = UIDropDownMenu(new_p1_opts, p1_sel, self.p1_color_rect, self.manager, self.window)

        if set(new_p2_opts) != set(self.p2_color.options_list):
            self.p2_color.kill()
            self.p2_color = UIDropDownMenu(new_p2_opts, p2_sel, self.p2_color_rect, self.manager, self.window)