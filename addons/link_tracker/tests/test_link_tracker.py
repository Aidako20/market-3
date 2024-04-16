#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

from.commonimportMockLinkTracker
fromflectra.testsimportcommon


classTestLinkTracker(common.TransactionCase,MockLinkTracker):
    @patch('flectra.addons.link_tracker.models.link_tracker.LinkTracker.get_base_url',
           return_value='http://example.com')
    deftest_no_external_tracking(self,mocked_get_base_url):
        self.env['ir.config_parameter'].set_param('link_tracker.no_external_tracking','1')

        campaign=self.env['utm.campaign'].create({'name':'campaign'})
        source=self.env['utm.source'].create({'name':'source'})
        medium=self.env['utm.medium'].create({'name':'medium'})

        expected_utm_params={
            'utm_campaign':campaign.name,
            'utm_source':source.name,
            'utm_medium':medium.name,
        }

        #URLtoanexternalwebsite->UTMparametersshouldnobeadded
        #becausethesystemparameter"no_external_tracking"isset
        link=self.env['link.tracker'].create({
            'url':'http://external.com/test?a=example.com',
            'campaign_id':campaign.id,
            'source_id':source.id,
            'medium_id':medium.id,
            'title':'Title',
        })
        self.assertLinkParams(
            'http://external.com/test',
            link,
            {'a':'example.com'}
        )

        #URLtothelocalwebsite->UTMparametersshouldbeaddedsinceweknowwehandlethem
        #eventhoughtheparameter"no_external_tracking"isenabled
        link.url='http://example.com/test?a=example.com'
        self.assertLinkParams(
            'http://example.com/test',
            link,
            {**expected_utm_params,'a':'example.com'}
        )

        #RelativeURLtothelocalwebsite->UTMparametersshouldbeaddedsinceweknowwehandlethem
        #eventhoughtheparameter"no_external_tracking"isenabled
        link.url='/test?a=example.com'

        self.assertLinkParams(
            '/test',
            link,
            {**expected_utm_params,'a':'example.com'}
        )

        #Deactivatethesystemparameter
        self.env['ir.config_parameter'].set_param('link_tracker.no_external_tracking',False)

        #URLtoanexternalwebsite->UTMparametersshouldbeaddedsince
        #thesystem parameter"link_tracker.no_external_tracking"isdisabled
        link.url='http://external.com/test?a=example.com'
        self.assertLinkParams(
            'http://external.com/test',
            link,
            {**expected_utm_params,'a':'example.com'}
        )
