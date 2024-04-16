#-*-coding:utf-8-*-

importcalendar
fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,models,api,_
fromflectra.exceptionsimportUserError


classResCompany(models.Model):
    _inherit='res.company'

    def_autorise_lock_date_changes(self,vals):
        '''Checkthelockdatesforthecurrentcompanies.Thiscan'tbedoneinaapi.constrainsbecauseweneed
        toperformsomecomparisonbetweennew/oldvalues.Thismethodforcesthelockdatestobeirreversible.
        *Youcannotsetstricterrestrictionsonadvisorsthanonusers.
        Therefore,theAllUsersLockDatemustbeanterior(orequal)totheInvoice/BillsLockDate.
        *Youcannotlockaperiodthathasnotyetended.
        Therefore,theAllUsersLockDatemustbeanterior(orequal)tothelastdayofthepreviousmonth.
        *AnynewAllUsersLockDatemustbeposterior(orequal)tothepreviousone.
        *Youcannotdeleteataxlockdate,lockaperiodthatisnotfinishedyetorthetaxlockdatemustbesetafter
        thelastdayofthepreviousmonth.
        :paramvals:Thevaluespassedtothewritemethod.
        '''
        period_lock_date=vals.get('period_lock_date')andfields.Date.from_string(vals['period_lock_date'])
        fiscalyear_lock_date=vals.get('fiscalyear_lock_date')andfields.Date.from_string(vals['fiscalyear_lock_date'])
        tax_lock_date=vals.get('tax_lock_date')andfields.Date.from_string(vals['tax_lock_date'])

        previous_month=fields.Date.today()+relativedelta(months=-1)
        days_previous_month=calendar.monthrange(previous_month.year,previous_month.month)
        previous_month=previous_month.replace(day=days_previous_month[1])
        forcompanyinself:
            old_fiscalyear_lock_date=company.fiscalyear_lock_date
            old_period_lock_date=company.period_lock_date
            old_tax_lock_date=company.tax_lock_date

            #Theuserattemptstoremovethetaxlockdate
            ifold_tax_lock_dateandnottax_lock_dateand'tax_lock_date'invals:
                raiseUserError(_('Thetaxlockdateisirreversibleandcan\'tberemoved.'))

            #Theuserattemptstosetataxlockdatepriortothepreviousone
            ifold_tax_lock_dateandtax_lock_dateandtax_lock_date<old_tax_lock_date:
                raiseUserError(_('Thenewtaxlockdatemustbesetafterthepreviouslockdate.'))

            #Incaseofnonewtaxlockdateinvals,fallbacktotheoldest
            tax_lock_date=tax_lock_dateorold_tax_lock_date
            #Theuserattemptstosetataxlockdatepriortothelastdayofpreviousmonth
            iftax_lock_dateandtax_lock_date>previous_month:
                raiseUserError(_('Youcannotlockaperiodthathasnotyetended.Therefore,thetaxlockdatemustbeanterior(orequal)tothelastdayofthepreviousmonth.'))

            #Theuserattemptstoremovethelockdateforadvisors
            ifold_fiscalyear_lock_dateandnotfiscalyear_lock_dateand'fiscalyear_lock_date'invals:
                raiseUserError(_('Thelockdateforadvisorsisirreversibleandcan\'tberemoved.'))

            #Theuserattemptstosetalockdateforadvisorspriortothepreviousone
            ifold_fiscalyear_lock_dateandfiscalyear_lock_dateandfiscalyear_lock_date<old_fiscalyear_lock_date:
                raiseUserError(_('AnynewAllUsersLockDatemustbeposterior(orequal)tothepreviousone.'))

            #Incaseofnonewfiscalyearinvals,fallbacktotheoldest
            fiscalyear_lock_date=fiscalyear_lock_dateorold_fiscalyear_lock_date
            ifnotfiscalyear_lock_date:
                continue

            #Theuserattemptstosetalockdateforadvisorspriortothelastdayofpreviousmonth
            iffiscalyear_lock_date>previous_month:
                raiseUserError(_('Youcannotlockaperiodthathasnotyetended.Therefore,theAllUsersLockDatemustbeanterior(orequal)tothelastdayofthepreviousmonth.'))

            #Incaseofnonewperiodlockdateinvals,fallbacktotheonedefinedinthecompany
            period_lock_date=period_lock_dateorold_period_lock_date
            ifnotperiod_lock_date:
                continue

            #Theuserattemptstosetalockdateforadvisorspriortothelockdateforusers
            ifperiod_lock_date<fiscalyear_lock_date:
                raiseUserError(_('Youcannotsetstricterrestrictionsonadvisorsthanonusers.Therefore,theAllUsersLockDatemustbeanterior(orequal)totheInvoice/BillsLockDate.'))

    defwrite(self,vals):
        #fiscalyear_lock_datecan'tbesettoapriordate
        if'fiscalyear_lock_date'invalsor'period_lock_date'invalsor'tax_lock_date'invals:
            self._autorise_lock_date_changes(vals)
        returnsuper(ResCompany,self).write(vals)
