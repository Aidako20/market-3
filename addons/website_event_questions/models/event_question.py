#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError


classEventQuestion(models.Model):
    _name='event.question'
    _rec_name='title'
    _order='sequence,id'
    _description='EventQuestion'

    title=fields.Char(required=True,translate=True)
    question_type=fields.Selection([
        ('simple_choice','Selection'),
        ('text_box','TextInput')],default='simple_choice',string="QuestionType",required=True)
    event_type_id=fields.Many2one('event.type','EventType',ondelete='cascade')
    event_id=fields.Many2one('event.event','Event',ondelete='cascade')
    answer_ids=fields.One2many('event.question.answer','question_id',"Answers",copy=True)
    sequence=fields.Integer(default=10)
    once_per_order=fields.Boolean('Askonlyonceperorder',
                                    help="IfTrue,thisquestionwillbeaskedonlyonceanditsvaluewillbepropagatedtoeveryattendees."
                                         "Ifnotitwillbeaskedforeveryattendeeofareservation.")

    @api.constrains('event_type_id','event_id')
    def_constrains_event(self):
        ifany(question.event_type_idandquestion.event_idforquestioninself):
            raiseUserError(_('Questioncannotbelongtoboththeeventcategoryanditself.'))

    defwrite(self,vals):
        """Weaddachecktopreventchangingthequestion_typeofaquestionthatalreadyhasanswers.
        Indeed,itwouldmessuptheevent.registration.answer(answertypenotmatchingthequestiontype)."""

        if'question_type'invals:
            questions_new_type=self.filtered(lambdaquestion:question.question_type!=vals['question_type'])
            ifquestions_new_type:
                answer_count=self.env['event.registration.answer'].search_count([('question_id','in',questions_new_type.ids)])
                ifanswer_count>0:
                    raiseUserError(_("Youcannotchangethequestiontypeofaquestionthatalreadyhasanswers!"))
        returnsuper(EventQuestion,self).write(vals)

    defaction_view_question_answers(self):
        """Allowanalyzingtheattendeesanswerstoeventquestionsinaconvenientway:
        -Agraphviewshowingcountsofeachsuggestionsforsimple_choicequestions
          (Alongwithsecondarypivotandtreeviews)
        -Atreeviewshowingtextualanswersvaluesfortext_boxquestions."""
        self.ensure_one()
        action=self.env["ir.actions.actions"]._for_xml_id("website_event_questions.action_event_registration_report")
        action['domain']=[('question_id','=',self.id)]
        ifself.question_type=='simple_choice':
            action['views']=[(False,'graph'),(False,'pivot'),(False,'tree')]
        elifself.question_type=='text_box':
            action['views']=[(False,'tree')]
        returnaction

classEventQuestionAnswer(models.Model):
    """Containssuggestedanswerstoa'simple_choice'event.question."""
    _name='event.question.answer'
    _order='sequence,id'
    _description='EventQuestionAnswer'

    name=fields.Char('Answer',required=True,translate=True)
    question_id=fields.Many2one('event.question',required=True,ondelete='cascade')
    sequence=fields.Integer(default=10)
