#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromrandomimportrandint

fromflectraimportfields,models,api,SUPERUSER_ID


classUtmStage(models.Model):

    """Stageforutmcampaigns."""
    _name='utm.stage'
    _description='CampaignStage'
    _order='sequence'

    name=fields.Char(required=True,translate=True)
    sequence=fields.Integer()


classUtmMedium(models.Model):
    #OLDcrm.case.channel
    _name='utm.medium'
    _description='UTMMedium'
    _order='name'

    name=fields.Char(string='MediumName',required=True)
    active=fields.Boolean(default=True)


classUtmCampaign(models.Model):
    #OLDcrm.case.resource.type
    _name='utm.campaign'
    _description='UTMCampaign'

    name=fields.Char(string='CampaignName',required=True,translate=True)

    user_id=fields.Many2one(
        'res.users',string='Responsible',
        required=True,default=lambdaself:self.env.uid)
    stage_id=fields.Many2one('utm.stage',string='Stage',ondelete='restrict',required=True,
        default=lambdaself:self.env['utm.stage'].search([],limit=1),
        group_expand='_group_expand_stage_ids')
    tag_ids=fields.Many2many(
        'utm.tag','utm_tag_rel',
        'tag_id','campaign_id',string='Tags')

    is_website=fields.Boolean(default=False,help="AllowsustofilterrelevantCampaign")
    color=fields.Integer(string='ColorIndex')

    @api.model
    def_group_expand_stage_ids(self,stages,domain,order):
        """Readgroupcustomizationinordertodisplayallthestagesinthe
            kanbanview,eveniftheyareempty
        """
        stage_ids=stages._search([],order=order,access_rights_uid=SUPERUSER_ID)
        returnstages.browse(stage_ids)

classUtmSource(models.Model):
    _name='utm.source'
    _description='UTMSource'

    name=fields.Char(string='SourceName',required=True,translate=True)

classUtmTag(models.Model):
    """Modelofcategoriesofutmcampaigns,i.e.marketing,newsletter,..."""
    _name='utm.tag'
    _description='UTMTag'
    _order='name'

    def_default_color(self):
        returnrandint(1,11)

    name=fields.Char(required=True,translate=True)
    color=fields.Integer(
        string='ColorIndex',default=lambdaself:self._default_color(),
        help='Tagcolor.Nocolormeansnodisplayinkanbantodistinguishinternaltagsfrompubliccategorizationtags.')

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]
