#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classIrModelField(models.Model):
    _inherit='ir.model.fields'

    tracking=fields.Integer(
        string="EnableOrderedTracking",
        help="Ifseteverymodificationdonetothisfieldistrackedinthechatter.Valueisusedtoordertrackingvalues.",
    )

    def_reflect_field_params(self,field,model_id):
        """Trackingvaluecanbeeitherabooleanenablingtrackingmechanism
        onfield,eitheranintegergivingthesequence.Defaultsequenceis
        setto100."""
        vals=super(IrModelField,self)._reflect_field_params(field,model_id)
        tracking=getattr(field,'tracking',None)
        iftrackingisTrue:
            tracking=100
        eliftrackingisFalse:
            tracking=None
        vals['tracking']=tracking
        returnvals

    def_instanciate_attrs(self,field_data):
        attrs=super(IrModelField,self)._instanciate_attrs(field_data)
        ifattrsandfield_data.get('tracking'):
            attrs['tracking']=field_data['tracking']
        returnattrs
