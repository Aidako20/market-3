#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

#
#OrderPointMethod:
#   -Orderifthevirtualstockoftodayisbelowtheminofthedefinedorderpoint
#

fromflectraimportapi,models,tools

importlogging
importthreading

_logger=logging.getLogger(__name__)


classStockSchedulerCompute(models.TransientModel):
    _name='stock.scheduler.compute'
    _description='RunSchedulerManually'

    def_procure_calculation_orderpoint(self):
        #Asthisfunctionisinanewthread,Ineedtoopenanewcursor,becausetheoldonemaybeclosed
        withapi.Environment.manage(),self.pool.cursor()asnew_cr:
            self=self.with_env(self.env(cr=new_cr))
            scheduler_cron=self.sudo().env.ref('stock.ir_cron_scheduler_action')
            #Avoidtoruntheschedulermultipletimesinthesametime
            try:
                withtools.mute_logger('flectra.sql_db'):
                    self._cr.execute("SELECTidFROMir_cronWHEREid=%sFORUPDATENOWAIT",(scheduler_cron.id,))
            exceptException:
                _logger.info('Attempttorunprocurementscheduleraborted,asalreadyrunning')
                self._cr.rollback()
                return{}

            forcompanyinself.env.user.company_ids:
                cids=(self.env.user.company_id|self.env.user.company_ids).ids
                self.env['procurement.group'].with_context(allowed_company_ids=cids).run_scheduler(
                    use_new_cursor=self._cr.dbname,
                    company_id=company.id)
            self._cr.rollback()
            return{}

    defprocure_calculation(self):
        threaded_calculation=threading.Thread(target=self._procure_calculation_orderpoint,args=())
        threaded_calculation.start()
        return{'type':'ir.actions.client','tag':'reload'}
