#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportfields,tests


@tests.tagged('post_install','-at_install')
classTestUi(tests.HttpCase):

    deftest_01_tickets_questions(self):
        """Willexecutethetourthatfillsuptwoticketswithafewquestionsanswers
        andthenassertthattheanswersarecorrectlysavedforeachattendee."""

        self.design_fair_event=self.env['event.event'].create({
            'name':'DesignFairNewYork',
            'date_begin':fields.Datetime.now()-relativedelta(days=15),
            'date_end':fields.Datetime.now()+relativedelta(days=15),
            'event_ticket_ids':[(0,0,{
                'name':'Free',
                'start_sale_date':fields.Datetime.now()-relativedelta(days=15)
            }),(0,0,{
                'name':'Other',
                'start_sale_date':fields.Datetime.now()-relativedelta(days=15)
            })],
            'website_published':True,
            'question_ids':[(0,0,{
                'title':'MealType',
                'question_type':'simple_choice',
                'answer_ids':[
                    (0,0,{'name':'Mixed'}),
                    (0,0,{'name':'Vegetarian'}),
                    (0,0,{'name':'Pastafarian'})
                ]
            }),(0,0,{
                'title':'Allergies',
                'question_type':'text_box'
            }),(0,0,{
                'title':'Howdidyoulearnaboutthisevent?',
                'question_type':'simple_choice',
                'once_per_order':True,
                'answer_ids':[
                    (0,0,{'name':'Ourwebsite'}),
                    (0,0,{'name':'Commercials'}),
                    (0,0,{'name':'Afriend'})
                ]
            })]
        })

        self.start_tour("/",'test_tickets_questions',login="portal")

        registrations=self.env['event.registration'].search([
            ('email','in',['attendee-a@gmail.com','attendee-b@gmail.com'])
        ])
        self.assertEqual(len(registrations),2)
        first_registration=registrations.filtered(lambdareg:reg.email=='attendee-a@gmail.com')
        second_registration=registrations.filtered(lambdareg:reg.email=='attendee-b@gmail.com')
        self.assertEqual(first_registration.name,'AttendeeA')
        self.assertEqual(first_registration.phone,'+32499123456')
        self.assertEqual(second_registration.name,'AttendeeB')

        event_questions=registrations.mapped('event_id.question_ids')
        self.assertEqual(len(event_questions),3)

        first_registration_answers=first_registration.registration_answer_ids
        self.assertEqual(len(first_registration_answers),3)

        self.assertEqual(first_registration_answers.filtered(
            lambdaanswer:answer.question_id.title=='MealType'
        ).value_answer_id.name,'Vegetarian')

        self.assertEqual(first_registration_answers.filtered(
            lambdaanswer:answer.question_id.title=='Allergies'
        ).value_text_box,'FishandNuts')

        self.assertEqual(first_registration_answers.filtered(
            lambdaanswer:answer.question_id.title=='Howdidyoulearnaboutthisevent?'
        ).value_answer_id.name,'Afriend')

        second_registration_answers=second_registration.registration_answer_ids
        self.assertEqual(len(second_registration_answers),2)

        self.assertEqual(second_registration_answers.filtered(
            lambdaanswer:answer.question_id.title=='MealType'
        ).value_answer_id.name,'Pastafarian')

        self.assertEqual(first_registration_answers.filtered(
            lambdaanswer:answer.question_id.title=='Howdidyoulearnaboutthisevent?'
        ).value_answer_id.name,'Afriend')
