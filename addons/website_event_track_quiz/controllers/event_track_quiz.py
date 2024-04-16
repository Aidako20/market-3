#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimporthttp
fromflectra.addons.website_event_track.controllers.event_trackimportEventTrackController
fromflectra.httpimportrequest


classWebsiteEventTrackQuiz(EventTrackController):

    #QUIZZESINPAGE
    #----------------------------------------------------------

    @http.route('/event_track/quiz/submit',type="json",auth="public",website=True)
    defevent_track_quiz_submit(self,event_id,track_id,answer_ids):
        track=self._fetch_track(track_id)

        event_track_visitor=track._get_event_track_visitors(force_create=True)
        visitor_sudo=event_track_visitor.visitor_id
        ifevent_track_visitor.quiz_completed:
            return{'error':'track_quiz_done'}

        answers_details=self._get_quiz_answers_details(track,answer_ids)
        ifanswers_details.get('error'):
            returnanswers_details

        event_track_visitor.write({
            'quiz_completed':True,
            'quiz_points':answers_details['points'],
        })

        result={
            'answers':{
                answer.question_id.id:{
                    'is_correct':answer.is_correct,
                    'comment':answer.comment
                }foranswerinanswers_details['user_answers']
            },
            'quiz_completed':event_track_visitor.quiz_completed,
            'quiz_points':answers_details['points']
        }
        ifvisitor_sudoandrequest.httprequest.cookies.get('visitor_uuid','')!=visitor_sudo.access_token:
            result['visitor_uuid']=visitor_sudo.access_token
        returnresult

    @http.route('/event_track/quiz/reset',type="json",auth="user",website=True)
    defquiz_reset(self,event_id,track_id):
        track=self._fetch_track(track_id)

        event_track_visitor=track._get_event_track_visitors(force_create=True)
        event_track_visitor.write({
            'quiz_completed':False,
            'quiz_points':0,
        })

    def_get_quiz_answers_details(self,track,answer_ids):
        #TDEFIXME:lostsudo
        questions_count=request.env['event.quiz.question'].sudo().search_count([('quiz_id','=',track.sudo().quiz_id.id)])
        user_answers=request.env['event.quiz.answer'].sudo().search([('id','in',answer_ids)])

        iflen(user_answers.mapped('question_id'))!=questions_count:
            return{'error':'quiz_incomplete'}

        return{
            'user_answers':user_answers,
            'points':sum([
                answer.awarded_points
                foranswerinuser_answers.filtered(lambdaanswer:answer.is_correct)
            ])
        }
