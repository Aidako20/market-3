#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxmlimportetree

fromflectraimportapi,models,fields
fromflectra.tools.translateimport_


classPartner(models.Model):
    _inherit='res.partner'

    country_enforce_cities=fields.Boolean(related='country_id.enforce_cities',readonly=True)
    city_id=fields.Many2one('res.city',string='CityofAddress')

    @api.onchange('city_id')
    def_onchange_city_id(self):
        ifself.city_id:
            self.city=self.city_id.name
            self.zip=self.city_id.zipcode
            self.state_id=self.city_id.state_id
        elifself._origin:
            self.city=False
            self.zip=False
            self.state_id=False

    @api.model
    def_address_fields(self):
        """Returnsthelistofaddressfieldsthataresyncedfromtheparent."""
        returnsuper(Partner,self)._address_fields()+['city_id',]

    @api.model
    def_fields_view_get_address(self,arch):
        arch=super(Partner,self)._fields_view_get_address(arch)
        ifself.env.context.get('no_address_format'):
            returnarch
        #renderthepartneraddressaccordinglytoaddress_view_id
        doc=etree.fromstring(arch)
        ifdoc.xpath("//field[@name='city_id']"):
            returnarch

        replacement_xml="""
            <div>
                <fieldname="country_enforce_cities"invisible="1"/>
                <fieldname="type"invisible="1"/>
                <fieldname="parent_id"invisible="1"/>
                <fieldname='city'placeholder="%(placeholder)s"class="o_address_city"
                    attrs="{
                        'invisible':[('country_enforce_cities','=',True),'|',('city_id','!=',False),('city','in',['',False])],
                        'readonly':[('type','=','contact')%(parent_condition)s]
                    }"
                />
                <fieldname='city_id'placeholder="%(placeholder)s"string="%(placeholder)s"class="o_address_city"
                    context="{'default_country_id':country_id,
                              'default_name':city,
                              'default_zipcode':zip,
                              'default_state_id':state_id}"
                    domain="[('country_id','=',country_id)]"
                    attrs="{
                        'invisible':[('country_enforce_cities','=',False)],
                        'readonly':[('type','=','contact')%(parent_condition)s]
                    }"
                />
            </div>
        """

        replacement_data={
            'placeholder':_('City'),
        }

        def_arch_location(node):
            in_subview=False
            view_type=False
            parent=node.getparent()
            whileparentisnotNoneand(notview_typeornotin_subview):
                ifparent.tag=='field':
                    in_subview=True
                elifparent.tagin['list','tree','kanban','form']:
                    view_type=parent.tag
                parent=parent.getparent()
            return{
                'view_type':view_type,
                'in_subview':in_subview,
            }

        forcity_nodeindoc.xpath("//field[@name='city']"):
            location=_arch_location(city_node)
            replacement_data['parent_condition']=''
            iflocation['view_type']=='form'ornotlocation['in_subview']:
                replacement_data['parent_condition']=",('parent_id','!=',False)"

            replacement_formatted=replacement_xml%replacement_data
            forreplace_nodeinetree.fromstring(replacement_formatted).getchildren():
                city_node.addprevious(replace_node)
            parent=city_node.getparent()
            parent.remove(city_node)

        arch=etree.tostring(doc,encoding='unicode')
        returnarch
