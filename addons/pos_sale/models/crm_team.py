#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
fromdatetimeimportdatetime
importpytz


classCrmTeam(models.Model):
    _inherit='crm.team'

    pos_config_ids=fields.One2many('pos.config','crm_team_id',string="PointofSales")
    pos_sessions_open_count=fields.Integer(string='OpenPOSSessions',compute='_compute_pos_sessions_open_count')
    pos_order_amount_total=fields.Float(string="SessionSaleAmount",compute='_compute_pos_order_amount_total')

    def_compute_pos_sessions_open_count(self):
        forteaminself:
            team.pos_sessions_open_count=self.env['pos.session'].search_count([('config_id.crm_team_id','=',team.id),('state','=','opened')])

    def_compute_pos_order_amount_total(self):
        data=self.env['report.pos.order'].read_group([
            ('session_id.state','=','opened'),
            ('config_id.crm_team_id','in',self.ids),
        ],['price_total:sum','config_id'],['config_id'])
        rg_results=dict((d['config_id'][0],d['price_total'])fordindata)
        forteaminself:
            team.pos_order_amount_total=sum([
                rg_results.get(config.id,0.0)
                forconfiginteam.pos_config_ids
            ])
