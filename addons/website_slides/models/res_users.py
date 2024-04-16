#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_


classUsers(models.Model):
    _inherit='res.users'

    @api.model
    defcreate(self,values):
        """Triggerautomaticsubscriptionbasedonusergroups"""
        user=super(Users,self).create(values)
        self.env['slide.channel'].sudo().search([('enroll_group_ids','in',user.groups_id.ids)])._action_add_members(user.partner_id)
        returnuser

    defwrite(self,vals):
        """Triggerautomaticsubscriptionbasedonupdatedusergroups"""
        res=super(Users,self).write(vals)
        ifvals.get('groups_id'):
            added_group_ids=[command[1]forcommandinvals['groups_id']ifcommand[0]==4]
            added_group_ids+=[idforcommandinvals['groups_id']ifcommand[0]==6foridincommand[2]]
            self.env['slide.channel'].sudo().search([('enroll_group_ids','in',added_group_ids)])._action_add_members(self.mapped('partner_id'))
        returnres

    defget_gamification_redirection_data(self):
        res=super(Users,self).get_gamification_redirection_data()
        res.append({
            'url':'/slides',
            'label':_('SeeoureLearning')
        })
        returnres
