#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classChannel(models.Model):
    _inherit='mail.channel'

    defpartner_info(self,all_partners,direct_partners):
        partner_infos=super(Channel,self).partner_info(all_partners,direct_partners)
        #onlysearchforleaveout_of_office_date_endifim_statusisonleave
        partners_on_leave=[partner_idforpartner_idindirect_partners.idsif'leave'inpartner_infos[partner_id]['im_status']]
        ifpartners_on_leave:
            now=fields.Datetime.now()
            self.env.cr.execute('''SELECTres_users.partner_idaspartner_id,hr_leave.date_toasdate_to
                                FROMres_users
                                JOINhr_leaveONhr_leave.user_id=res_users.id
                                ANDhr_leave.statenotin('cancel','refuse')
                                ANDres_users.active='t'
                                ANDhr_leave.date_from<=%s
                                ANDhr_leave.date_to>=%s
                                ANDres_users.partner_idin%s''',(now,now,tuple(partners_on_leave)))
            out_of_office_infos=dict(((res['partner_id'],res)forresinself.env.cr.dictfetchall()))
            forpartner_id,out_of_office_infoinout_of_office_infos.items():
                partner_infos[partner_id]['out_of_office_date_end']=out_of_office_info['date_to']

        #fillemptyvaluesfortheconsistencyoftheresult
        forpartner_infoinpartner_infos.values():
            partner_info.setdefault('out_of_office_date_end',False)

        returnpartner_infos
