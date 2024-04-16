#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.httpimportrequest

fromflectra.addons.website_event.controllers.mainimportWebsiteEventController


classWebsiteEvent(WebsiteEventController):

    def_process_attendees_form(self,event,form_details):
        """Processdatapostedfromtheattendeedetailsform.
        Extractsquestionanswers:
        -Forbothquestionsasked'once_per_order'andquestionsaskedtoeveryattendee
        -Forquestionsoftype'simple_choice',extractingthesuggestedanswerid
        -Forquestionsoftype'text_box',extractingthetextansweroftheattendee."""
        registrations=super(WebsiteEvent,self)._process_attendees_form(event,form_details)

        forregistrationinregistrations:
            registration['registration_answer_ids']=[]

        general_answer_ids=[]
        forkey,valueinform_details.items():
            if'question_answer'inkeyandvalue:
                dummy,registration_index,question_id=key.split('-')
                question_sudo=request.env['event.question'].browse(int(question_id))
                answer_values=None
                ifquestion_sudo.question_type=='simple_choice':
                    answer_values={
                        'question_id':int(question_id),
                        'value_answer_id':int(value)
                    }
                elifquestion_sudo.question_type=='text_box':
                    answer_values={
                        'question_id':int(question_id),
                        'value_text_box':value
                    }

                ifanswer_valuesandnotint(registration_index):
                    general_answer_ids.append((0,0,answer_values))
                elifanswer_values:
                    registrations[int(registration_index)-1]['registration_answer_ids'].append((0,0,answer_values))

        forregistrationinregistrations:
            registration['registration_answer_ids'].extend(general_answer_ids)

        returnregistrations
