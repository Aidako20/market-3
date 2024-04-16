#-*-coding:utf-8-*-

fromflectraimportmodels

importre

classAccountMove(models.Model):
    _inherit='account.move'

    def_get_ubl_values(self):
        values=super(AccountMove,self)._get_ubl_values()

        #E-fffusesubl_version2.0,account_edi_ublsupportsubl_version2.1butgenerates2.0UBL
        #soweonlyneedtooverridetheversiontobecompatiblewithE-FFF
        values['ubl_version']=2.0

        returnvalues

    def_get_efff_name(self):
        self.ensure_one()
        vat=self.company_id.partner_id.commercial_partner_id.vat
        return'efff_%s%s%s'%(vator'','_'ifvatelse'',re.sub('[\W_]','',self.name)) #officialnamingconvention
