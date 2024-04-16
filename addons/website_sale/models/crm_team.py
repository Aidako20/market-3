#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,api,models,_
fromflectra.exceptionsimportUserError,ValidationError


classCrmTeam(models.Model):
    _inherit="crm.team"

    website_ids=fields.One2many('website','salesteam_id',string='Websites',help="WebsitesusingthisSalesTeam")
    abandoned_carts_count=fields.Integer(
        compute='_compute_abandoned_carts',
        string='NumberofAbandonedCarts',readonly=True)
    abandoned_carts_amount=fields.Integer(
        compute='_compute_abandoned_carts',
        string='AmountofAbandonedCarts',readonly=True)

    def_compute_abandoned_carts(self):
        #abandonedcartstorecoveraredraftsalesordersthathavenoorderlines,
        #apartnerotherthanthepublicuser,andcreatedoveranhourago
        #andtherecoverymailwasnotyetsent
        counts={}
        amounts={}
        website_teams=self.filtered(lambdateam:team.website_ids)
        ifwebsite_teams:
            abandoned_carts_data=self.env['sale.order'].read_group([
                ('is_abandoned_cart','=',True),
                ('cart_recovery_email_sent','=',False),
                ('team_id','in',website_teams.ids),
            ],['amount_total','team_id'],['team_id'])
            counts={data['team_id'][0]:data['team_id_count']fordatainabandoned_carts_data}
            amounts={data['team_id'][0]:data['amount_total']fordatainabandoned_carts_data}
        forteaminself:
            team.abandoned_carts_count=counts.get(team.id,0)
            team.abandoned_carts_amount=amounts.get(team.id,0)

    defget_abandoned_carts(self):
        self.ensure_one()
        return{
            'name':_('AbandonedCarts'),
            'type':'ir.actions.act_window',
            'view_mode':'tree,form',
            'domain':[('is_abandoned_cart','=',True)],
            'search_view_id':[self.env.ref('sale.sale_order_view_search_inherit_sale').id],
            'context':{
                'search_default_team_id':self.id,
                'default_team_id':self.id,
                'search_default_recovery_email':1,
                'create':False
            },
            'res_model':'sale.order',
            'help':_('''<pclass="o_view_nocontent_smiling_face">
                        Youcanfindallabandonedcartshere,i.e.thecartsgeneratedbyyourwebsite'svisitorsfromoveranhouragothathaven'tbeenconfirmedyet.</p>
                        <p>Youshouldsendanemailtothecustomerstoencouragethem!</p>
                    '''),
        }
