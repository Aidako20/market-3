#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,fields,api,SUPERUSER_ID
fromflectra.httpimportrequest


classwebsite_form_config(models.Model):
    _inherit='website'

    def_website_form_last_record(self):
        ifrequestandrequest.session.form_builder_model_model:
            returnrequest.env[request.session.form_builder_model_model].browse(request.session.form_builder_id)
        returnFalse


classwebsite_form_model(models.Model):
    _name='ir.model'
    _description='Models'
    _inherit='ir.model'

    website_form_access=fields.Boolean('Allowedtouseinforms',help='Enabletheformbuilderfeatureforthismodel.')
    website_form_default_field_id=fields.Many2one('ir.model.fields','Fieldforcustomformdata',domain="[('model','=',model),('ttype','=','text')]",help="Specifythefieldwhichwillcontainmetaandcustomformfieldsdatas.")
    website_form_label=fields.Char("Labelforformaction",help="Formactionlabel.Ex:crm.leadcouldbe'Sendane-mail'andproject.issuecouldbe'CreateanIssue'.")
    website_form_key=fields.Char(help='UsedinFormBuilderRegistry')

    def_get_form_writable_fields(self):
        """
        Restrictionof"authorizedfields"(fieldswhichcanbeusedinthe
        formbuilders)tofieldswhichhaveactuallybeenoptedintoform
        buildersandarewritable.Bydefaultnofieldiswritablebythe
        formbuilder.
        """
        ifself.model=="mail.mail":
            included={'email_from','email_to','email_cc','email_bcc','body','reply_to','subject'}
        else:
            included={
                field.name
                forfieldinself.env['ir.model.fields'].sudo().search([
                    ('model_id','=',self.id),
                    ('website_form_blacklisted','=',False)
                ])
            }

        return{
            k:vfork,vinself.get_authorized_fields(self.model).items()
            ifkinincluded
        }

    @api.model
    defget_authorized_fields(self,model_name):
        """Returnthefieldsofthegivenmodelnameasamappinglikemethod`fields_get`."""
        model=self.env[model_name]
        fields_get=model.fields_get()

        forkey,valinmodel._inherits.items():
            fields_get.pop(val,None)

        #Unrequirefieldswithdefaultvalues
        default_values=model.with_user(SUPERUSER_ID).default_get(list(fields_get))
        forfieldin[fforfinfields_getiffindefault_values]:
            fields_get[field]['required']=False

        #Removereadonlyandmagicfields
        #Removestringdomainswhicharesupposedtobeevaluated
        #(e.g."[('product_id','=',product_id)]")
        MAGIC_FIELDS=models.MAGIC_COLUMNS+[model.CONCURRENCY_CHECK_FIELD]
        forfieldinlist(fields_get):
            if'domain'infields_get[field]andisinstance(fields_get[field]['domain'],str):
                delfields_get[field]['domain']
            iffields_get[field].get('readonly')orfieldinMAGIC_FIELDSorfields_get[field]['type']=='many2one_reference':
                delfields_get[field]

        returnfields_get


classwebsite_form_model_fields(models.Model):
    """fieldsconfigurationforformbuilder"""
    _name='ir.model.fields'
    _description='Fields'
    _inherit='ir.model.fields'

    definit(self):
        #setallexistingunsetwebsite_form_blacklistedfieldsto``true``
        # (sothatwecanuseitasawhitelistratherthanablacklist)
        self._cr.execute('UPDATEir_model_fields'
                         'SETwebsite_form_blacklisted=true'
                         'WHEREwebsite_form_blacklistedISNULL')
        #addanSQL-leveldefaultvalueonwebsite_form_blacklistedtothat
        #pure-SQLir.model.fieldcreations(e.g.in_reflect)generate
        #therightdefaultvalueforawhitelist(akafieldsshouldbe
        #blacklistedbydefault)
        self._cr.execute('ALTERTABLEir_model_fields'
                         'ALTERCOLUMNwebsite_form_blacklistedSETDEFAULTtrue')

    @api.model
    defformbuilder_whitelist(self,model,fields):
        """
        :paramstrmodel:nameofthemodelonwhichtowhitelistfields
        :paramlist(str)fields:listoffieldstowhitelistonthemodel
        :return:nothingofimport
        """
        #postgresdoes*not*like``in[EMPTYTUPLE]``queries
        ifnotfields:returnFalse

        #onlyallowuserswhocanchangethewebsitestructure
        ifnotself.env['res.users'].has_group('website.group_website_designer'):
            returnFalse

        #theORMonlyallowswritingoncustomfieldsandwilltriggera
        #registryreloadoncethat'shappened.Wewanttobeableto
        #whitelistnon-customfieldsandtheregistryreloadabsolutely
        #isn'tdesirable,sogowithamethodandrawSQL
        self.env.cr.execute(
            "UPDATEir_model_fields"
            "SETwebsite_form_blacklisted=false"
            "WHEREmodel=%sANDnamein%s",(model,tuple(fields)))
        returnTrue

    website_form_blacklisted=fields.Boolean(
        'Blacklistedinwebforms',default=True,index=True,#required=True,
        help='Blacklistthisfieldforwebforms'
    )
