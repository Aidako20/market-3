#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,_
fromflectra.exceptionsimportValidationError


classUsers(models.Model):
    _inherit="res.users"

    @api.constrains('groups_id')
    def_check_one_user_type(self):
        super(Users,self)._check_one_user_type()

        g1=self.env.ref('account.group_show_line_subtotals_tax_included',False)
        g2=self.env.ref('account.group_show_line_subtotals_tax_excluded',False)

        ifnotg1ornotg2:
            #Ausercannotbeinanon-existantgroup
            return

        foruserinself:
            ifuser._has_multiple_groups([g1.id,g2.id]):
                raiseValidationError(_("AusercannothavebothTaxB2BandTaxB2C.\n"
                                        "YoushouldgoinGeneralSettings,andchoosetodisplayProductPrices\n"
                                        "eitherin'Tax-Included'orin'Tax-Excluded'mode\n"
                                        "(orswitchtwicethemodeifyouarealreadyinthedesiredone)."))
