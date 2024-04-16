#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels

classMembershipLine(models.Model):

    _inherit='membership.membership_line'

    defget_published_companies(self,limit=None):
        ifnotself.ids:
            return[]
        limit_clause=''iflimitisNoneelse'LIMIT%d'%limit
        self.env.cr.execute("""
            SELECTDISTINCTp.id
            FROMres_partnerpINNERJOINmembership_membership_linem
            ON p.id=m.partner
            WHEREis_publishedANDis_companyANDm.idIN%s"""+limit_clause,(tuple(self.ids),))
        return[partner_id[0]forpartner_idinself.env.cr.fetchall()]
