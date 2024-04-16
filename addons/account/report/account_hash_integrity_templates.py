#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classReportAccountHashIntegrity(models.AbstractModel):
    _name='report.account.report_hash_integrity'
    _description='GethashintegrityresultasPDF.'

    @api.model
    def_get_report_values(self,docids,data=None):
        ifdata:
            data.update(self.env.company._check_hash_integrity())
        else:
            data=self.env.company._check_hash_integrity()
        return{
            'doc_ids':docids,
            'doc_model':self.env['res.company'],
            'data':data,
            'docs':self.env['res.company'].browse(self.env.company.id),
        }
