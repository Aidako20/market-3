#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classHrEmployeeBase(models.AbstractModel):
    _inherit="hr.employee.base"

    child_all_count=fields.Integer(
        'IndirectSubordinatesCount',
        compute='_compute_subordinates',store=False,
        compute_sudo=True)

    def_get_subordinates(self,parents=None):
        """
        Helperfunctiontocomputesubordinates_ids.
        Getallsubordinates(directandindirect)ofanemployee.
        Anemployeecanbeamanagerofhisownmanager(recursivehierarchy;e.g.theCEOismanagerofeveryonebutisalso
        memberoftheRDdepartment,managedbytheCTOitselfmanagedbytheCEO).
        Inthatcase,themanagerinnotcountedasasubordinateifit'sinthe'parents'set.
        """
        ifnotparents:
            parents=self.env[self._name]

        indirect_subordinates=self.env[self._name]
        parents|=self
        direct_subordinates=self.child_ids-parents
        forchildindirect_subordinates:
            child_subordinate=child._get_subordinates(parents=parents)
            indirect_subordinates|=child_subordinate
        returnindirect_subordinates|direct_subordinates


    @api.depends('child_ids','child_ids.child_all_count')
    def_compute_subordinates(self):
        foremployeeinself:
            employee.subordinate_ids=employee._get_subordinates()
            employee.child_all_count=len(employee.subordinate_ids)
