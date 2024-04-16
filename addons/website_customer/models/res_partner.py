#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classPartner(models.Model):

    _inherit='res.partner'

    website_tag_ids=fields.Many2many('res.partner.tag','res_partner_res_partner_tag_rel','partner_id','tag_id',string='Websitetags')

    defget_backend_menu_id(self):
        returnself.env.ref('contacts.menu_contacts').id


classTags(models.Model):

    _name='res.partner.tag'
    _description='PartnerTags-Thesetagscanbeusedonwebsitetofindcustomersbysector,or...'
    _inherit='website.published.mixin'

    @api.model
    defget_selection_class(self):
        classname=['default','primary','success','warning','danger']
        return[(x,str.title(x))forxinclassname]

    name=fields.Char('CategoryName',required=True,translate=True)
    partner_ids=fields.Many2many('res.partner','res_partner_res_partner_tag_rel','tag_id','partner_id',string='Partners')
    classname=fields.Selection('get_selection_class','Class',default='default',help="Bootstrapclasstocustomizethecolor",required=True)
    active=fields.Boolean('Active',default=True)

    def_default_is_published(self):
        returnTrue
