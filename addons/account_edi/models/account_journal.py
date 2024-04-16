#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields,_
fromflectra.exceptionsimportUserError

fromcollectionsimportdefaultdict


classAccountJournal(models.Model):
    _inherit='account.journal'

    edi_format_ids=fields.Many2many(comodel_name='account.edi.format',
                                      string='Electronicinvoicing',
                                      help='SendXML/EDIinvoices',
                                      domain="[('id','in',compatible_edi_ids)]",
                                      compute='_compute_edi_format_ids',
                                      readonly=False,store=True)

    compatible_edi_ids=fields.Many2many(comodel_name='account.edi.format',
                                          compute='_compute_compatible_edi_ids',
                                          help='EDIformatthatsupportmovesinthisjournal')

    defwrite(self,vals):
        #OVERRIDE
        #Don'tallowtheusertodeactivateanediformathavingatleastonedocumenttobeprocessed.
        ifvals.get('edi_format_ids'):
            old_edi_format_ids=self.edi_format_ids
            res=super().write(vals)
            diff_edi_format_ids=old_edi_format_ids-self.edi_format_ids
            documents=self.env['account.edi.document'].search([
                ('move_id.journal_id','in',self.ids),
                ('edi_format_id','in',diff_edi_format_ids.ids),
                ('state','in',('to_cancel','to_send')),
            ])
            #Iftheformatsweareuncheckingdonotneedawebservice,wedon'tneedthemtobecorrectlysent
            ifdocuments.filtered(lambdad:d.edi_format_id._needs_web_services()):
                raiseUserError(_('Cannotdeactivate(%s)onthisjournalbecausenotalldocumentsaresynchronized',','.join(documents.edi_format_id.mapped('display_name'))))
            #removethesedocumentswhich:donotneedawebservice&arelinkedtotheediformatsweareunchecking
            ifdocuments:
                documents.unlink()
            returnres
        else:
            returnsuper().write(vals)

    @api.depends('type','company_id','company_id.country_id')
    def_compute_compatible_edi_ids(self):
        edi_formats=self.env['account.edi.format'].search([])

        forjournalinself:
            compatible_edis=edi_formats.filtered(lambdae:e._is_compatible_with_journal(journal))
            journal.compatible_edi_ids=compatible_edis

    @api.depends('type','company_id','company_id.country_id')
    def_compute_edi_format_ids(self):
        edi_formats=self.env['account.edi.format'].search([])
        journal_ids=self.ids

        ifjournal_ids:
            self._cr.execute('''
                SELECT
                    move.journal_id,
                    ARRAY_AGG(doc.edi_format_id)ASedi_format_ids
                FROMaccount_edi_documentdoc
                JOINaccount_movemoveONmove.id=doc.move_id
                WHEREdoc.stateIN('to_cancel','to_send')
                ANDmove.journal_idIN%s
                GROUPBYmove.journal_id
            ''',[tuple(journal_ids)])
            protected_edi_formats_per_journal={r[0]:set(r[1])forrinself._cr.fetchall()}
        else:
            protected_edi_formats_per_journal=defaultdict(set)

        forjournalinself:
            enabled_edi_formats=edi_formats.filtered(lambdae:e._is_compatible_with_journal(journal)and
                                                                 e._is_enabled_by_default_on_journal(journal))

            #Theexistingediformatsthatarealreadyinusesowecan'tremoveit.
            protected_edi_format_ids=protected_edi_formats_per_journal.get(journal.id,set())
            protected_edi_formats=journal.edi_format_ids.filtered(lambdae:e.idinprotected_edi_format_ids)

            journal.edi_format_ids=enabled_edi_formats+protected_edi_formats
