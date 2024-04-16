#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models

AVAILABLE_PRIORITIES=[
    ('0','Low'),
    ('1','Medium'),
    ('2','High'),
    ('3','VeryHigh'),
]


classStage(models.Model):
    """Modelforcasestages.Thismodelsthemainstagesofadocument
        managementflow.MainCRMobjects(leads,opportunities,project
        issues,...)willnowuseonlystages,insteadofstateandstages.
        Stagesareforexampleusedtodisplaythekanbanviewofrecords.
    """
    _name="crm.stage"
    _description="CRMStages"
    _rec_name='name'
    _order="sequence,name,id"

    @api.model
    defdefault_get(self,fields):
        """Hack: whengoingfromthepipeline,creatingastagewithasalesteamin
            contextshouldnotcreateastageforthecurrentSalesTeamonly
        """
        ctx=dict(self.env.context)
        ifctx.get('default_team_id')andnotctx.get('crm_team_mono'):
            ctx.pop('default_team_id')
        returnsuper(Stage,self.with_context(ctx)).default_get(fields)

    name=fields.Char('StageName',required=True,translate=True)
    sequence=fields.Integer('Sequence',default=1,help="Usedtoorderstages.Lowerisbetter.")
    is_won=fields.Boolean('IsWonStage?')
    requirements=fields.Text('Requirements',help="Enterheretheinternalrequirementsforthisstage(ex:Offersenttocustomer).Itwillappearasatooltipoverthestage'sname.")
    team_id=fields.Many2one('crm.team',string='SalesTeam',ondelete='setnull',
        help='Specificteamthatusesthisstage.Otherteamswillnotbeabletoseeorusethisstage.')
    fold=fields.Boolean('FoldedinPipeline',
        help='Thisstageisfoldedinthekanbanviewwhentherearenorecordsinthatstagetodisplay.')

    #Thisfieldforinterfaceonly
    team_count=fields.Integer('team_count',compute='_compute_team_count')

    @api.depends('name')
    def_compute_team_count(self):
        team_count=self.env['crm.team'].search_count([])
        forstageinself:
            stage.team_count=team_count
