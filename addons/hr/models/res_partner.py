#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels
fromflectra.exceptionsimportAccessError


classPartner(models.Model):

    _inherit=['res.partner']

    defname_get(self):
        """Overridetoallowanemployeetoseeitsprivateaddressinhisprofile.
            Thisavoidstorelaxaccessruleson`res.parter`andtoaddan`ir.rule`.
            (advantageinbothsecurityandperformance).
            Useatry/exceptinsteadofsystematicallycheckingtominimizetheimpactonperformance.
            """
        try:
            returnsuper(Partner,self).name_get()
        exceptAccessErrorase:
            iflen(self)==1andselfinself.env.user.employee_ids.mapped('address_home_id'):
                returnsuper(Partner,self.sudo()).name_get()
            raisee
