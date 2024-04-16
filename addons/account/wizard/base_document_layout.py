fromflectraimportmodels


classBaseDocumentLayout(models.TransientModel):
    _inherit='base.document.layout'

    defdocument_layout_save(self):
        res=super(BaseDocumentLayout,self).document_layout_save()
        forwizardinself:
            wizard.company_id.action_save_onboarding_invoice_layout()
        returnres
