# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os
from flectra import models, fields

DEFAULT_THEME_CONFIG_PATH = 'static/src/scss/backend_theme_customizer'
THEME_CONFIG = '''$theme-brand-primary: {theme_color_brand};
$theme-brand-background-color: {theme_background_color};
$theme-root-font-family: {theme_font_name};
$theme-sidebar-color: {theme_sidebar_color};
'''


class ResCompany(models.Model):

    _inherit = 'res.company'

    theme_menu_style = fields.Selection([
        ('sidemenu', 'Side Menu'),
        ('apps', 'Top Menu')], string="Menu Style", default="sidemenu")
    theme_font_name = fields.Selection([
        ('Rubik', 'Rubik'),
        ('sans-serif', 'sans-serif')], string="Select Font", default='Rubik')
    theme_color_brand = fields.Char("Theme Brand Color", default="#009efb")
    theme_background_color = fields.Char("Theme Background Color", default="#f2f7fb")
    theme_sidebar_color = fields.Char("Theme Sidebar Color", default="#212529")
    dashboard_background = fields.Binary(attachment=True)

    def update_theme_color(self):
        modulePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assetPath = os.path.join(modulePath, DEFAULT_THEME_CONFIG_PATH, 'variables.scss')
        F = open(assetPath, 'w')
        theme = THEME_CONFIG.format(
            theme_color_brand=self.theme_color_brand or '#009efb',
            theme_background_color=self.theme_background_color or '#f2f7fb',
            theme_font_name=self.theme_font_name or 'Rubik',
            theme_sidebar_color=self.theme_sidebar_color or '#212529',)
        F.write(theme)
        F.close()
