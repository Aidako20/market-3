#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimport_,api,fields,models

_logger=logging.getLogger(__name__)


classAliasMixin(models.AbstractModel):
    """Amixinformodelsthatinheritsmail.alias.Thismixininitializesthe
        alias_idcolumnindatabase,andmanagestheexpectedone-to-one
        relationbetweenyourmodelandmailaliases.
    """
    _name='mail.alias.mixin'
    _inherits={'mail.alias':'alias_id'}
    _description='EmailAliasesMixin'
    ALIAS_WRITEABLE_FIELDS=['alias_name','alias_contact','alias_defaults','alias_bounced_content']

    alias_id=fields.Many2one('mail.alias',string='Alias',ondelete="restrict",required=True)

    #--------------------------------------------------
    #CRUD
    #--------------------------------------------------

    @api.model_create_multi
    defcreate(self,vals_list):
        """Createarecordwitheach``vals``or``vals_list``andcreateacorrespondingalias."""
        valid_vals_list=[]
        forvalsinvals_list:
            new_alias=notvals.get('alias_id')
            ifnew_alias:
                alias_vals,record_vals=self._alias_filter_fields(vals)
                alias_vals.update(self._alias_get_creation_values())
                alias=self.env['mail.alias'].sudo().create(alias_vals)
                record_vals['alias_id']=alias.id
                valid_vals_list.append(record_vals)
            else:
                valid_vals_list.append(vals)

        records=super(AliasMixin,self).create(valid_vals_list)

        forrecordinrecords:
            record.alias_id.sudo().write(record._alias_get_creation_values())

        returnrecords

    defwrite(self,vals):
        """Splitwritablefieldsofmail.aliasandotherfieldsaliasfieldswill
        writewithsudoandtheothernormally"""
        alias_vals,record_vals=self._alias_filter_fields(vals,filters=self.ALIAS_WRITEABLE_FIELDS)
        ifrecord_vals:
            super(AliasMixin,self).write(record_vals)
        ifalias_valsand(record_valsorself.check_access_rights('write',raise_exception=False)):
            self.mapped('alias_id').sudo().write(alias_vals)

        returnTrue

    defunlink(self):
        """Deletethegivenrecords,andcascade-deletetheircorrespondingalias."""
        aliases=self.mapped('alias_id')
        res=super(AliasMixin,self).unlink()
        aliases.sudo().unlink()
        returnres

    @api.returns(None,lambdavalue:value[0])
    defcopy_data(self,default=None):
        data=super(AliasMixin,self).copy_data(default)[0]
        forfields_not_writableinset(self.env['mail.alias']._fields.keys())-set(self.ALIAS_WRITEABLE_FIELDS):
            iffields_not_writableindata:
                deldata[fields_not_writable]
        return[data]

    def_init_column(self,name):
        """Createaliasesforexistingrows."""
        super(AliasMixin,self)._init_column(name)
        ifname=='alias_id':
            #as'mail.alias'recordsreferto'ir.model'records,create
            #aliasesafterthereflectionofmodels
            self.pool.post_init(self._init_column_alias_id)

    def_init_column_alias_id(self):
        #bothselfandthealiasmodelmustbepresentin'ir.model'
        child_ctx={
            'active_test':False,      #retrieveallrecords
            'prefetch_fields':False,  #donotprefetchfieldsonrecords
        }
        child_model=self.sudo().with_context(child_ctx)

        forrecordinchild_model.search([('alias_id','=',False)]):
            #createthealias,andlinkittothecurrentrecord
            alias=self.env['mail.alias'].sudo().create(record._alias_get_creation_values())
            record.with_context(mail_notrack=True).alias_id=alias
            _logger.info('Mailaliascreatedfor%s%s(id%s)',
                         record._name,record.display_name,record.id)

    #--------------------------------------------------
    #MIXINTOOLOVERRIDEMETHODS
    #--------------------------------------------------

    def_alias_get_creation_values(self):
        """Returnvaluestocreateanalias,ortowriteonthealiasafterits
            creation.
        """
        return{
            'alias_parent_thread_id':self.idifself.idelseFalse,
            'alias_parent_model_id':self.env['ir.model']._get(self._name).id,
        }

    def_alias_filter_fields(self,values,filters=False):
        """Splitthevalsdictintotwodictionnaryofvals,oneforalias
        fieldandtheotherforotherfields"""
        ifnotfilters:
            filters=self.env['mail.alias']._fields.keys()
        alias_values,record_values={},{}
        forfnameinvalues.keys():
            iffnameinfilters:
                alias_values[fname]=values.get(fname)
            else:
                record_values[fname]=values.get(fname)
        returnalias_values,record_values

    #--------------------------------------------------
    #GATEWAY
    #--------------------------------------------------

    def_alias_check_contact_on_record(self,record,message,message_dict,alias):
        """Moveto``BaseModel._alias_get_error_message()"""
        returnrecord._alias_get_error_message(message,message_dict,alias)
