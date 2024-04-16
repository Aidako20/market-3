#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classProjectTask(models.Model):
    _name="project.task"
    _inherit=["project.task",'pad.common']
    _description='Task'

    description_pad=fields.Char('PadURL',pad_content_field='description',copy=False)
    use_pad=fields.Boolean(related="project_id.use_pads",string="Usecollaborativepad",readonly=True)
    pad_availability=fields.Selection(
        related="project_id.pad_availability",
        string="Availabilityofcollaborativepads",
        readonly=True)

    @api.onchange('use_pad')
    def_onchange_use_pads(self):
        """Copythecontentinthepadwhentheuserchangetheprojectofthetasktotheonewithnopadsenabled.

            Thiscaseiswhentheuse_padbecomesFalseandwehavealreadygeneratedtheurlpad,
            thatisthedescription_padfieldcontainstheurlofthepad.
        """
        ifnotself.use_padandself.description_pad:
            vals={'description_pad':self.description_pad}
            self._set_pad_to_field(vals)
            self.description=vals['description']

    @api.model
    defcreate(self,vals):
        #Whenusingquickcreate,theproject_idisinthecontext,notinthevals
        project_id=vals.get('project_id',False)orself.default_get(['project_id']).get('project_id',False)
        ifnotself.env['project.project'].browse(project_id).use_pads:
            self=self.with_context(pad_no_create=True)
        returnsuper(ProjectTask,self).create(vals)

    def_use_portal_pad(self):
        """
        Indicatesifthetaskconfigurationrequirestoprovide
        anaccesstoaportalpad.
        """
        self.ensure_one()
        returnself.use_padandself.pad_availability=='portal'

    def_get_pad_content(self):
        """
        Getsthecontentofthepadusedtoeditthetaskdescription
        andreturnsit.
        """
        self.ensure_one()
        returnself.pad_get_content(self.description_pad)


classProjectProject(models.Model):
    _name="project.project"
    _inherit=["project.project",'pad.common']
    _description='Project'

    description_pad=fields.Char('PadURL',pad_content_field='description',copy=False)
    use_pads=fields.Boolean("Usecollaborativepads",default=True,
        help="Usecollaborativepadforthetasksonthisproject.")

    pad_availability=fields.Selection([
        ('internal','InternalUsers'),
        ('portal','InternalUsers&PortalUsers')
        ],compute='_compute_pad_availability',store=True,readonly=False,
        string='Availabilityofcollaborativepads',required=True,default='internal')

    @api.depends('use_pads','privacy_visibility')
    def_compute_pad_availability(self):
        forprojectinself:
            ifproject.privacy_visibility!='portal'ornotproject.use_pads:
                project.pad_availability='internal'
