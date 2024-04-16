#-*-coding:utf-8-*-
fromflectraimportmodels


classAccountEdiFormat(models.Model):
    _inherit='account.edi.format'

    #-------------------------------------------------------------------------
    #Helpers
    #-------------------------------------------------------------------------

    def_get_proxy_user(self,company):
        '''Returnstheproxy_userassociatedwiththisediformat.
        '''
        self.ensure_one()
        returncompany.account_edi_proxy_client_ids.filtered(lambdau:u.edi_format_id==self)

    #-------------------------------------------------------------------------
    #Tooverride
    #-------------------------------------------------------------------------

    def_get_proxy_identification(self,company):
        '''Returnsthekeythatwillidentifycompanyuniquelyforthisediformat(forexample,thevat)
        orraisesaUserError(iftheuserdidn'tfilltherelatedfield).
        TOOVERRIDE
        '''
        returnFalse
