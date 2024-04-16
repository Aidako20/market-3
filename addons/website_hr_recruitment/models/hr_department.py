#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classDepartment(models.Model):
    _inherit='hr.department'

    defname_get(self):
        #Getdepartmentnameusingsuperuser,becausemodelisnotaccessible
        #forportalusers
        self_sudo=self.sudo()
        returnsuper(Department,self_sudo).name_get()
