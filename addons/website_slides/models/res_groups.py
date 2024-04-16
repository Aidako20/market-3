#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classUserGroup(models.Model):
    _inherit='res.groups'

    defwrite(self,vals):
        """Automaticallysubscribenewuserstolinkedslidechannels"""
        write_res=super(UserGroup,self).write(vals)
        ifvals.get('users'):
            #TDEFIXME:maybedirectlycheckusersandsubscribethem
            self.env['slide.channel'].sudo().search([('enroll_group_ids','in',self._ids)])._add_groups_members()
        returnwrite_res
