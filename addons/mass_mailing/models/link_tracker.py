#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classLinkTracker(models.Model):
    _inherit="link.tracker"

    mass_mailing_id=fields.Many2one('mailing.mailing',string='MassMailing')


classLinkTrackerClick(models.Model):
    _inherit="link.tracker.click"

    mailing_trace_id=fields.Many2one('mailing.trace',string='MailStatistics')
    mass_mailing_id=fields.Many2one('mailing.mailing',string='MassMailing')

    def_prepare_click_values_from_route(self,**route_values):
        click_values=super(LinkTrackerClick,self)._prepare_click_values_from_route(**route_values)

        ifclick_values.get('mailing_trace_id'):
            trace_sudo=self.env['mailing.trace'].sudo().browse(route_values['mailing_trace_id']).exists()
            ifnottrace_sudo:
                click_values['mailing_trace_id']=False
            else:
                ifnotclick_values.get('campaign_id'):
                    click_values['campaign_id']=trace_sudo.campaign_id.id
                ifnotclick_values.get('mass_mailing_id'):
                    click_values['mass_mailing_id']=trace_sudo.mass_mailing_id.id

        returnclick_values

    @api.model
    defadd_click(self,code,**route_values):
        click=super(LinkTrackerClick,self).add_click(code,**route_values)

        ifclickandclick.mailing_trace_id:
            click.mailing_trace_id.set_opened()
            click.mailing_trace_id.set_clicked()

        returnclick
