#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMrpDocument(models.Model):
    """Extensionofir.attachmentonlyusedinMRPtohandlearchivage
    andbasicversioning.
    """
    _name='mrp.document'
    _description="ProductionDocument"
    _inherits={
        'ir.attachment':'ir_attachment_id',
    }
    _order="prioritydesc,iddesc"

    defcopy(self,default=None):
        ir_default=default
        ifir_default:
            ir_fields=list(self.env['ir.attachment']._fields)
            ir_default={field:default[field]forfieldindefault.keys()iffieldinir_fields}
        new_attach=self.ir_attachment_id.with_context(no_document=True).copy(ir_default)
        returnsuper().copy(dict(default,ir_attachment_id=new_attach.id))

    ir_attachment_id=fields.Many2one('ir.attachment',string='Relatedattachment',required=True,ondelete='cascade')
    active=fields.Boolean('Active',default=True)
    priority=fields.Selection([
        ('0','Normal'),
        ('1','Low'),
        ('2','High'),
        ('3','VeryHigh')],string="Priority",help='GivesthesequenceorderwhendisplayingalistofMRPdocuments.')
