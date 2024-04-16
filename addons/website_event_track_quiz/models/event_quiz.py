#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classQuiz(models.Model):
    _name="event.quiz"
    _description="Quiz"

    name=fields.Char('Name',required=True,translate=True)
    question_ids=fields.One2many('event.quiz.question','quiz_id',string="Questions")
    event_track_ids=fields.One2many('event.track','quiz_id',string="Tracks")
    event_track_id=fields.Many2one(
        'event.track',compute='_compute_event_track_id',
        readonly=True,store=True)
    event_id=fields.Many2one(
        'event.event',related='event_track_id.event_id',
        readonly=True,store=True)

    @api.depends('event_track_ids.quiz_id')
    def_compute_event_track_id(self):
        forquizinself:
            quiz.event_track_id=quiz.event_track_ids[0]ifquiz.event_track_idselseFalse


classQuizQuestion(models.Model):
    _name="event.quiz.question"
    _description="ContentQuizQuestion"
    _order="quiz_id,sequence,id"

    name=fields.Char("Question",required=True,translate=True)
    sequence=fields.Integer("Sequence")
    quiz_id=fields.Many2one("event.quiz","Quiz",required=True,ondelete='cascade')
    awarded_points=fields.Integer("NumberofPoints",compute='_compute_awarded_points')
    answer_ids=fields.One2many('event.quiz.answer','question_id',string="Answer")

    @api.depends('answer_ids.awarded_points')
    def_compute_awarded_points(self):
        forquestioninself:
            question.awarded_points=sum(question.answer_ids.mapped('awarded_points'))

    @api.constrains('answer_ids')
    def_check_answers_integrity(self):
        forquestioninself:
            iflen(question.answer_ids.filtered(lambdaanswer:answer.awarded_points))!=1:
                raiseValidationError(_('Question"%s"musthave1correctanswer',question.name))
            iflen(question.answer_ids)<2:
                raiseValidationError(_('Question"%s"musthave1correctanswerandatleast1incorrectanswer',question.name))


classQuizAnswer(models.Model):
    _name="event.quiz.answer"
    _rec_name="text_value"
    _description="Question'sAnswer"
    _order='question_id,sequence,id'

    sequence=fields.Integer("Sequence")
    question_id=fields.Many2one('event.quiz.question',string="Question",required=True,ondelete='cascade')
    text_value=fields.Char("Answer",required=True,translate=True)
    is_correct=fields.Boolean("Iscorrectanswer",compute='_compute_is_correct')
    comment=fields.Text("Comment",translate=True,
        help='''Thiscommentwillbedisplayedtotheuserifheselectsthisanswer,aftersubmittingthequiz.
                Itisusedasasmallinformationaltexthelpingtounderstandwhythisansweriscorrect/incorrect.''')
    awarded_points=fields.Integer('NumberofPoints')

    @api.depends('awarded_points')
    def_compute_is_correct(self):
        foranswerinself:
            answer.is_correct=bool(answer.awarded_points)
