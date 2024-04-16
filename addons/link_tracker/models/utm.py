#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classUtmCampaign(models.Model):
    _inherit=['utm.campaign']
    _description='UTMCampaign'

    click_count=fields.Integer(string="Numberofclicksgeneratedbythecampaign",compute="_compute_clicks_count")

    def_compute_clicks_count(self):
        click_data=self.env['link.tracker.click'].read_group(
            [('campaign_id','in',self.ids)],
            ['campaign_id'],['campaign_id'])

        mapped_data={datum['campaign_id'][0]:datum['campaign_id_count']fordatuminclick_data}

        forcampaigninself:
            campaign.click_count=mapped_data.get(campaign.id,0)
