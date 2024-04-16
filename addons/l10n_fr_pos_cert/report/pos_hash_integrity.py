#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classReportPosHashIntegrity(models.AbstractModel):
    _name='report.l10n_fr_pos_cert.report_pos_hash_integrity'
    _description='GetfrenchposhashintegrityresultasPDF.'

    @api.model
    def_get_report_values(self,docids,data=None):
        data=dataor{}
        data.update(self.env.company._check_pos_hash_integrity()or{})
        return{
            'doc_ids':docids,
            'doc_model':self.env['res.company'],
            'data':data,
            'docs':self.env['res.company'].browse(self.env.company.id),
        }
