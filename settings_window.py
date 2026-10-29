# settings_window.py
import pygame
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UIDropDownMenu, UILabel
import config


class SettingsWindow:
    def __init__(self, manager, grid_x, grid_y, rules, p1_name, p2_name, p1_color_rgb, p2_color_rgb):
        self.manager = manager
        self.window = UIWindow(
            rect=pygame.Rect((100, 80), (400, 480)),
            window_display_title="Game Settings",
            manager=manager
        )

        y_offset = 15

        # Player 1 Name
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Name:", manager=manager, container=self.window)
        self.p1_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p1_name.set_text(p1_name)
        y_offset += 45

        # Player 2 Name
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Name:", manager=manager, container=self.window)
        self.p2_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p2_name.set_text(p2_name)
        y_offset += 45

        # Grid Size X
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Width (X):", manager=manager, container=self.window)
        self.grid_x = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_x.set_text(str(grid_x))
        y_offset += 45

        # Grid Size Y
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Height (Y):", manager=manager, container=self.window)
        self.grid_y = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_y.set_text(str(grid_y))
        y_offset += 45

        # Rules Dropdown
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Rules:", manager=manager, container=self.window)
        current_rule = 'Classic (Any 4 sides)' if rules == 'classic' else '4 Sides (Same color)'
        self.rules = UIDropDownMenu(
            options_list=['Classic (Any 4 sides)', '4 Sides (Same color)'],
            starting_option=current_rule,
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager, container=self.window
        )
        y_offset += 45

        # Color Dropdowns
        self.all_colors = list(config.PLAYER_COLOR_CHOICES.keys())
        p1_color_name = config.COLOR_NAME_BY_RGB.get(p1_color_rgb, "Green")
        p2_color_name = config.COLOR_NAME_BY_RGB.get(p2_color_rgb, "Blue")

        if p1_color_name == p2_color_name:
            for c in self.all_colors:
                if c != p1_color_name:
                    p2_color_name = c
                    break

        # Player 1 Color
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Color:", manager=manager, container=self.window)
        self.p1_color_rect = pygame.Rect((165, y_offset), (200, 30))
        self.p1_color = UIDropDownMenu(
            options_list=[c for c in self.all_colors if c != p2_color_name],
            starting_option=p1_color_name,
            relative_rect=self.p1_color_rect,
            manager=manager, container=self.window
        )
        y_offset += 45

        # Player 2 Color
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Color:", manager=manager, container=self.window)
        self.p2_color_rect = pygame.Rect((165, y_offset), (200, 30))
        self.p2_color = UIDropDownMenu(
            options_list=[c for c in self.all_colors if c != p1_color_name],
            starting_option=p2_color_name,
            relative_rect=self.p2_color_rect,
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

    def get_dropdown_text(self, dropdown):
        opt = dropdown.selected_option
        return opt[0] if isinstance(opt, tuple) else opt

    def update_color_options(self):
        """Dynamically updates the dropdown lists by killing and recreating them."""
        p1_sel = self.get_dropdown_text(self.p1_color)
        p2_sel = self.get_dropdown_text(self.p2_color)

        new_p1_opts = [c for c in self.all_colors if c != p2_sel]
        new_p2_opts = [c for c in self.all_colors if c != p1_sel]

        if set(new_p1_opts) != set(self.p1_color.options_list):
            self.p1_color.kill()
            self.p1_color = UIDropDownMenu(
                options_list=new_p1_opts,
                starting_option=p1_sel,
                relative_rect=self.p1_color_rect,
                manager=self.manager,
                container=self.window
            )

        if set(new_p2_opts) != set(self.p2_color.options_list):
            self.p2_color.kill()
            self.p2_color = UIDropDownMenu(
                options_list=new_p2_opts,
                starting_option=p2_sel,
                relative_rect=self.p2_color_rect,
                manager=self.manager,
                container=self.window
            )