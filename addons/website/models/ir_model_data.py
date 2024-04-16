#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromflectraimportapi,models
fromflectra.httpimportrequest

_logger=logging.getLogger(__name__)


classIrModelData(models.Model):
    _inherit='ir.model.data'

    @api.model
    def_process_end_unlink_record(self,record):
        ifrecord._context['module'].startswith('theme_'):
            theme_records=self.env['ir.module.module']._theme_model_names.values()
            ifrecord._nameintheme_records:
                #useactive_testtoalsounlinkarchivedmodels
                #anduseMODULE_UNINSTALL_FLAGtoalsounlinkinheritedmodels
                copy_ids=record.with_context({
                    'active_test':False,
                    'MODULE_UNINSTALL_FLAG':True
                }).copy_ids
                ifrequest:
                    #weareinawebsitecontext,see`write()`overrideof
                    #ir.module.moduleinwebsite
                    current_website=self.env['website'].get_current_website()
                    copy_ids=copy_ids.filtered(lambdac:c.website_id==current_website)

                _logger.info('Deleting%s@%s(theme`copy_ids`)forwebsite%s',
                             copy_ids.ids,record._name,copy_ids.mapped('website_id'))
                copy_ids.unlink()

        returnsuper()._process_end_unlink_record(record)
