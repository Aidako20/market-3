#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models
fromflectra.osvimportexpression


classEventTrack(models.Model):
    _inherit=['event.track']

    quiz_id=fields.Many2one('event.quiz',string="Quiz",groups="event.group_event_user")
    quiz_questions_count=fields.Integer(string="#QuizQuestions",compute='_compute_quiz_questions_count',groups="event.group_event_user")
    is_quiz_completed=fields.Boolean('IsQuizDone',compute='_compute_quiz_data')
    quiz_points=fields.Integer('QuizPoints',compute='_compute_quiz_data')

    @api.depends('quiz_id.question_ids')
    def_compute_quiz_questions_count(self):
        fortrackinself:
            track.quiz_questions_count=len(track.quiz_id.question_ids)

    @api.depends('quiz_id','event_track_visitor_ids.visitor_id',
                 'event_track_visitor_ids.partner_id','event_track_visitor_ids.quiz_completed',
                 'event_track_visitor_ids.quiz_points')
    @api.depends_context('uid')
    def_compute_quiz_data(self):
        tracks_quiz=self.filtered(lambdatrack:track.quiz_id)
        (self-tracks_quiz).is_quiz_completed=False
        (self-tracks_quiz).quiz_points=0
        iftracks_quiz:
            current_visitor=self.env['website.visitor']._get_visitor_from_request(force_create=False)
            ifself.env.user._is_public()andnotcurrent_visitor:
                fortrackintracks_quiz:
                    track.is_quiz_completed=False
                    track.quiz_points=0
            else:
                ifself.env.user._is_public():
                    domain=[('visitor_id','=',current_visitor.id)]
                elifcurrent_visitor:
                    domain=[
                        '|',
                        ('partner_id','=',self.env.user.partner_id.id),
                        ('visitor_id','=',current_visitor.id)
                    ]
                else:
                    domain=[('partner_id','=',self.env.user.partner_id.id)]

                event_track_visitors=self.env['event.track.visitor'].sudo().search_read(
                    expression.AND([
                        domain,
                        [('track_id','in',tracks_quiz.ids)]
                    ]),fields=['track_id','quiz_completed','quiz_points']
                )

                quiz_visitor_map={
                    track_visitor['track_id'][0]:{
                        'quiz_completed':track_visitor['quiz_completed'],
                        'quiz_points':track_visitor['quiz_points']
                    }fortrack_visitorinevent_track_visitors
                }
                fortrackintracks_quiz:
                    ifquiz_visitor_map.get(track.id):
                        track.is_quiz_completed=quiz_visitor_map[track.id]['quiz_completed']
                        track.quiz_points=quiz_visitor_map[track.id]['quiz_points']
                    else:
                        track.is_quiz_completed=False
                        track.quiz_points=0
