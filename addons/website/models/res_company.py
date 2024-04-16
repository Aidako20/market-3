#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromastimportliteral_eval


classCompany(models.Model):
    _inherit="res.company"

    @api.model
    defaction_open_website_theme_selector(self):
        action=self.env["ir.actions.actions"]._for_xml_id("website.theme_install_kanban_action")
        action['target']='new'
        returnaction

    defgoogle_map_img(self,zoom=8,width=298,height=298):
        partner=self.sudo().partner_id
        returnpartnerandpartner.google_map_img(zoom,width,height)orNone

    defgoogle_map_link(self,zoom=8):
        partner=self.sudo().partner_id
        returnpartnerandpartner.google_map_link(zoom)orNone

    def_compute_website_theme_onboarding_done(self):
        """Thestepismarkedasdoneifonethemeisinstalled."""
        #weneedthesamedomainastheexistingaction
        action=self.env["ir.actions.actions"]._for_xml_id("website.theme_install_kanban_action")
        domain=literal_eval(action['domain'])
        domain.append(('state','=','installed'))
        installed_themes_count=self.env['ir.module.module'].sudo().search_count(domain)
        forrecordinself:
            record.website_theme_onboarding_done=(installed_themes_count>0)

    website_theme_onboarding_done=fields.Boolean("Onboardingwebsitethemestepdone",
                                                   compute='_compute_website_theme_onboarding_done')

    def_get_public_user(self):
        self.ensure_one()
        #Weneedsudotobeabletoseepublicusersfromotherscompaniestoo
        public_users=self.env.ref('base.group_public').sudo().with_context(active_test=False).users
        public_users_for_website=public_users.filtered(lambdauser:user.company_id==self)

        ifpublic_users_for_website:
            returnpublic_users_for_website[0]
        else:
            returnself.env.ref('base.public_user').sudo().copy({
                'name':'Publicuserfor%s'%self.name,
                'login':'public-user@company-%s.com'%self.id,
                'company_id':self.id,
                'company_ids':[(6,0,[self.id])],
            })
