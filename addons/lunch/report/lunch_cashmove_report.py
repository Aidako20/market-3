#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,_


classCashmoveReport(models.Model):
    _name="lunch.cashmove.report"
    _description='Cashmovesreport'
    _auto=False
    _order="datedesc"

    id=fields.Integer('ID')
    amount=fields.Float('Amount')
    date=fields.Date('Date')
    currency_id=fields.Many2one('res.currency',string='Currency')
    user_id=fields.Many2one('res.users',string='User')
    description=fields.Text('Description')

    defname_get(self):
        return[(cashmove.id,'%s%s'%(_('LunchCashmove'),'#%d'%cashmove.id))forcashmoveinself]

    definit(self):
        tools.drop_view_if_exists(self._cr,self._table)

        self._cr.execute("""
            CREATEorREPLACEview%sas(
                SELECT
                    lc.idasid,
                    lc.amountasamount,
                    lc.dateasdate,
                    lc.currency_idascurrency_id,
                    lc.user_idasuser_id,
                    lc.descriptionasdescription
                FROMlunch_cashmovelc
                UNIONALL
                SELECT
                    -lol.idasid,
                    -lol.priceasamount,
                    lol.dateasdate,
                    lol.currency_idascurrency_id,
                    lol.user_idasuser_id,
                    format('Order:%%sx%%s%%s',lol.quantity::text,lp.name,lol.display_toppings)asdescription
                FROMlunch_orderlol
                JOINlunch_productlpONlp.id=lol.product_id
                WHERE
                    lol.statein('ordered','confirmed')
                    ANDlol.active=True
            );
        """%self._table)
