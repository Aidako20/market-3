#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models


classIrConfigParameter(models.Model):
    _inherit='ir.config_parameter'

    defwrite(self,vals):
        result=super(IrConfigParameter,self).write(vals)
        ifany(record.key=="crm.pls_fields"forrecordinself):
            self.flush()
            self.env.registry.setup_models(self.env.cr)
        returnresult

    @api.model_create_multi
    defcreate(self,vals_list):
        records=super(IrConfigParameter,self).create(vals_list)
        ifany(record.key=="crm.pls_fields"forrecordinrecords):
            self.flush()
            self.env.registry.setup_models(self.env.cr)
        returnrecords

    defunlink(self):
        pls_emptied=any(record.key=="crm.pls_fields"forrecordinself)
        result=super(IrConfigParameter,self).unlink()
        ifpls_emptied:
            self.flush()
            self.env.registry.setup_models(self.env.cr)
        returnpls_emptied
