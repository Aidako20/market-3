#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.modules.moduleimportget_resource_path


classSponsor(models.Model):
    _name="event.sponsor"
    _description='EventSponsor'
    _order="sequence,sponsor_type_id"
    _rec_name='name'
    _inherit=['mail.thread','mail.activity.mixin']

    event_id=fields.Many2one('event.event','Event',required=True)
    sponsor_type_id=fields.Many2one('event.sponsor.type','SponsoringType',required=True)
    url=fields.Char('SponsorWebsite',compute='_compute_url',readonly=False,store=True)
    sequence=fields.Integer('Sequence')
    active=fields.Boolean(default=True)
    #contactinformation
    partner_id=fields.Many2one('res.partner','Sponsor/Customer',required=True)
    partner_name=fields.Char('Name',related='partner_id.name')
    partner_email=fields.Char('Email',related='partner_id.email')
    partner_phone=fields.Char('Phone',related='partner_id.phone')
    partner_mobile=fields.Char('Mobile',related='partner_id.mobile')
    name=fields.Char('SponsorName',compute='_compute_name',readonly=False,store=True)
    email=fields.Char('SponsorEmail',compute='_compute_email',readonly=False,store=True)
    phone=fields.Char('SponsorPhone',compute='_compute_phone',readonly=False,store=True)
    mobile=fields.Char('SponsorMobile',compute='_compute_mobile',readonly=False,store=True)
    #image
    image_512=fields.Image(
        string="Logo",max_width=512,max_height=512,
        compute='_compute_image_512',readonly=False,store=True)
    image_256=fields.Image("Image256",related="image_512",max_width=256,max_height=256,store=False)
    image_128=fields.Image("Image128",related="image_512",max_width=128,max_height=128,store=False)
    website_image_url=fields.Char(
        string='ImageURL',
        compute='_compute_website_image_url',compute_sudo=True,store=False)

    @api.depends('partner_id')
    def_compute_url(self):
        forsponsorinself:
            ifsponsor.partner_id.websiteornotsponsor.url:
                sponsor.url=sponsor.partner_id.website

    @api.depends('partner_id')
    def_compute_name(self):
        self._synchronize_with_partner('name')

    @api.depends('partner_id')
    def_compute_email(self):
        self._synchronize_with_partner('email')

    @api.depends('partner_id')
    def_compute_phone(self):
        self._synchronize_with_partner('phone')

    @api.depends('partner_id')
    def_compute_mobile(self):
        self._synchronize_with_partner('mobile')

    @api.depends('partner_id')
    def_compute_image_512(self):
        self._synchronize_with_partner('image_512')

    @api.depends('image_256','partner_id.image_256')
    def_compute_website_image_url(self):
        forsponsorinself:
            ifsponsor.image_256:
                sponsor.website_image_url=self.env['website'].image_url(sponsor,'image_256',size=256)
            elifsponsor.partner_id.image_256:
                sponsor.website_image_url=self.env['website'].image_url(sponsor.partner_id,'image_256',size=256)
            else:
                sponsor.website_image_url=get_resource_path('website_event_track','static/src/img','event_sponsor_default_%d.png'%(sponsor.id%1))

    def_synchronize_with_partner(self,fname):
        """Synchronizewithpartnerifnotset.Settingavaluedoesnotwrite
        onpartnerasthismaybeevent-specificinformation."""
        forsponsorinself:
            ifnotsponsor[fname]:
                sponsor[fname]=sponsor.partner_id[fname]

    #------------------------------------------------------------
    #MESSAGING
    #------------------------------------------------------------

    def_message_get_suggested_recipients(self):
        recipients=super(Sponsor,self)._message_get_suggested_recipients()
        forsponsorinself:
            ifsponsor.partner_id:
                sponsor._message_add_suggested_recipient(
                    recipients,
                    partner=sponsor.partner_id,
                    reason=_('Sponsor')
                )
        returnrecipients
