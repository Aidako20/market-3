fromflectraimportmodels


classIrActionsReport(models.Model):
    _inherit='ir.actions.report'

    def_get_rendering_context(self,docids,data):
        data=super()._get_rendering_context(docids,data)
        data['din_header_spacing']=self.get_paperformat().header_spacing
        returndata
