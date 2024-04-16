#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models
fromflectra.tools.translateimporthtml_translate


classKarmaRank(models.Model):
    _name='gamification.karma.rank'
    _description='Rankbasedonkarma'
    _inherit='image.mixin'
    _order='karma_min'

    name=fields.Text(string='RankName',translate=True,required=True)
    description=fields.Html(string='Description',translate=html_translate,sanitize_attributes=False,)
    description_motivational=fields.Html(
        string='Motivational',translate=html_translate,sanitize_attributes=False,
        help="Motivationalphrasetoreachthisrank")
    karma_min=fields.Integer(
        string='RequiredKarma',required=True,default=1,
        help='Minimumkarmaneededtoreachthisrank')
    user_ids=fields.One2many('res.users','rank_id',string='Users',help="Usershavingthisrank")
    rank_users_count=fields.Integer("#Users",compute="_compute_rank_users_count")

    _sql_constraints=[
        ('karma_min_check',"CHECK(karma_min>0)",'Therequiredkarmahastobeabove0.')
    ]

    @api.depends('user_ids')
    def_compute_rank_users_count(self):
        requests_data=self.env['res.users'].read_group([('rank_id','!=',False)],['rank_id'],['rank_id'])
        requests_mapped_data=dict((data['rank_id'][0],data['rank_id_count'])fordatainrequests_data)
        forrankinself:
            rank.rank_users_count=requests_mapped_data.get(rank.id,0)

    @api.model_create_multi
    defcreate(self,values_list):
        res=super(KarmaRank,self).create(values_list)
        ifany(res.mapped('karma_min'))>0:
            users=self.env['res.users'].sudo().search([('karma','>=',max(min(res.mapped('karma_min')),1))])
            ifusers:
                users._recompute_rank()
        returnres

    defwrite(self,vals):
        if'karma_min'invals:
            previous_ranks=self.env['gamification.karma.rank'].search([],order="karma_minDESC").ids
            low=min(vals['karma_min'],min(self.mapped('karma_min')))
            high=max(vals['karma_min'],max(self.mapped('karma_min')))

        res=super(KarmaRank,self).write(vals)

        if'karma_min'invals:
            after_ranks=self.env['gamification.karma.rank'].search([],order="karma_minDESC").ids
            ifprevious_ranks!=after_ranks:
                users=self.env['res.users'].sudo().search([('karma','>=',max(low,1))])
            else:
                users=self.env['res.users'].sudo().search([('karma','>=',max(low,1)),('karma','<=',high)])
            users._recompute_rank()
        returnres
