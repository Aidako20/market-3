#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importjson

fromflectraimporttests
fromflectra.toolsimportmute_logger


@tests.tagged('post_install','-at_install')
classTestControllers(tests.HttpCase):

    @mute_logger('flectra.addons.http_routing.models.ir_http','flectra.http')
    deftest_last_created_pages_autocompletion(self):
        self.authenticate("admin","admin")
        Page=self.env['website.page']
        last_5_url_edited=[]
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        suggested_links_url=base_url+'/website/get_suggested_links'

        foriinrange(0,10):
            new_page=Page.create({
                'name':'Generic',
                'type':'qweb',
                'arch':'''
                    <div>content</div>
                ''',
                'key':"test.generic_view-%d"%i,
                'url':"/generic-%d"%i,
                'is_published':True,
            })
            ifi%2==0:
                #markasold
                new_page._write({'write_date':'2020-01-01'})
            else:
                last_5_url_edited.append(new_page.url)

        res=self.opener.post(url=suggested_links_url,json={'params':{'needle':'/'}})
        resp=json.loads(res.content)
        assert'result'inresp
        suggested_links=resp['result']
        last_modified_history=next(oforoinsuggested_links['others']ifo["title"]=="Lastmodifiedpages")
        last_modified_values=map(lambdao:o['value'],last_modified_history['values'])

        matching_pages=set(map(lambdao:o['value'],suggested_links['matching_pages']))
        self.assertEqual(set(last_modified_values),set(last_5_url_edited)-matching_pages)
