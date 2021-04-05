# Part of flectra. See LICENSE file for full copyright and licensing details.

from flectra import api, fields, models, tools, _
from flectra.exceptions import AccessError
from datetime import datetime
import uuid



TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread.cc',
                'mail.thread',
                'mail.activity.mixin',
                'utm.mixin',
                'portal.mixin',
                'rating.mixin']

    _description = 'Helpdesk Ticket'
    _rec_name = 'issue_name'

    def _default_team_id(self):
        team_id = self.env['helpdesk.team'].search([('visibility_member_ids', 'in', self.env.uid)], limit=1).id
        if not team_id:
            team_id = self.env['helpdesk.team'].search([], limit=1).id
        return team_id

    uid = fields.Many2one('res.users', default=lambda self: self.env.uid)
    issue_name = fields.Char(string='Subject', required=True, index=True, tracking=True)
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', default=_default_team_id, tracking=True)
    help_description = fields.Text()
    active = fields.Boolean(default=True)
    tag_ids = fields.Many2many('helpdesk.tag', string='Tags')
    company_id = fields.Many2one(related='team_id.company_id', string='Company', store=True, readonly=True)
    user_id = fields.Many2one(
        'res.users', string='Assigned to',tracking=True)
    color = fields.Integer(string='Color Index')
    ticket_seq = fields.Char('Sequence', default='New', copy=False)
    priority = fields.Selection([('1', 'Low'), ('2', 'Medium'),
                                 ('3', 'High')], default='1')
    partner_id = fields.Many2one('res.partner', string='Related Partner',
        tracking=True)
    partner_name = fields.Char('Customer Name')
    email = fields.Char(string='Email')
    issue_type_id = fields.Many2one('issue.type', string='Issue Type', store=True)
    start_date = fields.Datetime(
            string='Start Date', default=fields.Datetime.now, tracking=True)
    end_date = fields.Datetime(string='End Date', tracking=True)
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachments',
            string="Main Attachments", help="Attachment that don't come from message.")
    attachments_count = fields.Integer(compute='_compute_attachments',
                                       string='Add Attachments')
    is_accessible = fields.Boolean('Is Accessible',
                                   compute='_compute_is_accessible')
    is_assigned = fields.Boolean('Is Asigned',
                                 compute='_compute_is_accessible')
    stage_id = fields.Many2one('helpdesk.stage', string='Stage', index=True, tracking=True,
        readonly=False, store=True,copy=False, ondelete='restrict')
    
    feedback = fields.Text('Comment', help="Reason of the rating")

    rating_last_value = fields.Float('Rating Last Value', groups='base.group_user', compute='_compute_rating_last_value', compute_sudo=True, store=True)
    is_rating = fields.Boolean("Is Rating")

    def _merge_ticket_attachments(self, tickets):
        self.ensure_one()

        def _get_attachments(ticket_id):
            return self.env['ir.attachment'].search([('res_model', '=', self._name), ('res_id', '=', ticket_id)])

        first_attachments = _get_attachments(self.id)
        # counter of all attachments to move. Used to make sure the name is different for all attachments
        count = 1
        for ticket in tickets:
            attachments = _get_attachments(ticket.id)
            for attachment in attachments:
                values = {'res_id': self.id}
                for attachment_in_first in first_attachments:
                    if attachment.name == attachment_in_first.name:
                        values['name'] = "%s (%s)" % (attachment.name, count)
                count += 1
                attachment.write(values)
        return True

    @api.depends('user_id')
    def _compute_team_id(self):
        """ When changing the user, also set a team_id or restrict team id
        to the ones user_id is member of. """
        for team in self:
            # setting user as void should not trigger a new team computation
            if not team.user_id:
                continue
            user = team.user_id
            if team.team_id and user in team.team_id.member_ids | team.team_id.user_id:
                continue
            team = self.env['helpdesk.team']._get_default_team_id(user_id=user.id)
            team.team_id = team.id


    def _message_get_suggested_recipients(self):
        recipients = super(HelpdeskTicket, self)._message_get_suggested_recipients()
        try:
            for ticket in self:
                if ticket.partner_id:
                    ticket._message_add_suggested_recipient(recipients, partner=ticket.partner_id, reason=_('Customer'))
                elif ticket.email:
                    ticket._message_add_suggested_recipient(recipients, email=ticket.email, reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def _ticket_email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        return [
            x for x in email_list
            if x.split('@')[0] not in self.mapped('team_id.alias_name')
        ]

    def message_update(self, msg, update_vals=None):
        partner_ids = [x.id for x in self.env['mail.thread']._mail_find_partner_from_emails(self._ticket_email_split(msg), records=self) if x]
        if partner_ids:
            self.message_subscribe(partner_ids)
        return super(HelpdeskTicket, self).message_update(msg, update_vals=update_vals)

    def _track_template(self, changes):
        res = super(HelpdeskTicket, self)._track_template(changes)
        ticket = self[0]
        if 'team_id' in changes and ticket.team_id.mail_template_id:
            res['team_id'] = (ticket.team_id.mail_template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            }
        )
        return res

    def _notify_get_reply_to(self, default=None, records=None, company=None, doc_names=None):
        """ Override to set alias of tickets to their team if any. """
        aliases = self.mapped('team_id').sudo()._notify_get_reply_to(default=default, records=None, company=company, doc_names=None)
        res = {ticket.id: aliases.get(ticket.team_id.id) for ticket in self}
        leftover = self.filtered(lambda rec: not rec.team_id)
        if leftover:
            res.update(super(HelpdeskTicket, leftover)._notify_get_reply_to(default=default, records=None, company=company, doc_names=doc_names))
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        values = dict(custom_values or {}, email=msg.get('from'), partner_id=msg.get('author_id'))
        ticket = super(HelpdeskTicket, self.with_context(mail_notify_author=True)).message_new(msg, custom_values=values)
        partner_ids = [x.id for x in self.env['mail.thread']._mail_find_partner_from_emails(self._ticket_email_split(msg), records=ticket) if x]
        customer_ids = [p.id for p in self.env['mail.thread']._mail_find_partner_from_emails(tools.email_split(values['email']), records=ticket) if p]
        partner_ids += customer_ids
        if customer_ids and not values.get('partner_id'):
            ticket.partner_id = customer_ids[0]
        if partner_ids:
            ticket.message_subscribe(partner_ids)
        return ticket

    
    def _message_post_after_hook(self, message, msg_vals):
        
        if self.email and self.partner_id and not self.partner_id.email:
            self.partner_id.email = self.partner_email

        if self.email and not self.partner_id:
            # we consider that posting a message with a specified recipient (not a follower, a specific one)
            # on a document without customer means that it was created through the chatter using
            # suggested recipients. This heuristic allows to avoid ugly hacks in JS.
            new_partner = message.partner_ids.filtered(lambda partner: partner.email == self.email)
            if new_partner:
                self.search([
                    ('partner_id', '=', False),
                    ('email', '=', new_partner.email),
                    ('stage_id.fold', '=', False)]).write({'partner_id': new_partner.id})
        return super(HelpdeskTicket, self)._message_post_after_hook(message, msg_vals)

    @api.model
    def _default_access_token(self):
        return uuid.uuid4().hex

    access_token = fields.Char('Access Token', default=_default_access_token)
    
    @api.model
    def default_get(self, fields):
        result = super(HelpdeskTicket, self).default_get(fields)
        if result.get('team_id') and fields:
            team = self.env['helpdesk.team'].browse(result['team_id'])
            if 'user_id' in fields and 'user_id' not in result:  # if no user given, deduce it from the team
                result['user_id'] = team._determine_user_id()[team.id].id
            if 'stage_id' in fields and 'stage_id' not in result:  # if no stage given, deduce it from the team
                result['stage_id'] = team._determine_stage()[team.id].id
        return result

    @api.onchange('stage_id')
    def onchange_end_date(self):
        if self.stage_id.stage_type == 'done':
            self.end_date = datetime.today()
            mail_id = self.team_id.mail_close_tmpl_id
            if mail_id:
                mail_id.send_mail(res_id=self._origin.id, force_send=True)

    def _creation_subtype(self):
        return self.env.ref('helpdesk_basic.mt_ticket_new')
    
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'user_id' in init_values and self.user_id:
            return self.env.ref('helpdesk_basic.mt_ticket_new')
        elif 'stage_id' in init_values and self.stage_id and \
                self.stage_id.sequence <= 1:
            return self.env.ref('helpdesk_basic.mt_ticket_new')
        elif 'stage_id' in init_values:
            return self.env.ref('helpdesk_basic.mt_ticket_stage')
        return super(HelpdeskTicket, self)._track_subtype(init_values)


    @api.model_create_multi 
    def create(self, values):
        now = fields.Datetime.now()

        # determine user_id and stage_id if not given. Done in batch.
        teams = self.env['helpdesk.team'].browse([vals['team_id'] for vals in values if vals.get('team_id')])
        team_default_map = dict.fromkeys(teams.ids, dict())
        for team in teams:
            team_default_map[team.id] = {
                'stage_id': team._determine_stage()[team.id].id,
                'user_id': team._determine_user_id()[team.id].id

            }

        for vals in values:
            if not vals.get('ticket_seq') or vals['ticket_seq'] == _('New'):
                vals['ticket_seq'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket') or _('New')

            partner_id = vals.get('partner_id', False)
            partner_name = vals.get('email', False)
            partner_email = vals.get('email', False)
            if partner_email and partner_name and not partner_id:
                try:
                    vals['partner_id'] = self.env['res.partner'].find_or_create(
                        self._ticket_email_split({'to': partner_email, 'cc':''})[0]).id
                except UnicodeEncodeError:
                    
                    vals['partner_id'] = self.env['res.partner'].create({
                        'name': partner_name,
                        'email': partner_email,
                    }).id

        partners = self.env['res.partner'].browse([vals['partner_id'] for vals in values if 'partner_id' in vals and vals.get('partner_id') and 'email' not in vals])
        partner_email_map = {partner.id: partner.email for partner in partners}
        partner_name_map = {partner.id: partner.name for partner in partners}

        for vals in values:
            if vals.get('team_id'):
                team_default = team_default_map[vals['team_id']]
                if 'stage_id' not in vals:
                    vals['stage_id'] = team_default['stage_id']
                # Note: this will break the randomly distributed user assignment. Indeed, it will be too difficult to
                # equally assigned user when creating ticket in batch, as it requires to search after the last assigned
                # after every ticket creation, which is not very performant. We decided to not cover this user case.
                if 'user_id' not in vals:
                    vals['user_id'] = team_default['user_id']
        
            # set partner email if in map of not given
            if vals.get('partner_id') in partner_email_map:
                vals['email'] = partner_email_map.get(vals['partner_id'])
            # set partner name if in map of not given
            if vals.get('partner_id') in partner_name_map:
                vals['partner_name'] = partner_name_map.get(vals['partner_id'])

            if vals.get('team_id'):
                team = self.team_id.browse(vals.get('team_id'))
                vals.update(
                    {'stage_id': team.stage_ids and team.stage_ids[0].id or False})
            if not self.stage_id and self.team_id and self.team_id.stage_ids:
                self.stage_id = self.team_id.stage_ids[0]


        # context: no_log, because subtype already handle this
        tickets = super(HelpdeskTicket, self).create(values)

        # make customer follower
        for ticket in tickets:
            if ticket.partner_id:
                ticket.message_subscribe(partner_ids=ticket.partner_id.ids)

            ticket._portal_ensure_token()
        return tickets

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.email = self.partner_id.email

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.team_id:
            self.stage_id = \
                self.team_id.stage_ids and self.team_id.stage_ids.ids[0]

    def _compute_is_accessible(self):
        has_group = self.env.user.has_group('base.group_no_one')
        for ticket in self:
            if self.env.user.partner_id.id == ticket.partner_id.id or \
                    has_group:
                ticket.is_accessible = True
            if self.env.user.id == ticket.user_id.id or has_group:
                ticket.is_assigned = True

    def _compute_attachments(self):
        for ticket in self:
            attachment_ids = self.env['ir.attachment'].search(
                    [('res_model', '=', ticket._name),
                     ('res_id', '=', ticket.id)])
            ticket.attachments_count = len(attachment_ids.ids)
            ticket.attachment_ids = attachment_ids

    def _auto_rating_request_mail(self):
        ticket_ids = self.env['helpdesk.ticket'].search([])
        for ticket in ticket_ids.filtered(
                lambda r: r.stage_id.stage_type == 'done' and r.team_id.is_rating == True):
            template = self.env.ref('helpdesk_basic.ticket_rating_mail_template')
            if ticket.is_rating != True:
                template.send_mail(res_id=ticket.id, force_send=True)
            ticket.is_rating = True
