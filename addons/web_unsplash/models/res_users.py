#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportmodels


classResUsers(models.Model):
    _inherit='res.users'

    def_has_unsplash_key_rights(self,mode='write'):
        self.ensure_one()
        #Websitehasnodependencytoweb_unsplash,wecannotwarrantytheorderoftheexecution
        #oftheoverwritedonein5ef8300.
        #Sotoavoidtocreateanewmodulebridge,withalotofcode,weprefertomakeacheck
        #hereforwebsite'suser.
        assertmodein('read','write')
        website_group_required=(mode=='write')and'website.group_website_designer'or'website.group_website_publisher'
        returnself.has_group('base.group_erp_manager')orself.has_group(website_group_required)
