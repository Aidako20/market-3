#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError


classSlideQuestion(models.Model):
    _name="slide.question"
    _rec_name="question"
    _description="ContentQuizQuestion"
    _order="sequence"

    sequence=fields.Integer("Sequence")
    question=fields.Char("QuestionName",required=True,translate=True)
    slide_id=fields.Many2one('slide.slide',string="Content",required=True)
    answer_ids=fields.One2many('slide.answer','question_id',string="Answer")
    #statistics
    attempts_count=fields.Integer(compute='_compute_statistics',groups='website_slides.group_website_slides_officer')
    attempts_avg=fields.Float(compute="_compute_statistics",digits=(6,2),groups='website_slides.group_website_slides_officer')
    done_count=fields.Integer(compute="_compute_statistics",groups='website_slides.group_website_slides_officer')

    @api.constrains('answer_ids')
    def_check_answers_integrity(self):
        forquestioninself:
            iflen(question.answer_ids.filtered(lambdaanswer:answer.is_correct))!=1:
                raiseValidationError(_('Question"%s"musthave1correctanswer',question.question))
            iflen(question.answer_ids)<2:
                raiseValidationError(_('Question"%s"musthave1correctanswerandatleast1incorrectanswer',question.question))

    @api.depends('slide_id')
    def_compute_statistics(self):
        slide_partners=self.env['slide.slide.partner'].sudo().search([('slide_id','in',self.slide_id.ids)])
        slide_stats=dict((s.slide_id.id,dict({'attempts_count':0,'attempts_unique':0,'done_count':0}))forsinslide_partners)

        forslide_partnerinslide_partners:
            slide_stats[slide_partner.slide_id.id]['attempts_count']+=slide_partner.quiz_attempts_count
            slide_stats[slide_partner.slide_id.id]['attempts_unique']+=1
            ifslide_partner.completed:
                slide_stats[slide_partner.slide_id.id]['done_count']+=1

        forquestioninself:
            stats=slide_stats.get(question.slide_id.id)
            question.attempts_count=stats.get('attempts_count',0)ifstatselse0
            question.attempts_avg=stats.get('attempts_count',0)/stats.get('attempts_unique',1)ifstatselse0
            question.done_count=stats.get('done_count',0)ifstatselse0


classSlideAnswer(models.Model):
    _name="slide.answer"
    _rec_name="text_value"
    _description="SlideQuestion'sAnswer"
    _order='question_id,sequence'

    sequence=fields.Integer("Sequence")
    question_id=fields.Many2one('slide.question',string="Question",required=True,ondelete='cascade')
    text_value=fields.Char("Answer",required=True,translate=True)
    is_correct=fields.Boolean("Iscorrectanswer")
    comment=fields.Text("Comment",translate=True,help='Thiscommentwillbedisplayedtotheuserifheselectsthisanswer')
