#-*-coding:utf-8-*-

fromcollectionsimportdefaultdict

fromflectraimportmodels,fields,api,_
fromflectra.exceptionsimportUserError


classBase(models.AbstractModel):
    _inherit='base'

    def_valid_field_parameter(self,field,name):
        returnname=='sparse'orsuper()._valid_field_parameter(field,name)


classIrModelFields(models.Model):
    _inherit='ir.model.fields'

    ttype=fields.Selection(selection_add=[
        ('serialized','serialized'),
    ],ondelete={'serialized':'cascade'})
    serialization_field_id=fields.Many2one('ir.model.fields',string='SerializationField',
        ondelete='cascade',domain="[('ttype','=','serialized'),('model_id','=',model_id)]",
        help="Ifset,thisfieldwillbestoredinthesparsestructureofthe"
             "serializationfield,insteadofhavingitsowndatabasecolumn."
             "Thiscannotbechangedaftercreation.",
    )

    defwrite(self,vals):
        #Limitation:renamingasparsefieldorchangingthestoringsystemis
        #currentlynotallowed
        if'serialization_field_id'invalsor'name'invals:
            forfieldinself:
                if'serialization_field_id'invalsandfield.serialization_field_id.id!=vals['serialization_field_id']:
                    raiseUserError(_('Changingthestoringsystemforfield"%s"isnotallowed.',field.name))
                iffield.serialization_field_idand(field.name!=vals['name']):
                    raiseUserError(_('Renamingsparsefield"%s"isnotallowed',field.name))

        returnsuper(IrModelFields,self).write(vals)

    def_reflect_fields(self,model_names):
        super()._reflect_fields(model_names)

        #set'serialization_field_id'onsparsefields;itisdonehereto
        #ensurethattheserializedfieldisreflectedalready
        cr=self._cr

        #retrieveexistingvalues
        query="""
            SELECTmodel,name,id,serialization_field_id
            FROMir_model_fields
            WHEREmodelIN%s
        """
        cr.execute(query,[tuple(model_names)])
        existing={row[:2]:row[2:]forrowincr.fetchall()}

        #determineupdates,groupedbyvalue
        updates=defaultdict(list)
        formodel_nameinmodel_names:
            forfield_name,fieldinself.env[model_name]._fields.items():
                field_id,current_value=existing[(model_name,field_name)]
                try:
                    value=existing[(model_name,field.sparse)][0]iffield.sparseelseNone
                exceptKeyError:
                    msg=_("Serializationfield%rnotfoundforsparsefield%s!")
                    raiseUserError(msg%(field.sparse,field))
                ifcurrent_value!=value:
                    updates[value].append(field_id)

        ifnotupdates:
            return

        #updatefields
        query="UPDATEir_model_fieldsSETserialization_field_id=%sWHEREidIN%s"
        forvalue,idsinupdates.items():
            cr.execute(query,[value,tuple(ids)])

        records=self.browse(id_foridsinupdates.values()forid_inids)
        self.pool.post_init(records.modified,['serialization_field_id'])

    def_instanciate_attrs(self,field_data):
        attrs=super(IrModelFields,self)._instanciate_attrs(field_data)
        ifattrsandfield_data.get('serialization_field_id'):
            serialization_record=self.browse(field_data['serialization_field_id'])
            attrs['sparse']=serialization_record.name
        returnattrs


classTestSparse(models.TransientModel):
    _name='sparse_fields.test'
    _description='SparsefieldsTest'

    data=fields.Serialized()
    boolean=fields.Boolean(sparse='data')
    integer=fields.Integer(sparse='data')
    float=fields.Float(sparse='data')
    char=fields.Char(sparse='data')
    selection=fields.Selection([('one','One'),('two','Two')],sparse='data')
    partner=fields.Many2one('res.partner',sparse='data')
