#-*-coding:utf-8-*-

fromastimportliteral_eval
fromcollectionsimportOrderedDict
fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportValidationError,MissingError
fromflectra.osvimportexpression
fromflectra.toolsimporthtml_escapeasescape
fromlxmlimportetreeasET
importlogging

_logger=logging.getLogger(__name__)


classWebsiteSnippetFilter(models.Model):
    _name='website.snippet.filter'
    _inherit=['website.published.multi.mixin']
    _description='WebsiteSnippetFilter'
    _order='nameASC'

    name=fields.Char(required=True,translate=True)
    action_server_id=fields.Many2one('ir.actions.server','ServerAction',ondelete='cascade')
    field_names=fields.Char(help="Alistofcomma-separatedfieldnames",required=True)
    filter_id=fields.Many2one('ir.filters','Filter',ondelete='cascade')
    limit=fields.Integer(help='Thelimitisthemaximumnumberofrecordsretrieved',required=True)
    website_id=fields.Many2one('website',string='Website',ondelete='cascade',required=True)

    @api.model
    defescape_falsy_as_empty(self,s):
        returnescape(s)ifselse''

    @api.constrains('action_server_id','filter_id')
    def_check_data_source_is_provided(self):
        forrecordinself:
            ifbool(record.action_server_id)==bool(record.filter_id):
                raiseValidationError(_("Eitheraction_server_idorfilter_idmustbeprovided."))

    @api.constrains('limit')
    def_check_limit(self):
        """Limitmustbebetween1and16."""
        forrecordinself:
            ifnot0<record.limit<=16:
                raiseValidationError(_("Thelimitmustbebetween1and16."))

    @api.constrains('field_names')
    def_check_field_names(self):
        forrecordinself:
            forfield_nameinrecord.field_names.split(","):
                ifnotfield_name.strip():
                    raiseValidationError(_("Emptyfieldnamein%r")%(record.field_names))

    defrender(self,template_key,limit,search_domain=[]):
        """Rendersthewebsitedynamicsnippetitems"""
        self.ensure_one()
        assert'.dynamic_filter_template_'intemplate_key,_("Youcanonlyusetemplateprefixedbydynamic_filter_template_")

        ifself.env['website'].get_current_website()!=self.website_id:
            return''

        records=self._prepare_values(limit,search_domain)
        View=self.env['ir.ui.view'].sudo().with_context(inherit_branding=False)
        content=View._render_template(template_key,dict(records=records)).decode('utf-8')
        return[ET.tostring(el,encoding='utf-8')forelinET.fromstring('<root>%s</root>'%content).getchildren()]

    def_prepare_values(self,limit=None,search_domain=None):
        """Getsthedataandreturnsittherightformatforrender."""
        self.ensure_one()
        limit=limitandmin(limit,self.limit)orself.limit
        ifself.filter_id:
            filter_sudo=self.filter_id.sudo()
            domain=filter_sudo._get_eval_domain()
            if'is_published'inself.env[filter_sudo.model_id]:
                domain=expression.AND([domain,[('is_published','=',True)]])
            ifsearch_domain:
                domain=expression.AND([domain,search_domain])
            try:
                records=self.env[filter_sudo.model_id].search(
                    domain,
                    order=','.join(literal_eval(filter_sudo.sort))orNone,
                    limit=limit
                )
                returnself._filter_records_to_dict_values(records)
            exceptMissingError:
                _logger.warning("Theprovideddomain%sin'ir.filters'generatedaMissingErrorin'%s'",domain,self._name)
                return[]
        elifself.action_server_id:
            try:
                returnself.action_server_id.with_context(
                    dynamic_filter=self,
                    limit=limit,
                    search_domain=search_domain,
                    get_rendering_data_structure=self._get_rendering_data_structure,
                ).sudo().run()
            exceptMissingError:
                _logger.warning("Theprovideddomain%sin'ir.actions.server'generatedaMissingErrorin'%s'",search_domain,self._name)
                return[]

    @api.model
    def_get_rendering_data_structure(self):
        return{
            'fields':OrderedDict({}),
            'image_fields':OrderedDict({}),
        }

    def_filter_records_to_dict_values(self,records):
        """Extractthefieldsfromthedatasourceandputthemintoadictionaryofvalues

            [{
                'fields':
                    OrderedDict([
                        ('name','Afghanistan'),
                        ('code','AF'),
                    ]),
                'image_fields':
                    OrderedDict([
                        ('image','/web/image/res.country/3/image?unique=5d9b44e')
                    ]),
             },...,...]

        """

        self.ensure_one()
        values=[]
        model=self.env[self.filter_id.model_id]
        Website=self.env['website']
        forrecordinrecords:
            data=self._get_rendering_data_structure()
            forfield_nameinself.field_names.split(","):
                field_name,_,field_widget=field_name.partition(":")
                field=model._fields.get(field_name)
                field_widget=field_widgetorfield.type
                iffield.type=='binary':
                    data['image_fields'][field_name]=self.escape_falsy_as_empty(Website.image_url(record,field_name))
                eliffield_widget=='image':
                    data['image_fields'][field_name]=self.escape_falsy_as_empty(record[field_name])
                eliffield_widget=='monetary':
                    FieldMonetary=self.env['ir.qweb.field.monetary']
                    model_currency=None
                    iffield.type=='monetary':
                        model_currency=record[record[field_name].currency_field]
                    elif'currency_id'inmodel._fields:
                        model_currency=record['currency_id']
                    ifmodel_currency:
                        website_currency=self._get_website_currency()
                        data['fields'][field_name]=FieldMonetary.value_to_html(
                            model_currency._convert(
                                record[field_name],
                                website_currency,
                                Website.get_current_website().company_id,
                                fields.Date.today()
                            ),
                            {'display_currency':website_currency}
                        )
                    else:
                        data['fields'][field_name]=self.escape_falsy_as_empty(record[field_name])
                elif('ir.qweb.field.%s'%field_widget)inself.env:
                    data['fields'][field_name]=self.env[('ir.qweb.field.%s'%field_widget)].record_to_html(record,field_name,{})
                else:
                    data['fields'][field_name]=self.escape_falsy_as_empty(record[field_name])

            data['fields']['call_to_action_url']='website_url'inrecordandrecord['website_url']
            values.append(data)
        returnvalues

    @api.model
    def_get_website_currency(self):
        company=self.env['website'].get_current_website().company_id
        returncompany.currency_id
