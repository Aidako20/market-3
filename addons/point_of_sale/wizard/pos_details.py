#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classPosDetails(models.TransientModel):
    _name='pos.details.wizard'
    _description='PointofSaleDetailsReport'

    def_default_start_date(self):
        """Findtheearlieststart_dateofthelatestssessions"""
        #restricttoconfigsavailabletotheuser
        config_ids=self.env['pos.config'].search([]).ids
        #excludeconfigshasnotbeenopenedfor2days
        self.env.cr.execute("""
            SELECT
            max(start_at)asstart,
            config_id
            FROMpos_session
            WHEREconfig_id=ANY(%s)
            ANDstart_at>(NOW()-INTERVAL'2DAYS')
            GROUPBYconfig_id
        """,(config_ids,))
        latest_start_dates=[res['start']forresinself.env.cr.dictfetchall()]
        #earliestofthelatestsessions
        returnlatest_start_datesandmin(latest_start_dates)orfields.Datetime.now()

    start_date=fields.Datetime(required=True,default=_default_start_date)
    end_date=fields.Datetime(required=True,default=fields.Datetime.now)
    pos_config_ids=fields.Many2many('pos.config','pos_detail_configs',
        default=lambdas:s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def_onchange_start_date(self):
        ifself.start_dateandself.end_dateandself.end_date<self.start_date:
            self.end_date=self.start_date

    @api.onchange('end_date')
    def_onchange_end_date(self):
        ifself.end_dateandself.start_dateandself.end_date<self.start_date:
            self.start_date=self.end_date

    defgenerate_report(self):
        data={'date_start':self.start_date,'date_stop':self.end_date,'config_ids':self.pos_config_ids.ids}
        returnself.env.ref('point_of_sale.sale_details_report').report_action([],data=data)
