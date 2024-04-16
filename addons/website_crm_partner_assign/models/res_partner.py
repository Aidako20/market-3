#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.addons.http_routing.models.ir_httpimportslug


classResPartnerGrade(models.Model):
    _name='res.partner.grade'
    _order='sequence'
    _inherit=['website.published.mixin']
    _description='PartnerGrade'

    sequence=fields.Integer('Sequence')
    active=fields.Boolean('Active',default=lambda*args:1)
    name=fields.Char('LevelName',translate=True)
    partner_weight=fields.Integer('LevelWeight',default=1,
        help="Givestheprobabilitytoassignaleadtothispartner.(0meansnoassignment.)")

    def_compute_website_url(self):
        super(ResPartnerGrade,self)._compute_website_url()
        forgradeinself:
            grade.website_url="/partners/grade/%s"%(slug(grade))

    def_default_is_published(self):
        returnTrue


classResPartnerActivation(models.Model):
    _name='res.partner.activation'
    _order='sequence'
    _description='PartnerActivation'

    sequence=fields.Integer('Sequence')
    name=fields.Char('Name',required=True)


classResPartner(models.Model):
    _inherit="res.partner"

    partner_weight=fields.Integer(
        'LevelWeight',compute='_compute_partner_weight',
        readonly=False,store=True,tracking=True,
        help="Thisshouldbeanumericalvaluegreaterthan0whichwilldecidethecontentionforthispartnertotakethislead/opportunity.")
    grade_id=fields.Many2one('res.partner.grade','PartnerLevel',tracking=True)
    grade_sequence=fields.Integer(related='grade_id.sequence',readonly=True,store=True)
    activation=fields.Many2one('res.partner.activation','Activation',index=True,tracking=True)
    date_partnership=fields.Date('PartnershipDate')
    date_review=fields.Date('LatestPartnerReview')
    date_review_next=fields.Date('NextPartnerReview')
    #customerimplementation
    assigned_partner_id=fields.Many2one(
        'res.partner','Implementedby',
    )
    implemented_partner_ids=fields.One2many(
        'res.partner','assigned_partner_id',
        string='ImplementationReferences',
    )
    implemented_count=fields.Integer(compute='_compute_implemented_partner_count',store=True)

    @api.depends('implemented_partner_ids','implemented_partner_ids.website_published','implemented_partner_ids.active')
    def_compute_implemented_partner_count(self):
        forpartnerinself:
            partner.implemented_count=len(partner.implemented_partner_ids.filtered('website_published'))

    @api.depends('grade_id.partner_weight')
    def_compute_partner_weight(self):
        forpartnerinself:
            partner.partner_weight=partner.grade_id.partner_weightifpartner.grade_idelse0
