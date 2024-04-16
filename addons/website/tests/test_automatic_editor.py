fromunittest.mockimportpatch

fromflectra.testsimportHttpCase,tagged

@tagged('post_install','-at_install')
classTestAutomaticEditor(HttpCase):

    def_theme_upgrade_upstream(self):
        #Becausewecannotdo_theme_upgrade_upstream,thethemeinstallaction
        #isn'tconsumed,soitputstheuserbackontheinstallthemescreen.
        #Soactionsprioraredisabledandanactionthatwilltriggerwhat
        #needstobetestediscreated.
        actions=self.env['ir.actions.todo'].search([('state','=','open')])
        actions.write({'state':'done'})
        self.env['ir.actions.todo'].create({'action_id':self.env.ref('website.action_website_edit').id,'state':'open'})

    defsetUp(self):
        super().setUp()
        patcher=patch('flectra.addons.website.models.ir_module_module.IrModuleModule._theme_upgrade_upstream',wraps=self._theme_upgrade_upstream)
        patcher.start()
        self.addCleanup(patcher.stop)

    deftest_01_automatic_editor_on_new_website(self):
        #Wecreatealangbecauseifthenewwebsiteisdisplayedinthislang
        #insteadofthewebsite'sdefaultone,theeditorwon'tautomatically
        #start.
        self.env['res.lang'].create({
            'name':'Parseltongue',
            'code':'pa_GB',
            'iso_code':'pa_GB',
            'url_code':'pa_GB',
        })
        self.start_tour('/','automatic_editor_on_new_website',login='admin')
