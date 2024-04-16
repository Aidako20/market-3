#coding:utf-8
fromflectra.testsimportcommon,tagged


@tagged('-at_install','post_install')
classTestTheme(common.TransactionCase):

    deftest_theme_remove_working(self):
        """Thistestensurethemecanberemoved.
        Themeremovalisalsothefirststepduringthemeinstallation.
        """
        theme_common_module=self.env['ir.module.module'].search([('name','=','theme_default')])
        website=self.env['website'].get_current_website()
        website.theme_id=theme_common_module.id
        self.env['ir.module.module']._theme_remove(website)

    deftest_02_disable_view(self):
        """Thistestensureonlyonetemplateheadercanbeactiveatatime."""
        website_id=self.env['website'].browse(1)
        ThemeUtils=self.env['theme.utils'].with_context(website_id=website_id.id)

        ThemeUtils._reset_default_config()

        def_get_header_template_key():
            returnself.env['ir.ui.view'].search([
                ('key','in',ThemeUtils._header_templates),
                ('website_id','=',website_id.id),
            ]).key

        self.assertEqual(_get_header_template_key(),'website.template_header_default',
                         "Onlythedefaulttemplateshouldbeactive.")

        key='website.template_header_magazine'
        ThemeUtils.enable_view(key)
        self.assertEqual(_get_header_template_key(),key,
                         "Onlyonetemplatecanbeactiveatatime.")

        key='website.template_header_hamburger'
        ThemeUtils.enable_view(key)
        self.assertEqual(_get_header_template_key(),key,
                         "Ensuringitworksalsofornondefaulttemplate.")
