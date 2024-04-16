#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,fields,models


classWebsiteRobots(models.TransientModel):
    _name="website.robots"
    _description="Robots.txtEditor"

    content=fields.Text(default=lambdas:s.env['website'].get_current_website().robots_txt)

    defaction_save(self):
        self.env['website'].get_current_website().robots_txt=self.content
        return{'type':'ir.actions.act_window_close'}
