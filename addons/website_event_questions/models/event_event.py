#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classEventType(models.Model):
    _inherit='event.type'

    use_questions=fields.Boolean('QuestionstoAttendees')
    question_ids=fields.One2many(
        'event.question','event_type_id',
        string='Questions',copy=True)


classEventEvent(models.Model):
    """OverrideEventmodeltoaddoptionalquestionswhenbuyingtickets."""
    _inherit='event.event'

    question_ids=fields.One2many(
        'event.question','event_id','Questions',copy=True,
        compute='_compute_question_ids',readonly=False,store=True)
    general_question_ids=fields.One2many('event.question','event_id','GeneralQuestions',
                                           domain=[('once_per_order','=',True)])
    specific_question_ids=fields.One2many('event.question','event_id','SpecificQuestions',
                                            domain=[('once_per_order','=',False)])

    @api.depends('event_type_id')
    def_compute_question_ids(self):
        """Updateeventquestionsfromitseventtype.Dependsaresetonlyon
        event_type_iditselftoemulateanonchange.Changingeventtypecontent
        itselfshouldnottriggerthismethod.

        Whensynchronizingquestions:

          *linesthatnoanswerareremoved;
          *typelinesareadded;
        """
        ifself._origin.question_ids:
            #linestokeep:thosewithalreadysentemailsorregistrations
            questions_tokeep_ids=self.env['event.registration.answer'].search(
                [('question_id','in',self._origin.question_ids.ids)]
            ).question_id.ids
        else:
            questions_tokeep_ids=[]
        foreventinself:
            ifnotevent.event_type_idandnotevent.question_ids:
                event.question_ids=False
                continue

            ifquestions_tokeep_ids:
                questions_toremove=event._origin.question_ids.filtered(lambdaquestion:question.idnotinquestions_tokeep_ids)
                command=[(3,question.id)forquestioninquestions_toremove]
            else:
                command=[(5,0)]
            ifevent.event_type_id.use_questions:
                command+=[
                    (0,0,{
                        'title':question.title,
                        'question_type':question.question_type,
                        'sequence':question.sequence,
                        'once_per_order':question.once_per_order,
                        'answer_ids':[(0,0,{
                            'name':answer.name,
                            'sequence':answer.sequence
                        })foranswerinquestion.answer_ids],
                    })forquestioninevent.event_type_id.question_ids
                ]
            event.question_ids=command
